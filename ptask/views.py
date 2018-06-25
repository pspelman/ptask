# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from time import sleep, time

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader

from apt_logic import get_results_indices, process_raw_data
from forms import QuantityResponseForm
from methods import *


# Handle 404 Errors
# @param request WSGIRequest list with all HTTP Request
def error404(request):
    # Generate Content for this view
    response_page = loader.get_template('404.html')
    context = {
        'message': 'Not available',
    }
    # Return Template for this view + Data
    return HttpResponse(content=response_page.render(context), content_type='text/html; charset=utf-8', status=404)


# TODO: add ability to call price_levels file OR add ability for price levels to be specified via the researcher page

# price_levels = [0, 5, 10, 25, 50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500]
PRICES = [0, 25, 50, 75, 100, 200, 300, 400, 500, 1000]


def welcome_vew(request):
    return render(request, 'welcome.html', {"theTime": time()})


def instructions_view(request):
    if 'in_progress' not in request.session:
        initiate_task_session(request.session, PRICES)
        start_timestamp = time()
        request.session['start_timestamp'] = start_timestamp
    # reqeust.session['in_progress'] WILL be false, so this will display the directions page AS INTENDED

    if request.session['in_progress']:
        # if task is already in progress then return to next item
        response_data = {}
        response_data['result'] = 'error'
        response_data['message'] = 'Some error message'
        context = {
            "error_message": "try the reset button"
        }
        return render(request, 'error_page.html', context)

    context = {
        'task': get_task_instructions(),
    }
    request.session.modified = True
    return render(request, 'instructions.html', context)


def task_view(request):
    next_unanswered_question = get_next_unanswered_question(request.session)
    if next_unanswered_question == "DONE":
        # print "Task is done...redirect to completion"
        return redirect('/completion')

    # if it's not done, show the next question
    context = get_task_question_context(request)
    context['form'] = QuantityResponseForm()

    return render(request, 'task_question_form.html', context)


""" this will return the variables to send to the template
    based on the next question that needs to be answered """


def get_task_question_context(request):
    next_unanswered_question = get_next_unanswered_question(request.session)

    # get the price associated with the current item (string price)
    quantity_response_form = QuantityResponseForm(request.POST or None)

    current_price_text = request.session['price_strings'][next_unanswered_question]

    context = {
        'individual_price_level': current_price_text,
        'price_as_dollar': '$100',
        'quantity_response_form': quantity_response_form,
        'task': get_task_instructions(current_price_text),
    }
    return context


def begin_task(request):
    # reached begin task...test to see if task was already started
    request.session['in_progress'] = True
    request.session.modified = True
    return redirect('/task_view')


def process_form_data(request):
    if request.method == 'POST':
        quantity_response_form = QuantityResponseForm(request.POST or None)
        # ###123### print "quant form set"
        if quantity_response_form.is_valid():
            # print "quantity form was valid"
            response_quant = quantity_response_form.cleaned_data.get('quantity')
            next_unanswered_question = get_next_unanswered_question(request.session)
            # response = 'placeholder for values from item {} | user submitted {}' \
            #            ' need to save to session'.format(next_unanswered_question, response_quant)
            request.session['response_key'][next_unanswered_question]['0'] = response_quant
            request.session.modified = True
            return redirect('/task_view')

        else:
            context = get_task_question_context(request)
            # return render(request, 'task_question_form.html', {'quantity_response_form': quantity_response_form})
            return render(request, 'task_question_form.html', context)
    else:
        return redirect('/task_view')


# TODO: EMAIL the results
# TODO: Once the task is in production, DISABLE the display of the user's results
# TODO: send dirty data to the database
# TODO: determine the number of reversals in participant data
# TODO: auto-clean one or two reversals
# TODO: send clean data to the database
def task_complete_view(request):
    if 'end_timestamp' not in request.session:
        end_timestamp = time()
        request.session['end_timestamp'] = end_timestamp

    raw_task_results = process_raw_data(request.session)
    results_indices = get_results_indices(raw_task_results)
    request.session['raw_data'] = raw_task_results['raw_tuples']
    request.session['final_indices'] = results_indices
    request.session.modified = True

    context = {
        'start_timestamp': request.session['start_timestamp'],
        'end_timestamp': request.session['end_timestamp'],
        'researcher_email': request.session['researcher_email'],
        'participant_id': request.session['participant_id'],
        'data': raw_task_results['raw_tuples'],
        'indices': results_indices,
    }
    return render(request, 'task_complete.html', context)


def logout_view(request):
    ###123### print "reached logout"
    request.session.flush()
    clear_session(request)
    request.session.modified = True
    return redirect('/')


def clear_session(request):
    request.session.flush()
    request.session['initiated'] = False
    return redirect('/task')

    # to delete keys but keep the user logged in
    # for key in request.session.keys():
    #     del request.session[key]


def manual_input(request):
    # print "reached manual input"
    researcher_email = request.GET['researcher_email']
    # print "researcher email: ", researcher_email
    participant_id = request.GET['participant_id']
    if not researcher_email or researcher_email == "":
        request.session['researcher_email'] = 'research@philspelman.com'
        researcher_email = 'research@philspelman.com'
    if not participant_id or participant_id == "":
        participant_id = 'none'
    return begin_task_with_url_params(request, researcher_email, participant_id)


def begin_task_with_url_params(request, researcher_email='research@philspelman.com', participant_id='none'):
    request.session['participant_id'] = participant_id
    request.session['researcher_email'] = researcher_email
    # print "researcher email: {}".format(researcher_email)
    request.session.modified = True
    return redirect("/instructions")


# in_progress redirects here
def render_question_page_view(request):
    # determine the next question
    next_unanswered_question = get_next_unanswered_question(request.session)
    # prepare the appropriate context variables for the item
    if next_unanswered_question == "DONE":
        return HttpResponse("Placeholder for ALL DONE")
    else:
        return HttpResponse('this is a response')
