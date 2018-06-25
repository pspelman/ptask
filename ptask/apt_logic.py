from django.http import HttpResponse


def process_raw_data(session):
    # ###123### print "reached process_raw_data"
    response_key = session['response_key']
    ###123### print "response_key: ", response_key
    raw_data_dict = []
    raw_task_tuples = []
    raw_price_and_consumption_only = []

    price_list = session['price_numbers']
    ###123### print "price_list: ", price_list

    for i in range(len(response_key)):
        raw_price_and_consumption_only.append(
            (price_list[i], response_key[i]['0'])
        )

        raw_task_tuples.append(
            (i, price_list[i], response_key[i]['0'])
        )

        raw_data_dict.append(
            {
                price_list[i]: response_key[i]['0']
            }
        )

    ###123### print "raw_task_tuples processed... ->", raw_task_tuples
    ###123### print "raw_data_dict processed... -> ", raw_data_dict
    raw_task_results = {
        'raw_tuples': raw_task_tuples,
        'raw_data_dict': raw_data_dict,
        'raw_price_and_consumption_only': raw_price_and_consumption_only,
    }

    return raw_task_results


def get_results_indices(raw_task_results):
    raw_price_and_consumption_only = raw_task_results['raw_price_and_consumption_only']
    ###123### print "raw price and consumption: ", raw_price_and_consumption_only

    demand_indices = get_demand_indices(raw_price_and_consumption_only)

    # Check for meaningful breakpoint, intensity > 0 & breakpoint != 0
    if demand_indices['intensity'] > 0:
        if demand_indices['breakpoint'] == 0:
            # there was no breakpoint, they consumed across all prices, make breakpoint NONE
            breakpoint = "None. Participant reported consumption at every price"
        # elif demand_indices['breakpoint'] == "ERROR":
        #     breakpoint = "ERROR - Inconsistencies in participant data"
        else:
            # breakpoint is meaningful, send it back as formatted price
            breakpoint = "${:.2f}".format((float(demand_indices['breakpoint'])))

        omax = "${:.2f}".format((float(demand_indices['omax'])))
        pmax_results = demand_indices['pmax']

        pmax = "${:.2f}".format((float(pmax_results[len(pmax_results) - 1][0])))
    else:
        intensity = 0
        omax = "None"
        pmax = "None"
        breakpoint = "None"

    results_indices = {
        'intensity': demand_indices['intensity'],
        'omax': omax,
        'pmax': pmax,
        'breakpoint': breakpoint,
        'data_warnings': demand_indices['data_warnings'],
    }
    return results_indices


def get_demand_indices(consumption_data):
    data_warnings = []
    # consumption data will be JUST the price and consumption, not the trial (price, quant)
    intensity = consumption_data[0][1]
    omax = 0
    pmax = []
    breakpoint = 0
    breakpoint_isset = False
    breakpoint_error = False

    for trial in consumption_data:
        # NOTE: change the logic below to >= for the possibility of multiple pmax values
        # quant * price
        if trial[0] * trial[1] > omax:
            omax = trial[0] * trial[1]
            pmax.append([trial[0], omax])


    # TODO: Data consistency tests - REVERSALS


    # Data consistency tests - BREAKPOINT
        # CASE 1 - consumption @ price level 0 is NONE and then there IS consumption ANYWHERE ELSE (this is also a reversal)
    if consumption_data[0][1] == 0:
        for i in range(1, len(consumption_data)):
            if consumption_data[i][1] > 0:
                print "line 103 making breakpoint error"
                breakpoint_error = True
                break


        # CASE 2 - consumption drops to zero and THEN increases (this is also considered a reversal)
    if consumption_data[0][1] > 0:
        # if something was consumed at price[i], but NOTHING at the next price, the next price is the breakpoint
        for i in range(1, len(consumption_data)):
            if consumption_data[i][1] > 0 and breakpoint_isset:
                print "line 112 making breakpoint error"
                breakpoint_error = True
                break
            elif consumption_data[i][1] == 0:
                if consumption_data[i - 1][1] > 0 and not breakpoint_isset:
                    # if no breakpoint yet, make one
                    breakpoint_isset = True
                    breakpoint = consumption_data[i][0]

            # COULD DECIDE TO BREAK OUT HERE AND SKIP REMAINING DATA, assuming detecting inconsistency doesn't matter

    if breakpoint_error:
        data_warnings.append(['Breakpoint', 'Inconsistencies in participant data'])

    return {'intensity': intensity, 'omax': omax, 'pmax': pmax, 'breakpoint': breakpoint,
            'data_warnings': data_warnings}
