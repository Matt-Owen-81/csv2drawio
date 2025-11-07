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

def create_edge(source_id, target_id, source_x, source_y, target_x, target_y, points, style):
    edge_id = str(uuid.uuid4())
    edge = Element('mxCell', {
        'id': edge_id,
        'value': '',
        'style': style,
        'edge': '1',
        'parent': '1',
        'source': source_id,
        'target': target_id
    })
    geometry = SubElement(edge, 'mxGeometry', {'relative': '1'})
    geometry.set('as', 'geometry')
    SubElement(geometry, 'mxPoint', {'x': str(source_x), 'y': str(source_y)}).set('as', 'sourcePoint')
    SubElement(geometry, 'mxPoint', {'x': str(target_x), 'y': str(target_y)}).set('as', 'targetPoint')
    array = SubElement(geometry, 'Array', {'as': 'points'})
    for px, py in points:
        SubElement(array, 'mxPoint', {'x': str(px), 'y': str(py)})
    return edge

def generate_drawio(config, data):
    root = Element('mxGraphModel', {
        'dx': '0', 'dy': '0',
        'grid': str(config['page']['grid']),
        'gridSize': str(config['page']['gridSize']),
        'guides': str(config['page']['guides']),
        'tooltips': str(config['page']['tooltips']),
        'connect': str(config['page']['connect']),
        'arrows': str(config['page']['arrows']),
        'fold': str(config['page']['fold']),
        'page': '1',
        'pageScale': str(config['page']['pageScale']),
        'pageWidth': str(config['page']['pageWidth']),
        'pageHeight': str(config['page']['pageHeight']),
        'background': config['page']['background']
    })

    diagram = SubElement(root, 'root')
    SubElement(diagram, 'mxCell', {'id': '0'})
    SubElement(diagram, 'mxCell', {'id': '1', 'parent': '0'})

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
    item_to_subheader_gap_y = layout['item_to_subheader_gap_y']
    item_wrap_limit = layout.get('item_wrap_limit', 4)

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

    for header, sub_map in grouped.items():
        max_item_right = header_x
        for sub_index, (sub, items) in enumerate(sub_map.items()):
            for i_index, item in enumerate(items):
                col = i_index % item_wrap_limit
                item_x = header_x + sub_indent_x + sub_w + item_gap_x + col * item_spacing_x
                item_right = item_x + item_w
                max_item_right = max(max_item_right, item_right)

        header_width = max_item_right - header_x + item_gap_x
        header_id = str(uuid.uuid4())
        diagram.append(create_cell(header_id, header, shape['header']['style'], header_x, header_y, header_width, header_h))

        for sub_index, (sub, items) in enumerate(sub_map.items()):
            sub_x = header_x + sub_indent_x
            sub_y = header_y + header_h + sub_gap_y + sub_index * sub_spacing_y
            sub_id = str(uuid.uuid4())
            diagram.append(create_cell(sub_id, sub, shape['subheader']['style'], sub_x, sub_y, sub_w, sub_h))

            # Header → Subheader connector
            source_x = header_x + 20
            source_y = header_y + header_h
            target_x = sub_x
            target_y = sub_y + sub_h / 2
            mid_y = header_y + header_h + sub_gap_y / 2
            bend_x = header_x + sub_indent_x / 2
            center_x = header_x + header_width / 2
            diagram.append(create_edge(
                header_id, sub_id,
                source_x, source_y,
                target_x, target_y,
                points=[
                    (center_x, mid_y),
                    (bend_x, mid_y),
                    (bend_x, target_y)
                ],
                style="edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0;entryY=0.5;"
            ))

            for i_index, item in enumerate(items):
                row = i_index // item_wrap_limit
                col = i_index % item_wrap_limit
                item_x = sub_x + sub_w + item_gap_x + col * item_spacing_x
                item_y = sub_y + sub_h + item_gap_y + row * (item_h + item_gap_y)
                item_id = str(uuid.uuid4())
                diagram.append(create_cell(item_id, item, shape['item']['style'], item_x, item_y, item_w, item_h))

                # Subheader → Item connector
                source_x = sub_x + sub_w / 2
                source_y = sub_y + sub_h
                target_x = item_x + item_w / 2
                target_y = item_y
                bend_y = target_y - 20
                diagram.append(create_edge(
                    sub_id, item_id,
                    source_x, source_y,
                    target_x, target_y,
                    points=[
                        (source_x, bend_y),
                        (target_x, bend_y)
                    ],
                    style="edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
                ))

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
