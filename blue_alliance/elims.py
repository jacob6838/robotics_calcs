import requests
import json

API_KEY = 'hkc8UBiLuqDUU1mGGtvlzNMUoZ3Xsr13QG872wRnXajGlP6lgm12FMBIiYIAGdVc'
ENDPOINT = 'https://www.thebluealliance.com/api/v3/{endpoint}'

EVENTS_ENDPOINT = 'events/{year}'
EVENT_ENDPOINT = 'event/{key}'
EVENT_ENDPOINT_MATCHES = 'event/{key}/matches'

year = '2019'

# # ALL EVENTS
# resp = requests.get(ENDPOINT.format(endpoint=EVENTS_ENDPOINT.format(
#     year=year)), headers={'X-TBA-Auth-Key': API_KEY})
# body = resp.content.decode('utf-8')
# open(f'{year}/all_events.json', 'w').write(body)


# event_key = '2019code'

# Individual event


def get_event(event_key):
    resp = requests.get(ENDPOINT.format(endpoint=EVENT_ENDPOINT_MATCHES.format(
        key=event_key)), headers={'X-TBA-Auth-Key': API_KEY})
    body = resp.content.decode('utf-8')
    open(f'{year}/events/{event_key}_matches.json', 'w').write(body)
    return json.loads(body)


# Championship Division
# Regional
# District
# District Championship

def analyze_event(matches):
    keyed_matches = {}
    for i in matches:
        keyed_matches[i['key']] = i

    all_series = []
    same_result = []
    different_result = []
    if not matches:
        return 0, 0, 0
    for i in get_match_keys(matches[0]['event_key']):
        try:
            series_results = []
            # print(i)
            for j in i:
                if j in keyed_matches:
                    series_results.append(keyed_matches[j]['winning_alliance'])
            if series_results[0] == series_results[1] or series_results[0] == series_results[2]:
                same_result.append(series_results)
                all_series.append(series_results)
            elif "" in series_results:
                print("TIE! Ignoring")
                all_series = all_series[:-1]
            else:
                different_result.append(series_results)
                all_series.append(series_results)
        except Exception as e:
            print(f"ERROR: {e}, event: {matches[0]['event_key']}, match: {i}")
            pass
    return len(all_series), len(same_result), len(different_result)


# All events
all_event_summaries = json.loads(
    open(f'{year}/all_events.json').read())

keyed_event_summaries = {}
for i in all_event_summaries:
    keyed_event_summaries[i['key']] = i

all_events = []
for i in all_event_summaries:
    key = i['key']
    all_events.append(json.loads(
        open(f'{year}/events/{key}_matches.json').read()))
    # all_events.append(get_event(key))


match_key = "{event_key}_{comp_level}{set_number}m{match_number}"


def get_match_keys(event_key):
    return [
        [
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=1, match_number=1),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=1, match_number=2),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=1, match_number=3),
        ],
        [
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=2, match_number=1),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=2, match_number=2),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=2, match_number=3),
        ],
        [
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=3, match_number=1),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=3, match_number=2),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=3, match_number=3),
        ],
        [
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=4, match_number=1),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=4, match_number=2),
            match_key.format(event_key=event_key, comp_level='qf',
                             set_number=4, match_number=3),
        ],
        [
            match_key.format(event_key=event_key, comp_level='sf',
                             set_number=1, match_number=1),
            match_key.format(event_key=event_key, comp_level='sf',
                             set_number=1, match_number=2),
            match_key.format(event_key=event_key, comp_level='sf',
                             set_number=1, match_number=3),
        ],
        [
            match_key.format(event_key=event_key, comp_level='sf',
                             set_number=2, match_number=1),
            match_key.format(event_key=event_key, comp_level='sf',
                             set_number=2, match_number=2),
            match_key.format(event_key=event_key, comp_level='sf',
                             set_number=2, match_number=3),
        ],
        [
            match_key.format(event_key=event_key, comp_level='f',
                             set_number=1, match_number=1),
            match_key.format(event_key=event_key, comp_level='f',
                             set_number=1, match_number=2),
            match_key.format(event_key=event_key, comp_level='f',
                             set_number=1, match_number=3),
        ],
    ]


event_types = ['Championship Division', 'Regional',
               'District', 'District Championship', 'Offseason', 'Other', 'District Championship Division']

all_series_count = {_type: 0 for _type in event_types}
same_results_count = {_type: 0 for _type in event_types}
different_results_count = {_type: 0 for _type in event_types}
for event in all_events:
    if len(event) == 0:
        continue
    event_type_string = keyed_event_summaries.get(
        event[0]['event_key'], {}).get('event_type_string', "Other")
    if event_type_string not in event_types:
        event_type_string = "Other"
    all, same, different = analyze_event(event)

    all_series_count[event_type_string] += all
    same_results_count[event_type_string] += same
    different_results_count[event_type_string] += different


for i in event_types:
    print('------')
    print(i)
    if not all_series_count[i]:
        print("No results")
        continue
    print(all_series_count[i], same_results_count[i],
          different_results_count[i])
    print(different_results_count[i]/all_series_count[i])

print('------')
print('ALL (no Other)')
del all_series_count['Other']
del same_results_count['Other']
del different_results_count['Other']
all_series_count_all = sum(all_series_count.values())
same_results_count_all = sum(same_results_count.values())
different_results_count_all = sum(different_results_count.values())

print(all_series_count_all, same_results_count_all, different_results_count_all)
print(different_results_count_all/all_series_count_all)
