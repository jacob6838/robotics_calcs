import json


year = '2019'
event_key = '2019code'

matches = json.loads(open(f'{year}/{event_key}_matches.json').read())

qf_key = "qf"
match_key = "{event_key}_{comp_level}{set_number}m{match_number}"

matches_keys = [
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

keyed_matches = {}
for i in matches:
    keyed_matches[i['key']] = i

all_series = []
same_result = []
different_result = []
for i in matches_keys:
    series_results = []
    for j in i:
        if j in keyed_matches:
            series_results.append(keyed_matches[j]['winning_alliance'])
    all_series.append(series_results)
    if series_results[0] == series_results[1] or series_results[0] == series_results[2]:
        same_result.append(series_results)
    else:
        different_result.append(series_results)

print(all_series)
print(same_result)
print(different_result)
