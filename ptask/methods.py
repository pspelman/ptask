import StringIO
import csv
import re

from django import template
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import RegexValidator
from django.http import JsonResponse
from django.utils.translation import gettext as _

register = template.Library()



# import EmailMessage class - https://docs.djangoproject.com/en/1.9/topics/email/#django.core.mail.EmailMessage
# from django.core.mail import EmailMessage
def sendResults(data):

    email = EmailMessage('... Subject ...', '... Body ...', 'from-email',
                ['to-email-1', 'to-email-2'], ['bcc-email-1', 'bcc-email-2'])

    # now let's create a csv file dynamically
    attachment_csv_file = StringIO.StringIO()

    writer = csv.writer(attachment_csv_file)

    labels = ['name', 'city', 'email']
    writer.writerow(labels)

    rows = [['Nitin', 'Bengaluru', 'nitinbhojwani1993@gmail.com'], ['X', 'Y', 'Z']]

    for row in rows:
        writer.writerow(row)

    email.attach('attachment_file_name.csv', attachment_csv_file.getvalue(), 'text/csv')
    email.send(fail_silently=False)
#
#




@register.filter(name='replace_linebr')
def replace_linebr(value):
    """
    Replaces all values of line break from the given string with a line space.
    example call in template:    {{ education_detail.education_details_institution_name|replace_linebr }}
    """
    return value.replace("<br />", ' ')


'''
    EMAIL validator for incoming requests
'''


class EmailValidator(RegexValidator):
    def __call__(self, value):
        try:
            super(EmailValidator, self).__call__(value)
        except ValidationError, e:
            # Trivial case failed. Try for possible IDN domain-part
            if value and u'@' in value:
                parts = value.split(u'@')
                domain_part = parts[-1]
                try:
                    parts[-1] = parts[-1].encode('idna')
                except UnicodeError:
                    raise e
                super(EmailValidator, self).__call__(u'@'.join(parts))
            else:
                raise

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
validate_email = EmailValidator(email_re, _(u'Enter a valid e-mail address.'), 'invalid')


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False






'''This method will return an array of price levels as strings
    formatted to look like dollars with two decimals (e.g., $2.00 '''


def get_price_as_dollar_string(price_levels):
    price_as_dollar = []
    for level in price_levels:
        price_as_dollar.append("${:.2f}".format((float(level) / 100)))
    return price_as_dollar


# return an array of prices formatted as strings


def get_price_as_float(price_levels):
    price_level = []
    for i in range(len(price_levels)):
        price_level.append(float(price_levels[i]) / 100)
    # for level in price_levels:
    #     price_level.append(float(level) / 100)
    return price_level


# return an array of prices formatted as strings


def get_price_dictionary(PRICES):
    price_strings = get_price_as_dollar_string(PRICES)
    prices_as_float = get_price_as_float(PRICES)
    price_dictionary = {}
    for i in range(len(price_strings)):
        price_dictionary["{}".format(i)] = PRICES[i]
    return price_dictionary


def get_trial_numbers(num_trials):
    trials = []
    for i in range(len(num_trials)):
        trials.append(i)
        # ###123### print "trials:", trials
    return trials


def initiate_task_session(session, PRICES):
    ###123### print "reached initiate_task_session... checking if new session is needed"
    # if the session is empty, start a new task
    if 'initiated' not in session:
        session.flush()
        ###123### print "initiating NEW session"
        initiate_new_session_vars(session, PRICES)
        session['initiated'] = True
        session.modified = True
        return

    elif session['initiated'] == False:
        ###123### print "initiated was false, starting new session!"
        session['initiated'] = True
        initiate_new_session_vars(session, PRICES)
        session.modified = True
        return

    ###123### print "unexpected event: something in initiate_task_session went wrong"
    ###123### print "session task status:", session['task_status']


def create_task_response_key(num_trials):
    ###123### print "creating response key based on number of items to be presented"
    response_key = []
    for i in range(len(num_trials)):
        response_key.append(
            {0: '',
             })
    return response_key


