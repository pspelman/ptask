import StringIO
import csv

from django.http import JsonResponse, HttpResponse

from methods import make_JSON


def send_results(request):
    participant_id = request.session['participant_id']
    researcher_email = request.session['researcher_email']

    # send_mail(
    #     'Test results',
    #     'Here is the message.',
    #     FROM: 'purcahseTask@philspelman.com',
    #     TO: ['phil.spelman@gmail.com'],
    #     fail_silently=False,
    # )
    task_result_data = {"participant_id": participant_id, "researcher_email": researcher_email,
                        "raw_data": request.session['raw_data'], "final_indices": request.session['final_indices']}

    ###123### print "getting JSON"
    result = StringIO.StringIO(make_JSON(task_result_data))

    # todo: Make CSV file
    ###123### print result.read()
    # result.read()
    return JsonResponse({"message": "trying to send results via email", "raw_data": request.session['raw_data'],
                         "final_indices": request.session['final_indices']})





def make_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    if request.session['participant_id'] == 'none':
        file_ending = request.session['start_timestamp']
    else:
        file_ending = "participant_id-{}".format(request.session['participant_id'])


    raw_data = request.session['raw_data']
    final_indices = request.session['final_indices']
    # print "final indices: ", final_indices

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="apt_results_{}.csv"'.format(file_ending)


    writer = csv.writer(response)
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

    return response