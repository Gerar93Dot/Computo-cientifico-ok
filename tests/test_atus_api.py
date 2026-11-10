"""Pruebas con datos SINTÉTICOS; nunca se utilizan para alimentar el reporte."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import pandas as pd

spec = importlib.util.spec_from_file_location('atus_api', Path(__file__).resolve().parents[1] / 'src' / 'atus_api.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class PipelineTests(unittest.TestCase):
    def response(self, value='12.000', area='01', period='2024'):
        return {'Series': [{'INDICADOR': '123', 'OBSERVATIONS': [
            {'TIME_PERIOD': period, 'OBS_VALUE': value, 'COBER_GEO': area}]}]}

    def test_no_disponible_no_es_cero(self):
        self.assertIsNone(api.count_value(None))
        self.assertIsNone(api.count_value('N/D'))
        self.assertEqual(api.count_value('0.000'), 0)
        for invalid in ['1.5', '-1', 'NaN', 'texto']:
            with self.assertRaises(ValueError):
                api.count_value(invalid)

    def test_rechaza_geografia_periodo_y_duplicados(self):
        for response in [self.response(area='02'), self.response(period='2024/01')]:
            with self.assertRaises(ValueError):
                api.parse_series(response, '123', '01')
        response = self.response()
        response['Series'][0]['OBSERVATIONS'] *= 2
        with self.assertRaises(ValueError):
            api.parse_series(response, '123', '01')

    def test_nacional_no_se_suma_dos_veces_y_parquet_conserva_tipos(self):
        metrics = {'ACCIDENTES': {'id': '1'}, 'MUERTOS': {'id': '2'}, 'HERIDOS': {'id': '3'}}
        config = dict(anio_inicio=2024, anio_fin=2025, entidades=['01', '02'], indicadores=metrics)
        rows = [dict(ANIO=2024, CVE_ENT=area, INDICADOR=i, VALOR=value)
                for i in ['1', '2', '3'] for area, value in [('00', 30), ('01', 10), ('02', 20)]]
        facts, national, dates = api.build_tables(pd.DataFrame(rows), config)
        self.assertEqual(len(facts), 2)
        self.assertEqual(facts.ACCIDENTES.sum(), 30)
        self.assertEqual(len(dates), 366)
        self.assertTrue(api.validations(facts, national)['coincide_nacional'])
        discrepant = national.copy()
        discrepant.loc[0, 'MUERTOS'] += 1
        with self.assertRaisesRegex(ValueError, 'no coincide'):
            api.validations(facts, discrepant)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            output = Path(temp) / 'prueba.parquet'
            api.parquet(facts, output, {'origen': 'PRUEBA SINTETICA'})
            self.assertTrue(output.exists())
        with self.assertRaises(ValueError):
            api.build_tables(pd.DataFrame(rows[:-1]), config)


if __name__ == '__main__':
    unittest.main()
