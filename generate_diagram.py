layout = config.get('layout', {})
shape_conf = config['shape']

header_x = layout.get('header_x', 40)
header_y = layout.get('header_y', 40)
subheader_x = layout.get('subheader_x', 40)
subheader_spacing_y = layout.get('subheader_spacing_y', 40)
item_spacing_x = layout.get('item_spacing_x', 40)
item_spacing_y = layout.get('item_spacing_y', 35)

header_width = shape_conf['header']['width']
header_height = shape_conf['header']['height']
subheader_width = shape_conf['subheader']['width']
subheader_height = shape_conf['subheader']['height']

grouped = {}
for row in data:
    h = row['Header']
    s = row['Sub-Header']
    i = row['Item']
    grouped.setdefault(h, {}).setdefault(s, []).append(i)

for h_index, (header, sub_map) in enumerate(grouped.items()):
    header_id = str(uuid.uuid4())
    diagram.append(create_cell(
        header_id, header, shape_conf['header']['style'],
        header_x, header_y, header_width, header_height
    ))

    for s_index, (sub, items) in enumerate(sub_map.items()):
        sub_y = header_y + header_height + (s_index * (subheader_height + subheader_spacing_y * 2))
        sub_id = str(uuid.uuid4())
        diagram.append(create_cell(
            sub_id, sub, shape_conf['subheader']['style'],
            subheader_x, sub_y, subheader_width, subheader_height
        ))
        diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=header_id, target=sub_id))

        for i_index, item in enumerate(items):
            item_x = subheader_x + subheader_width + item_spacing_x
            item_y = header_y + header_height + (i_index * item_spacing_y)
            item_id = str(uuid.uuid4())
            diagram.append(create_cell(
                item_id, item, shape_conf['item']['style'],
                item_x, item_y, shape_conf['item']['width'], shape_conf['item']['height']
            ))
            diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=sub_id, target=item_id))
