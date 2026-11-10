"""Calcula hallazgos desde los Parquet de la API, sin redondear antes de calcular."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed'
df = pd.read_parquet(DATA / 'atus_anual_api.parquet')
entities = pd.read_parquet(DATA / 'dim_entidad.parquet')
annual = df.groupby('ANIO')[['ACCIDENTES', 'MUERTOS', 'HERIDOS']].sum()
annual['MUERTOS_POR_1000'] = annual.MUERTOS / annual.ACCIDENTES * 1000
territory = df.groupby('CVE_ENT')[['ACCIDENTES', 'MUERTOS', 'HERIDOS']].sum().reset_index().merge(entities)
territory = territory.sort_values('MUERTOS', ascending=False)
result = {
    'totales': {k: int(df[k].sum()) for k in ['ACCIDENTES', 'MUERTOS', 'HERIDOS']},
    'muertos_por_1000': float(df.MUERTOS.sum() / df.ACCIDENTES.sum() * 1000),
    'cambio_muertes_2011_2019_pct': float((annual.loc[2019, 'MUERTOS'] / annual.loc[2011, 'MUERTOS'] - 1) * 100),
    'cambio_muertes_2019_2025_pct': float((annual.loc[2025, 'MUERTOS'] / annual.loc[2019, 'MUERTOS'] - 1) * 100),
    'cambio_accidentes_2019_2025_pct': float((annual.loc[2025, 'ACCIDENTES'] / annual.loc[2019, 'ACCIDENTES'] - 1) * 100),
    'participacion_cinco_entidades_pct': float(territory.head(5).MUERTOS.sum() / df.MUERTOS.sum() * 100),
    'anual': json.loads(annual.reset_index().to_json(orient='records')),
    'entidades': json.loads(territory.to_json(orient='records')),
}
(ROOT / 'docs/hallazgos.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['anual', 'entidades']}, ensure_ascii=False, indent=2))