def get_next_unanswered_question(session):
    # todo: does current 'next_unanswered_question' have an answer?
    # check the response key against the current next_unanswered question
    # if there is NOW a response, then that question is answered, assign the next_unanswered question to the next item
    # ###123### print "next unanswered q: ", session['next_unanswered_question']
    task_length = len(session['response_key'])
    answer_location = '0'
    ###123### print "current session[response_key][[session[next_unanswered_question]", session['response_key'][session['next_unanswered_question']]
    # if there IS NO answer
    if session['response_key'][session['next_unanswered_question']][answer_location] == '':
        ###123### print "question {} has not yet been answered! No changes made".format(session['next_unanswered_question'])
        return session['next_unanswered_question']

    # if there IS an answer
    if session['response_key'][session['next_unanswered_question']][answer_location] != '':
        if session['next_unanswered_question'] == task_length - 1:
            ###123### print "the last question has been answered. Task is complete"
            session['next_unanswered_question'] = "DONE"
            return "DONE"
        else:
            ###123### print "question answered, getting next question"
            session['next_unanswered_question'] = int(session['next_unanswered_question'] + 1)

    return "PLACEHOLDER FOR NEXT UNANSWERED QUESTION...YOU SHOULDN'T SEE THIS"


def initiate_new_session_vars(session, PRICES):
    session['initiated'] = True
    session['user_id'] = "na"
    session['next_unanswered_question'] = 0
    session['current_question_number'] = []

    session['in_progress'] = False

    session['response_set'] = {
        'trial_number': [],
        'item_price': [],
        'quantity': [],
    }

    # TODO: put the reversal in a function, it should probably be defaulted to a lowest_num-to-highest presentation
    price_numbers = get_price_as_float(PRICES)
    price_strings = get_price_as_dollar_string(PRICES)
    trial_numbers = get_trial_numbers(PRICES)
    response_key = create_task_response_key(PRICES)

    # session['response_key'] = [{0:'answer'},{1:'answer'}] #need to pre-populate the keys

    session['response_key'] = []

    # USE REVERSE IF POPPING off the end
    # price_numbers.reverse()
    # price_strings.reverse()
    # trial_numbers.reverse()

    session['response_key'] = response_key
    session['price_numbers'] = price_numbers
    session['price_strings'] = price_strings
    session['trial_numbers'] = trial_numbers

    ###123### print 'price_numbers:', price_numbers
    ###123### print 'price_strings:', price_strings
    # ###123### print 'trial_numbers:', trial_numbers
    # instructions flag
    next_trial = []
    next_trial.append('instructions')
    next_trial.extend(trial_numbers)
    next_trial.append('DONE')
    # next_trial.reverse()

    ###123### print "next_trial array is constructed:", next_trial

    session['next_trial'] = next_trial

    session['task_status'] = {
        'price_numbers': price_numbers,
        'price_strings': price_strings,
        'trial_numbers': trial_numbers,
        'next_trial': next_trial,
    }

    session.modified = True
    ###123### print "session initiated...returning to task_form"
    return


def get_task_instructions(price_string="$"):
    instruction_head = "Instructions"

    acute_instructions = ("Imagine that you could drink alcohol RIGHT NOW.\n\n"
                          "Your task is to enter the number of alcoholic drinks you would consume at various prices\n")

    state_based_instructions = "Imagine you're going to go to a bar with friends this Friday night. ... get the rest of those instructions"

    # put together the instructions
    scenario_instructions = acute_instructions
    available_amounts_header = "The available drinks are:"
    drink_amounts_list = ['standard size domestic beer (12 oz.)',
                          'wine (5 oz.)',
                          'shots of hard liquor (1.5 oz.)',
                          'mixed drinks containing one shot of liquor',
                          ]
    assumption_instructions = "Please assume that you would consume every drink you request. \nYou cannot stockpile drinks for a later date or bring drinks home with you."
    how_to_respond_instructions = "Please use the number pad to enter numbers"
    individual_price_level_prompt = "How many drinks would you have right now if they cost"

    task_dictionary = {
        'task_title': instruction_head,
        'instruction_head': instruction_head,
        'scenario_instructions': scenario_instructions,
        'drink_amounts_list': drink_amounts_list,
        'available_amounts_header': available_amounts_header,
        'post_instructions': assumption_instructions,
        'how_to_respond_instructions': how_to_respond_instructions,
        'individual_price_level_prompt': individual_price_level_prompt,
        'individual_price_level': '{} / drink'.format(price_string),

    }

    return task_dictionary


def make_JSON(data):
    return JsonResponse(data)


