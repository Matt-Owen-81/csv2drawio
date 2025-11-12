import csv
import yaml
import uuid
import base64
import zlib
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

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

def generate_diagram(config, header, sub_map):
    layout = config['layout']
    shape = config['shape']

    header_x = layout['header_x']
    header_y = layout['header_y']
    sub_indent_x = layout['subheader_indent_x']
    sub_gap_y = layout['subheader_gap_y']
    item_gap_x = layout['item_gap_x']
    item_gap_y = layout['item_gap_y']
    item_spacing_x = layout['item_spacing_x']
    item_to_subheader_gap_y = layout['item_to_subheader_gap_y']
    item_wrap_limit = layout.get('item_wrap_limit', 4)

    sub_w = shape['subheader']['width']
    sub_h = shape['subheader']['height']
    item_w = shape['item']['width']
    item_h = shape['item']['height']
    header_h = shape['header']['height']
    label_h = shape['label']['height']
    label_w = shape['label']['width']
    bg_style = shape['background']['style']
    pad_x = shape['background']['padding_x']
    pad_y = shape['background']['padding_y']

    status_colors = {
        'Red': '#f8cecc',
        'Amber': '#fff2cc',
        'Green': '#d5e8d4'
    }

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

    # Calculate header width
    max_item_right = header_x
    for sub, items in sub_map.items():
        for i_index in range(len(items)):
            col = i_index % item_wrap_limit
            item_x = header_x + sub_indent_x + sub_w + item_gap_x + col * item_spacing_x
            item_right = item_x + item_w
            max_item_right = max(max_item_right, item_right)
    header_width = max_item_right - header_x + item_gap_x

    header_id = str(uuid.uuid4())
    diagram.append(create_cell(header_id, header, shape['header']['style'], header_x, header_y, header_width, header_h))

    current_y = header_y + header_h + sub_gap_y

    for sub_index, (sub, items) in enumerate(sub_map.items()):
        sub_x = header_x + sub_indent_x
        sub_y = current_y
        sub_id = str(uuid.uuid4())
        diagram.append(create_cell(sub_id, sub, shape['subheader']['style'], sub_x, sub_y, sub_w, sub_h))

        # Connect header to subheader
        center_x = header_x + header_width / 2
        mid_y = header_y + header_h + sub_gap_y / 2
        bend_x = header_x + sub_indent_x / 2
        diagram.append(create_edge(
            header_id, sub_id,
            header_x + 20, header_y + header_h,
            sub_x, sub_y + sub_h / 2,
            points=[(center_x, mid_y), (bend_x, mid_y), (bend_x, sub_y + sub_h / 2)],
            style="edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0;entryY=0.5;"
        ))

        # Split items by scope
        items_true = [row for row in items if row.get('Scope') == 'TRUE']
        items_false = [row for row in items if row.get('Scope') == 'FALSE']
        groups = [('Item 1', items_true), ('Item 2', items_false)]

        for label_index, (label_text, group_items) in enumerate(groups):
            label_y = sub_y + sub_h + item_to_subheader_gap_y + label_index * 200
            label_id = str(uuid.uuid4())
            diagram.append(create_cell(label_id, label_text, shape['label']['style'], sub_x, label_y, label_w, label_h))

            # Connect subheader to label
            diagram.append(create_edge(
                sub_id, label_id,
                sub_x + sub_w / 2, sub_y + sub_h,
                sub_x + label_w / 2, label_y,
                points=[(sub_x + sub_w / 2, label_y - 20), (sub_x + label_w / 2, label_y - 20)],
                style="edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
            ))

            # Background box
            cols = min(len(group_items), item_wrap_limit)
            rows = (len(group_items) - 1) // item_wrap_limit + 1
            bg_width = cols * item_w + (cols - 1) * item_spacing_x
            bg_height = rows * item_h + (rows - 1) * item_gap_y
            bg_x = sub_x + sub_w + item_gap_x - pad_x
            bg_y = label_y + label_h + item_gap_y - pad_y
            bg_id = str(uuid.uuid4())
            diagram.append(create_cell(bg_id, '', bg_style, bg_x, bg_y, bg_width + 2 * pad_x, bg_height + 2 * pad_y))

            # Items
            for i_index, row in enumerate(group_items):
                item = row['Item']
                status = row.get('Status', 'Amber')
                fill = status_colors.get(status, '#fff2cc')
                style = f"rounded=1;fillColor={fill}"

                row_num = i_index // item_wrap_limit
                col = i_index % item_wrap_limit
                item_x = sub_x + sub_w + item_gap_x + col * item_spacing_x
                item_y = label_y + label_h + item_gap_y + row_num * (item_h + item_gap_y)
                item_id = str(uuid.uuid4())
                diagram.append(create_cell(item_id, item, style, item_x, item_y, item_w, item_h))

                # Connect label to item
                diagram.append(create_edge(
                    label_id, item_id,
                    sub_x + label_w / 2, label_y + label_h,
                    item_x + item_w / 2, item_y,
                    points=[(sub_x + label_w / 2,
