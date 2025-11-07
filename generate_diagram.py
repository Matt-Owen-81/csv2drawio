import csv
import yaml
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring

def create_cell(id, value, style, x, y, width, height, parent='1', edge=False, source=None, target=None):
    cell = Element('mxCell', {
        'id': id,
        'value': value,
        'style': style,
        'vertex': '0' if edge else '1',
        'edge': '1' if edge else '0',
        'parent': parent
    })
    if edge and source and target:
        cell.set('source', source)
        cell.set('target', target)
    geometry = SubElement(cell, 'mxGeometry', {
        'x': str(x),
        'y': str(y),
        'width': str(width),
        'height': str(height)
    })
    geometry.set('as', 'geometry')
    return cell

def generate_drawio(config, data):
    root = Element('mxGraphModel', {
        'dx': '0', 'dy': '0',
        'grid': str(config['page'].get('grid', 1)),
        'gridSize': str(config['page'].get('gridSize', 10)),
        'guides': str(config['page'].get('guides', 1)),
        'tooltips': str(config['page'].get('tooltips', 1)),
        'connect': str(config['page'].get('connect', 1)),
        'arrows': str(config['page'].get('arrows', 1)),
        'fold': str(config['page'].get('fold', 1)),
        'page': '1',
        'pageScale': str(config['page'].get('pageScale', 1)),
        'pageWidth': str(config['page'].get('pageWidth', config['page']['width'])),
        'pageHeight': str(config['page'].get('pageHeight', config['page']['height'])),
        'background': config['page'].get('background', '#ffffff')
    })

    diagram = SubElement(root, 'root')
    SubElement(diagram, 'mxCell', {'id': '0'})
    SubElement(diagram, 'mxCell', {'id': '1', 'parent': '0'})

    layout = config['layout']
    shape = config['shape']

    header_x = layout['header_x']
    header_y = layout['header_y']
    sub_indent = layout['subheader_indent']
    sub_spacing_y = layout['subheader_spacing_y']
    item_spacing_x = layout['item_spacing_x']
    item_spacing_y = layout['item_spacing_y']

    sub_w = shape['subheader']['width']
    sub_h = shape['subheader']['height']
    item_w = shape['item']['width']
    item_h = shape['item']['height']

    grouped = {}
    for row in data:
        h = row['Header']
        s = row['Sub-Header']
        i = row['Item']
        grouped.setdefault(h, {}).setdefault(s, []).append(i)

    for h_index, (header, sub_map) in enumerate(grouped.items()):
        max_item_count = max(len(items) for items in sub_map.values())
        max_item_x = header_x + sub_indent + sub_w + (max_item_count * item_spacing_x)
        header_width = max_item_x - header_x

        header_id = str(uuid.uuid4())
        diagram.append(create_cell(
            header_id, header, shape['header']['style'],
            header_x, header_y, header_width, shape['header']['height']
        ))

        for s_index, (sub, items) in enumerate(sub_map.items()):
            sub_y = header_y + shape['header']['height'] + (s_index * sub_spacing_y)
            sub_x = header_x + sub_indent
            sub_id = str(uuid.uuid4())
            diagram.append(create_cell(
                sub_id, sub, shape['subheader']['style'],
                sub_x, sub_y, sub_w, sub_h
            ))
            diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=header_id, target=sub_id))

            for i_index, item in enumerate(items):
                item_x = sub_x + sub_w + (i_index * item_spacing_x)
                item_y = sub_y + item_spacing_y
                item_id = str(uuid.uuid4())
                diagram.append(create_cell(
                    item_id, item, shape['item']['style'],
                    item_x, item_y, item_w, item_h
                ))
                diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=sub_id, target=item_id))

    return tostring(root, encoding='unicode')

# Load config and data
with open('config.yaml') as f:
    config = yaml.safe_load(f)

with open('data.csv') as f:
    reader = csv.DictReader(f)
    data = list(reader)

# Generate diagram XML
xml_output = generate_drawio(config, data)

# Save to file
with open('diagram.drawio', 'w') as f:
    f.write(xml_output)
