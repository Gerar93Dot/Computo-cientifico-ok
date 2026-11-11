import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'reportes'


class Profesional(unittest.TestCase):
    def test_selectores_anios_sin_filtro_restrictivo(self):
        model = ROOT / 'ATUS_API_Profesional.SemanticModel/definition/tables'
        pages = ROOT / 'ATUS_API_Profesional.Report/definition/pages/cambios_periodo'
        found = set()
        for p in pages.glob('visuals/*/visual.json'):
            obj = json.loads(p.read_text(encoding='utf8'))
            v = obj['visual']
            if v['visualType'] != 'slicer':
                continue
            column = v['query']['queryState']['Values']['projections'][0]['field']['Column']
            name = column['Expression']['SourceRef']['Entity']
            if name not in ('Seleccion_Inicio', 'Seleccion_Fin'):
                continue
            found.add(name)
            self.assertNotIn('filterConfig', obj)
            self.assertEqual(v['query']['sortDefinition']['sort'][0]['direction'], 'Ascending')
            definition = (model / (name+'.tmdl')).read_text(encoding='utf8')
            self.assertIn('= calculated', definition)
            self.assertIn('sourceColumn: [ANIO]', definition)
            self.assertIn('GENERATESERIES(1997, 2025, 1)', definition)
        self.assertEqual(found, {'Seleccion_Inicio', 'Seleccion_Fin'})

    def test_referencias_y_diseno(self):
        tables = {}
        for path in (ROOT / 'ATUS_API_Profesional.SemanticModel/definition/tables').glob('*.tmdl'):
            tables[path.stem] = {a or b for a, b in re.findall(r"(?m)^\t(?:column|measure) (?:'([^']+)'|([^ =\n]+))", path.read_text(encoding='utf8'))}
        def walk(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ('Column', 'Measure') and isinstance(value, dict) and 'Property' in value:
                        entity = value.get('Expression', {}).get('SourceRef', {}).get('Entity')
                        if entity:
                            self.assertIn(value['Property'], tables.get(entity, set()), (entity,value['Property']))
                    walk(value)
            elif isinstance(obj, list):
                for value in obj:
                    walk(value)
        visuals = list((ROOT / 'ATUS_API_Profesional.Report').rglob('visual.json'))
        pages_dir = ROOT / 'ATUS_API_Profesional.Report/definition/pages'
        metadata = json.loads((pages_dir / 'pages.json').read_text(encoding='utf8'))
        self.assertEqual(metadata['pageOrder'], ['8b1a6ac879a0a1740f1b', '74eaa1553ef898147305', 'cantidad_gravedad', 'cambios_periodo', '514e3a3d1cf71f4da7c1'])
        self.assertEqual(len(visuals), 43)
        for path in visuals:
            obj = json.loads(path.read_text(encoding='utf8'))
            walk(obj)
            self.assertNotEqual(obj['visual']['visualType'], 'lineClusteredColumnComboChart')

    def test_interacciones_y_limites(self):
        pages = ROOT / 'ATUS_API_Profesional.Report/definition/pages'
        for name in ('cantidad_gravedad', 'cambios_periodo'):
            page = json.loads((pages / name / 'page.json').read_text(encoding='utf8'))
            visuals = [json.loads(p.read_text(encoding='utf8')) for p in (pages/name).glob('visuals/*/visual.json')]
            ids = {v['name'] for v in visuals}
            for interaction in page['visualInteractions']:
                self.assertIn(interaction['source'], ids)
                self.assertIn(interaction['target'], ids)
            for v in visuals:
                p = v['position']
                self.assertGreaterEqual(p['x'], 0)
                self.assertGreaterEqual(p['y'], 0)
                self.assertLessEqual(p['x']+p['width'], page['width'])
                self.assertLessEqual(p['y']+p['height'], page['height'])
                if v['visual']['visualType']=='tableEx':
                    self.assertTrue(all(p['active'] for p in v['visual']['query']['queryState']['Values']['projections']))
            if name=='cantidad_gravedad':
                scatter=next(v['name'] for v in visuals if v['visual']['visualType']=='scatterChart')
                self.assertTrue(any(i['source']==scatter and i['type']=='DataFilter' for i in page['visualInteractions']))


if __name__ == '__main__':
    unittest.main()
