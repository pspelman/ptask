import StringIO
import csv

from django.contrib import messages
from django.core import mail
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect

from methods import make_JSON

def download_results(request):
    return make_csv(request)


def get_notification_email():
    pass


def send_results(request):
    participant_id = request.session['participant_id']
    researcher_email = request.session['researcher_email']

    if not request.session['email_sent']:
        if participant_id == "none":
            participant_id = "DEMO PARTICIPANT"

        results_csv = make_csv(request)

        message_subject = "Purchase task | Participant - {}".format(participant_id)
        message_body = "Results are attached for participant: {}".format(participant_id)
        # THE FROM FIELD SHOULD STAY THE SAME - IT IS FROM MY RESEARCH PLATFORM
        message_from_email_field = "research@philspelman.com"
        to_email = researcher_email
        results_file_name = "{}_results.csv".format(participant_id)

        results_email = EmailMessage(message_subject, message_body, message_from_email_field, [to_email])
        results_email.attach(results_file_name, results_csv.getvalue(), 'text/csv')

        # TODO: re-enable email when ready
        # results_email.send(False)

        request.session['email_sent'] = True
        request.session.modified = True

        return redirect('/research/completion')

        # return JsonResponse({"message": "done"})

    elif request.session['email_sent']:
        # messages.success(request, 'Results were already sent to {}.'.format(researcher_email))
        # print "someone already clicked send. DO NOTHING"
        return redirect('/research/completion')

    else:
        messages.success(request, 'The task is complete. Press RESET to begin a new task')
        return redirect('/research/completion')
        # return JsonResponse({"message": "try again"})




def make_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    if request.session['participant_id'] == 'none':
        file_ending = request.session['start_timestamp']
    else:
        file_ending = "participant_id-{}".format(request.session['participant_id'])


    raw_data = request.session['raw_data']
    final_indices = request.session['final_indices']
    # print "final indices: ", final_indices

    results = HttpResponse(content_type='text/csv')
    results['Content-Disposition'] = 'attachment; filename="apt_results_{}.csv"'.format(file_ending)


    writer = csv.writer(results)
    writer.writerow(['participant_id',  "=\"" + request.session['participant_id'] + "\""])
    writer.writerow(['start_timestamp', request.session['start_timestamp']])
    writer.writerow(['end_timestamp', request.session['end_timestamp']])
    writer.writerow(['researcher_email', request.session['researcher_email']])
    writer.writerow([''])

    writer.writerow(['DEMAND INDICES'])
    writer.writerow(['Intensity', final_indices['intensity']])
    writer.writerow(['Omax', final_indices['omax']])
    writer.writerow(['Pmax', final_indices['pmax'],'','Note:','Current Pmax value is the FIRST price associated with Omax (i.e., in the event of multiple Omax values, Pmax is the price associated with the first occurence of Omax)'])
    writer.writerow(['Breakpoint', final_indices['breakpoint']])
    writer.writerow([])
    if len(final_indices['data_warnings']):
        writer.writerow(['WARNINGS:'])
        for warning in final_indices['data_warnings']:
            writer.writerow([warning[0], warning[1]])
    else:
        writer.writerow(['WARNINGS:','none'])

    # writer.writerow(['','Note:','Current Pmax value is the FIRST price associated with Omax (i.e., in the event of multiple Omax values, Pmax is the price associated with the first occurence of Omax)'])
    writer.writerow([''])
    writer.writerow([''])

    writer.writerow(['RAW DATA'])
    writer.writerow(['item', 'price', 'quantity', '$ spent'])
    for trial in raw_data:
        writer.writerow([trial[0], trial[1], trial[2], trial[1]*trial[2]])
    writer.writerow([])

    return results