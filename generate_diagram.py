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
    # Create root graph model
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

    # Create diagram root
    diagram = SubElement(root, 'root')
    SubElement(diagram, 'mxCell', {'id': '0'})
    SubElement(diagram, 'mxCell', {'id': '1', 'parent': '0'})

    # Load layout and shape config
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
    item_width = shape_conf['item']['width']
    item_height = shape_conf['item']['height']

    # Group data
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
                    item_x, item_y, item_width, item_height
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
