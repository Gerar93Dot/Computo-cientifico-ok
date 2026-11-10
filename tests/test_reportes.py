import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'reportes'


class Profesional(unittest.TestCase):
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
        self.assertEqual(len(visuals), 19)
        for path in visuals:
            obj = json.loads(path.read_text(encoding='utf8'))
            walk(obj)
            self.assertNotEqual(obj['visual']['visualType'], 'lineClusteredColumnComboChart')


if __name__ == '__main__':
    unittest.main()
