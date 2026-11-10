"""API oficial INEGI -> JSON originales -> Parquet -> validaciones.

Valida cobertura, tipos y totales nacionales sin sustituir datos ausentes por ceros.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/'
LICENSE = 'https://www.inegi.org.mx/inegi/terminos.html'


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


def read_token():
    token = os.environ.get('INEGI_TOKEN', '').strip()
    env = ROOT / '.env'
    if not token and env.exists():
        for line in env.read_text(encoding='utf-8-sig').splitlines():
            if line.strip().startswith('INEGI_TOKEN='):
                token = line.split('=', 1)[1].strip().strip('\"').strip("'")
    if not re.fullmatch(r'[a-zA-Z0-9-]{16,128}', token):
        raise ValueError('Configura tu token personal en el archivo .env de la raíz del proyecto (INEGI_TOKEN=...). No se muestra ni se guarda en los resultados.')
    return token


def fetch(path, token, raw_dir, offline=False, refresh=False):
    """Preserva bytes originales y procedencia. Errores sin mostrar la URL secreta."""
    filename = path.replace('/', '_') + '.json'
    target = raw_dir / filename
    meta_path = target.with_suffix('.meta.json')
    if target.exists() and not refresh:
        raw = target.read_bytes()
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if hashlib.sha256(raw).hexdigest() != meta['sha256']:
            raise ValueError(f'El JSON fue modificado: {filename}')
        return json.loads(raw), meta
    if offline:
        raise ValueError(f'Falta respuesta original para modo sin red: {filename}')
    url = BASE + path + '/' + token + '?type=json'
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'ATUS-PIA/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            data = json.loads(raw)
            if not isinstance(data, dict) or not ('Series' in data or 'CODE' in data):
                raise ValueError('La API no entregó Series/CODE. Revisa el token y los parámetros.')
            break
        except urllib.error.HTTPError as error:
            if error.code in (400, 401, 403, 404):
                raise ValueError(f'INEGI respondió HTTP {error.code}; revisa token, indicador y cobertura.') from None
            if attempt == 2:
                raise ValueError(f'INEGI no respondió correctamente: HTTP {error.code}.') from None
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise ValueError('No fue posible conectar con INEGI después de tres intentos.') from None
        except json.JSONDecodeError:
            raise ValueError('La respuesta del INEGI no es JSON válido.') from None
        time.sleep(2 ** attempt)
    raw_dir.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix('.tmp')
    temp.write_bytes(raw)
    temp.replace(target)
    meta = dict(url=BASE + path + '/TOKEN_OMITIDO?type=json',
                consulta_utc=datetime.now(timezone.utc).isoformat(),
                sha256=hashlib.sha256(raw).hexdigest(), archivo=filename)
    save_json(meta_path, meta)
    return data, meta


def count_value(value):
    """Los valores no disponibles permanecen nulos; los conteos deben ser enteros."""
    if value is None or str(value).strip() in ('', 'N/D', 'ND', 'NA', 'N/A'):
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f'Conteo no numérico inesperado: {value!r}') from None
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError(f'Conteo inválido: {value!r}')
    return int(number)


def parse_series(data, indicator, area):
    series = data.get('Series')
    if not isinstance(series, list) or len(series) != 1:
        raise ValueError(f'Se esperaba una serie de {indicator}, área {area}.')
    series = series[0]
    if str(series.get('INDICADOR')) != indicator:
        raise ValueError('La API devolvió un indicador distinto del solicitado.')
    observations = series.get('OBSERVATIONS', [])
    if not observations:
        raise ValueError(f'Sin observaciones: {indicator}, área {area}')
    rows = []
    for obs in observations:
        period = str(obs.get('TIME_PERIOD', ''))
        if not re.fullmatch(r'\d{4}', period):
            raise ValueError(f'Periodo no anual inesperado: {period!r}')
        geo = str(obs.get('COBER_GEO', ''))
        # La API BISE publica claves simples; aceptar ceros de relleno equivalentes.
        if not geo.isdigit() or int(geo) != int(area):
            raise ValueError(f'Área devuelta {geo!r} distinta del área solicitada {area}.')
        rows.append(dict(ANIO=int(period), CVE_ENT=area,
                         VALOR=count_value(obs.get('OBS_VALUE')),
                         INDICADOR=indicator, ESTATUS=obs.get('OBS_STATUS'),
                         EXCEPCION=obs.get('OBS_EXCEPTION'), NOTA=obs.get('OBS_NOTE'),
                         ACTUALIZACION=series.get('LASTUPDATE')))
    frame = pd.DataFrame(rows)
    if frame.duplicated(['ANIO', 'CVE_ENT', 'INDICADOR']).any():
        raise ValueError('La API devolvió observaciones duplicadas.')
    return frame, series


def parquet(frame, path, provenance):
    table = pa.Table.from_pandas(frame, preserve_index=False)
    metadata = dict(table.schema.metadata or {})
    metadata[b'procedencia'] = json.dumps(provenance, ensure_ascii=False).encode('utf-8')
    table = table.replace_schema_metadata(metadata)
    temporary = path.with_suffix('.tmp')
    pq.write_table(table, temporary, compression='snappy')
    reread = pq.read_table(temporary).to_pandas()
    pd.testing.assert_frame_equal(frame, reread)
    temporary.replace(path)


def build_tables(long, config):
    long = long[long.ANIO.between(config['anio_inicio'], config['anio_fin'])].copy()
    mapping = {v['id']: k for k, v in config['indicadores'].items()}
    long['MEDIDA'] = long.INDICADOR.map(mapping)
    wide = long.pivot(index=['ANIO', 'CVE_ENT'], columns='MEDIDA', values='VALOR').reset_index()
    wide.columns.name = None
    for key in mapping.values():
        if key not in wide:
            raise ValueError(f'Falta indicador {key}')
        wide[key] = wide[key].astype('Int64')
    if wide.empty:
        raise ValueError('Sin datos dentro del intervalo configurado.')
    wide['ANIO'] = wide.ANIO.astype('int64')
    wide['CVE_ENT'] = wide.CVE_ENT.astype('string')
    wide['FECHA'] = pd.to_datetime(wide.ANIO.astype(str) + '-01-01').astype('datetime64[ns]')
    national = wide[wide.CVE_ENT == '00'].copy().reset_index(drop=True)
    facts = wide[wide.CVE_ENT != '00'].copy().reset_index(drop=True)
    # Si falta una entidad/medida, detenerse para no presentar totales incompletos.
    expected = pd.MultiIndex.from_product([sorted(wide.ANIO.unique()), config['entidades']], names=['ANIO', 'CVE_ENT'])
    actual = pd.MultiIndex.from_frame(facts[['ANIO', 'CVE_ENT']])
    if len(expected.difference(actual)) or facts[list(mapping.values())].isna().any().any():
        raise ValueError('Cobertura incompleta por entidad/año/indicador. Revisa los JSON; no se publicaron totales parciales.')
    dates = pd.DataFrame({'FECHA': pd.date_range(f'{wide.ANIO.min()}-01-01', f'{wide.ANIO.max()}-12-31')})
    dates['FECHA'] = dates.FECHA.astype('datetime64[ns]')
    dates['ANIO'] = dates.FECHA.dt.year.astype('int64')
    dates['MES'] = dates.FECHA.dt.month.astype('int64')
    dates['DIA'] = dates.FECHA.dt.day.astype('int64')
    return facts, national, dates


def validations(facts, national):
    metrics = ['ACCIDENTES', 'MUERTOS', 'HERIDOS']
    totals = facts.groupby('ANIO')[metrics].sum(min_count=1)
    reference = national.set_index('ANIO')[metrics]
    if set(totals.index) != set(reference.index) or reference.isna().any().any():
        raise ValueError('Falta cobertura nacional para contrastar los totales estatales.')
    diff = totals - reference
    if (diff != 0).any().any():
        raise ValueError('La suma estatal no coincide con la serie nacional. Revisa la edición y cobertura de los JSON antes de generar los Parquet.')
    checks = []
    for year in totals.index:
        for metric in metrics:
            checks.append(dict(anio=int(year), medida=metric,
                               suma_entidades=int(totals.loc[year, metric]),
                               nacional_api=int(reference.loc[year, metric]),
                               diferencia=int(diff.loc[year, metric])))
    return dict(validacion='pandas: suma de entidades frente a serie nacional independiente de la API',
                coincide_nacional=bool((diff == 0).all().all()),
                totales={k: int(facts[k].sum()) for k in metrics}, por_anio=checks)


def run(args):
    config = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
    token = '' if args.offline else read_token()
    raw_dir = ROOT / 'data' / 'raw'
    output = ROOT / 'data' / 'processed'
    frames, sources, descriptions, entities = [], [], {}, []
    for metric, item in config['indicadores'].items():
        key = item['id']
        data, meta = fetch(f'CL_INDICATOR/{key}/es/BISE/2.0', token, raw_dir, args.offline, args.refresh)
        codes = data.get('CODE', [])
        matches = [x for x in codes if str(x.get('value')) == key]
        if len(matches) != 1 or matches[0].get('Description', '').strip().casefold() != item['titulo'].casefold():
            raise ValueError(f'La descripción oficial cambió o no corresponde a {key}; revisar antes de continuar.')
        descriptions[key] = matches[0]['Description']
        sources.append(meta)
        for area in ['00'] + config['entidades']:
            print(f'Consultando {metric}, área {area}', flush=True)
            data, meta = fetch(f'INDICATOR/{key}/es/{area}/false/BISE/2.0', token, raw_dir, args.offline, args.refresh)
            frame, series = parse_series(data, key, area)
            frames.append(frame)
            sources.append(meta)
            # Preservar también los metadatos de unidad, frecuencia, fuente y notas.
            for field, catalog in [('UNIT', 'CL_UNIT'), ('FREQ', 'CL_FREQ'), ('SOURCE', 'CL_SOURCE'), ('NOTE', 'CL_NOTE')]:
                if series.get(field):
                    _, metadata = fetch(f'{catalog}/{series[field]}/es/BISE/2.0', token, raw_dir, args.offline, False)
                    if metadata not in sources:
                        sources.append(metadata)
    for area in config['entidades']:
        data, meta = fetch(f'CL_GEO_AREA/{area}/es/BISE/2.0', token, raw_dir, args.offline, args.refresh)
        codes = data.get('CODE', [])
        matches = [x for x in codes if str(x.get('value', '')).isdigit() and int(x['value']) == int(area)]
        if len(matches) != 1:
            raise ValueError(f'Catálogo geográfico inesperado para {area}')
        entities.append(dict(CVE_ENT=area, NOM_ENTIDAD=matches[0]['Description']))
        sources.append(meta)
    facts, national, dates = build_tables(pd.concat(frames, ignore_index=True), config)
    checks = validations(facts, national)
    years = sorted(int(y) for y in facts.ANIO.unique())
    missing = sorted(set(range(config['anio_inicio'], config['anio_fin'] + 1)) - set(years))
    provenance = dict(programa='ATUS', origen='API oficial del Banco de Indicadores INEGI',
                      licencia=LICENSE, configuracion=config, respuestas=sources,
                      descripcion_indicadores=descriptions, anios_disponibles=years,
                      anios_no_disponibles=missing,
                      granularidad='Una fila por entidad federativa y año; conteos agregados',
                      fecha_anual='1 de enero como clave de relación; NO fecha de cada accidente')
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in [('atus_anual_api', facts), ('control_nacional', national),
                        ('dim_fecha', dates), ('dim_entidad', pd.DataFrame(entities).astype('string'))]:
        parquet(frame, output / f'{name}.parquet', provenance)
    checks['anios_no_disponibles'] = missing
    save_json(output / 'validacion_medidas.json', checks)
    save_json(output / 'procedencia.json', provenance)
    print(f'Parquet generado. Años: {years[0]}–{years[-1]}; filas estatales: {len(facts)}.')
    print(f'Años solicitados sin información: {missing}. Coincidencia con nacional: {checks["coincide_nacional"]}.')
    print('La validación compara fórmulas equivalentes en pandas; coteja también las tarjetas en Power BI Desktop.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--offline', action='store_true', help='Reprocesa JSON originales con verificación SHA-256; no requiere token.')
    mode.add_argument('--refresh', action='store_true', help='Actualiza respuestas de la API; conserva antes una copia si necesitas la edición anterior.')
    try:
        run(parser.parse_args())
    except (ValueError, OSError, KeyError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
