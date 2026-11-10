# -*- coding: utf-8 -*-
"""
CAD GEOMETRY TOOL: Pure-Python DXF AutoCAD Parser
Tu dong doc ban ve CAD (.dxf) boc tach chieu dai coc, dam, dien tich san va dem block thiet bi.
Khong phu thuoc phan mem ban quyen ngoai.
"""

import math
from typing import Dict, List, Any

class PureDXFParser:
    """
    Parser doc ban ve CAD DXF chuan quoc te (Group Code ASCII)
    - 0: Entity type (LINE, LWPOLYLINE, CIRCLE, INSERT, TEXT)
    - 8: Layer name
    - 10, 20, 30: Coordinate X, Y, Z
    - 40: Radius / Height
    - 70: Flags (Closed polyline)
    """

    @staticmethod
    def parse_dxf_content(dxf_text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in dxf_text.splitlines()]
        layers = set()
        entities = []
        
        i = 0
        n = len(lines)
        current_entity = None

        while i < n - 1:
            code = lines[i]
            val = lines[i + 1]

            if code == '0':
                if current_entity:
                    entities.append(current_entity)
                if val in ['LINE', 'LWPOLYLINE', 'CIRCLE', 'INSERT', 'TEXT', 'MTEXT']:
                    current_entity = {'type': val, 'layer': '0', 'points': [], 'props': {}}
                else:
                    current_entity = None
            elif current_entity:
                if code == '8':
                    current_entity['layer'] = val
                    layers.add(val)
                elif code == '10':
                    current_entity['props']['x'] = float(val) if val.replace('.','',1).replace('-','',1).isdigit() else 0.0
                elif code == '20':
                    current_entity['props']['y'] = float(val) if val.replace('.','',1).replace('-','',1).isdigit() else 0.0
                elif code == '11':
                    current_entity['props']['x2'] = float(val) if val.replace('.','',1).replace('-','',1).isdigit() else 0.0
                elif code == '21':
                    current_entity['props']['y2'] = float(val) if val.replace('.','',1).replace('-','',1).isdigit() else 0.0
                elif code == '40':
                    current_entity['props']['radius'] = float(val) if val.replace('.','',1).isdigit() else 0.0
                elif code == '2':
                    current_entity['props']['block_name'] = val
                elif code == '70':
                    current_entity['props']['is_closed'] = (int(val) & 1) == 1 if val.isdigit() else False

            i += 2

        if current_entity:
            entities.append(current_entity)

        # Thong ke va tinh toan hinh hoc
        total_line_length = 0.0
        circle_count = 0
        total_circle_area = 0.0
        block_counts = {}
        layer_stats = {}

        for ent in entities:
            etype = ent['type']
            layer = ent['layer']
            layer_stats[layer] = layer_stats.get(layer, 0) + 1

            if etype == 'LINE':
                x1 = ent['props'].get('x', 0)
                y1 = ent['props'].get('y', 0)
                x2 = ent['props'].get('x2', 0)
                y2 = ent['props'].get('y2', 0)
                length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                total_line_length += length

            elif etype == 'CIRCLE':
                circle_count += 1
                r = ent['props'].get('radius', 0)
                area = math.pi * (r ** 2)
                total_circle_area += area

            elif etype == 'INSERT':
                bname = ent['props'].get('block_name', 'Khong_ten')
                block_counts[bname] = block_counts.get(bname, 0) + 1

        return {
            "total_entities": len(entities),
            "layers": sorted(list(layers)),
            "layer_stats": layer_stats,
            "total_line_length_meters": round(total_line_length / 1000.0, 2) if total_line_length > 1000 else round(total_line_length, 2),
            "circle_count": circle_count,
            "total_circle_area_m2": round(total_circle_area / 1_000_000.0, 2) if total_circle_area > 10000 else round(total_circle_area, 2),
            "block_inventory": block_counts
        }

    @classmethod
    def analyze_file(cls, filepath: str) -> Dict[str, Any]:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return cls.parse_dxf_content(content)
        except Exception as e:
            return {"error": f"Lỗi đọc file DXF: {str(e)}"}
