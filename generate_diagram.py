layout = config['layout']
shape = config['shape']

header_x = layout['header_x']
header_y = layout['header_y']
sub_indent_x = layout['subheader_indent_x']
sub_gap_y = layout['subheader_gap_y']
item_gap_x = layout['item_gap_x']
item_gap_y = layout['item_gap_y']
sub_spacing_y = layout['subheader_spacing_y']
item_spacing_x = layout['item_spacing_x']

sub_w = shape['subheader']['width']
sub_h = shape['subheader']['height']
item_w = shape['item']['width']
item_h = shape['item']['height']
header_h = shape['header']['height']

grouped = {}
for row in data:
    h = row['Header']
    s = row['Sub-Header']
    i = row['Item']
    grouped.setdefault(h, {}).setdefault(s, []).append(i)

for h_index, (header, sub_map) in enumerate(grouped.items()):
    max_item_count = max(len(items) for items in sub_map.values())
    max_item_x = header_x + sub_indent_x + sub_w + layout['item_gap_x'] + (max_item_count * item_spacing_x)
    header_width = max_item_x - header_x

    header_id = str(uuid.uuid4())
    diagram.append(create_cell(
        header_id, header, shape['header']['style'],
        header_x, header_y, header_width, header_h
    ))

    for s_index, (sub, items) in enumerate(sub_map.items()):
        sub_y = header_y + header_h + sub_gap_y + (s_index * sub_spacing_y)
        sub_x = header_x + sub_indent_x
        sub_id = str(uuid.uuid4())
        diagram.append(create_cell(
            sub_id, sub, shape['subheader']['style'],
            sub_x, sub_y, sub_w, sub_h
        ))
        diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=header_id, target=sub_id))

        for i_index, item in enumerate(items):
            item_x = sub_x + sub_w + item_gap_x + (i_index * item_spacing_x)
            item_y = sub_y + sub_h + item_gap_y
            item_id = str(uuid.uuid4())
            diagram.append(create_cell(
                item_id, item, shape['item']['style'],
                item_x, item_y, item_w, item_h
            ))
            diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=sub_id, target=item_id))
