import csv
import yaml
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring

def create_cell(id, value, style, x, y, width, height, parent=None, edge=False, source=None, target=None):
    cell = Element('mxCell', {
        'id': id,
        'value': value,
        'style': style,
        'vertex': '0' if edge else '1',
        'edge': '1' if edge else '0',
        'parent': parent or '1'
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
    root = Element('mxGraphModel')
    root.set('dx', '0')
    root.set('dy', '0')
    root.set('grid', '1')
    root.set('gridSize', '10')
    root.set('guides', '1')
    root.set('tooltips', '1')
    root.set('connect', '1')
    root.set('arrows', '1')
    root.set('fold', '1')
    root.set('page', '1')
    root.set('pageScale', '1')
    root.set('pageWidth', str(config['page']['width']))
    root.set('pageHeight', str(config['page']['height']))
    root.set('background', config['page']['background'])

    diagram = SubElement(root, 'root')
    SubElement(diagram, 'mxCell', {'id': '0'})
    SubElement(diagram, 'mxCell', {'id': '1', 'parent': '0'})

    y_offset = 50
    x_offset = 50

    header_id = str(uuid.uuid4())
    diagram.append(create_cell(header_id, data[0]['Header'], config['shape']['header']['style'], x_offset + 200, y_offset, config['shape']['header']['width'], config['shape']['header']['height']))

    subheaders = {}
    items = {}

    for row in data:
        sub_key = row['Sub-Header']
        item_val = row['Item']

        if sub_key not in subheaders:
            sub_id = str(uuid.uuid4())
            subheaders[sub_key] = sub_id
            y_offset += 80
            diagram.append(create_cell(sub_id, sub_key, config['shape']['subheader']['style'], x_offset, y_offset, config['shape']['subheader']['width'], config['shape']['subheader']['height']))
            diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=header_id, target=sub_id))

        item_id = str(uuid.uuid4())
        diagram.append(create_cell(item_id, item_val, config['shape']['item']['style'], x_offset + 150, y_offset, config['shape']['item']['width'], config['shape']['item']['height']))
        diagram.append(create_cell(str(uuid.uuid4()), '', '', 0, 0, 0, 0, edge=True, source=subheaders[sub_key], target=item_id))
        y_offset += 35

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
