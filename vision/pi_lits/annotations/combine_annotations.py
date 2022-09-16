import json

a1 = json.loads(open('combined_3.json').read())
a2 = json.loads(open('lanes_1.json').read())

output = a1
img_offset = a1['images'][-1]['id']
annotation_offset = a1['annotations'][-1]['id']

img_names = {}
images = {}
annotations = {}

for i in a1['images']:
    img_names[i['file_name']] = i['id']
    
for i in a2['images']:
    if i['file_name'] in img_names:
        img_offset -= 1
        continue
    else:
        i['id'] += img_offset
        images[i['id']] = i
for i in a2['annotations']:
    i['id'] += annotation_offset
    i['image_id'] += img_offset
    
    values = annotations.get(i['image_id'], [])
    values.append(i)
    annotations[i['image_id']] = values
    
for k, v in images.items():
    if k in annotations:
        output['images'].append(v)

for k, v in annotations.items():
    output['annotations'].extend(v)
    
open('combined_3.json', 'w').write(json.dumps(output))