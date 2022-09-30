import json

a1 = json.loads(open('combined_4.json').read())
a2 = json.loads(open('9_16.json').read())

output = a1
img_offset = a1['images'][-1]['id']
annotation_offset = a1['annotations'][-1]['id']

img_names = {}
images = {}
annotations = {}
id_map = {}

for i in a1['images']:
    img_names[i['file_name']] = i['id']

for i in a2['images']:
    if i['file_name'] in img_names:
        new_id = img_names[i['file_name']]
        id_map[i['id']] = new_id
        img_offset -= 1
        continue
    else:
        new_id = i['id'] + img_offset
        id_map[i['id']] = new_id
        i['id'] = new_id
        images[i['id']] = i
for i in a2['annotations']:
    i['id'] += annotation_offset
    i['image_id'] = id_map[i['image_id']]

    values = annotations.get(i['image_id'], [])
    values.append(i)
    annotations[i['image_id']] = values

for k, v in images.items():
    if k in annotations:
        output['images'].append(v)

for k, v in annotations.items():
    output['annotations'].extend(v)

open('combined_5.json', 'w').write(json.dumps(output))
