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
        'dx': '0', 'dy': '0', 'grid': '1', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1',
        'arrows': '1', 'fold': '1', 'page': '1', 'pageScale': '1',
        'pageWidth': str(config['page']['width']),
        'pageHeight': str(config['page']['height']),
        'background': config['page']['background']
    })

    diagram = SubElement(root, 'root')
    SubElement(diagram, 'mxCell', {'id': '0'})
    SubElement(diagram, 'mxCell', {'id': '1', 'parent': '0'})

    layout = config.get('layout', {})
    header_x = layout.get('header_x', 400)
    header_y = layout.get('header_y', 50)
    subheader_spacing_y = layout.get('subheader_spacing_y', 100)
    item_spacing_x = layout.get('item_spacing_x', 150)
    item_spacing_y = layout.get('item_spacing_y', 35)

    shape_conf = config['shape']
    grouped = {}
    for row in data:
        h = row['Header']
        s = row['Sub-Header']
        i = row['Item']
        grouped.setdefault(h, {}).setdefault(s, []).append(i)

    for h_index, (header, sub_map) in enumerate(grouped.items()):
        header_id = str(uuid.uuid4())
        h_y = header_y + h_index * (len(sub_map) * subheader_spacing_y + 80)
        diagram.append(create_cell(
            header_id, header, shape_conf['header']['style'],
            header_x, h_y, shape_conf['header']['width'], shape_conf['header']['height']
        ))

        for s_index, (sub, items) in enumerate(sub_map.items()):
            sub_id = str(uuid.uuid4())
            s_y = h_y + s_index * subheader_spacing_y
            s_x = header_x - item_spacing_x
            diagram.append(create_cell(
                sub_id, sub, shape_conf['subheader']['style'],
                s_x, s_y, shape_conf['subheader']['width'], shape_conf['subheader']['height']
            ))
            diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=header_id, target=sub_id))

            for i_index, item in enumerate(items):
                item_id = str(uuid.uuid4())
                i_x = s_x + item_spacing_x * 2
                i_y = s_y + i_index * item_spacing_y
                diagram.append(create_cell(
                    item_id, item, shape_conf['item']['style'],
                    i_x, i_y, shape_conf['item']['width'], shape_conf['item']['height']
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
