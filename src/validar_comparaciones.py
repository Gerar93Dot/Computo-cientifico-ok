"""Control pandas para comparar con las hojas nuevas de Power BI.

Ejecutar: python src/validar_comparaciones.py
No ejecuta DAX ni abre Power BI. Conserva resultados esperados para revisión.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def comparar(df, inicio, fin):
    if inicio > fin:
        raise ValueError('El año final debe ser igual o posterior al inicial.')
    grouped = df.groupby(['CVE_ENT','ANIO'])[['ACCIDENTES','MUERTOS']].sum()
    a, b = grouped.xs(inicio, level='ANIO'), grouped.xs(fin, level='ANIO')
    result = a.add_suffix('_INICIO').join(b.add_suffix('_FIN'), validate='one_to_one')
    for c in ['ACCIDENTES','MUERTOS']:
        result['CAMBIO_'+c] = result[c+'_FIN'] - result[c+'_INICIO']
        result['VARIACION_'+c] = result['CAMBIO_'+c] / result[c+'_INICIO'].where(result[c+'_INICIO'] != 0)
    for suffix in ['INICIO','FIN']:
        result['RAZON_'+suffix] = result['MUERTOS_'+suffix] / result['ACCIDENTES_'+suffix].where(result['ACCIDENTES_'+suffix] != 0) * 1000
    result['CAMBIO_RAZON'] = result.RAZON_FIN-result.RAZON_INICIO
    return result.reset_index()

def main():
    df = pd.read_parquet(ROOT/'data/processed/atus_anual_api.parquet')
    assert len(df)==928 and not df.duplicated(['CVE_ENT','ANIO']).any()
    national = df.groupby('ANIO',as_index=False)[['ACCIDENTES','MUERTOS']].sum().assign(CVE_ENT='00')
    complete = pd.concat([df,national],ignore_index=True)
    result = comparar(complete,2019,2025)
    names = pd.read_parquet(ROOT/'data/processed/dim_entidad.parquet')[['CVE_ENT','NOM_ENTIDAD']]
    result = result.merge(names,on='CVE_ENT',how='left',validate='one_to_one')
    result.loc[result.CVE_ENT=='00','NOM_ENTIDAD']='México nacional'
    years = sorted(df.ANIO.unique())
    checked=0
    for start in years:
        for end in years:
            if end<start: continue
            r=comparar(complete,int(start),int(end)).set_index('CVE_ENT')
            for column in ['CAMBIO_ACCIDENTES','CAMBIO_MUERTOS']:
                assert r.loc['00',column] == r.drop('00')[column].sum()
                if start==end: assert (r[column]==0).all()
            checked+=1
    try:
        comparar(complete,2025,2019)
        raise AssertionError('Periodo invertido no detectado')
    except ValueError:
        pass
    sample=pd.DataFrame({'CVE_ENT':['01','01'],'ANIO':[2019,2025],'ACCIDENTES':[0,10],'MUERTOS':[0,1]})
    zero=comparar(sample,2019,2025)
    assert pd.isna(zero.loc[0,'VARIACION_ACCIDENTES']) and pd.isna(zero.loc[0,'RAZON_INICIO'])
    out=ROOT/'docs'
    result.to_csv(out/'control_comparacion_2019_2025.csv',index=False,encoding='utf-8-sig')
    row=result[result.CVE_ENT=='00'].iloc[0]
    summary={'motor':'pandas','ejecucion_DAX':False,'filas_control':len(result),'pares_de_anios_comprobados':checked,
             'nacional_2019_2025':{k:(int(row[k]) if k.startswith(('ACCIDENTES_','MUERTOS_','CAMBIO_ACCIDENTES','CAMBIO_MUERTOS')) else float(row[k])) for k in result.columns if k not in ['CVE_ENT','NOM_ENTIDAD']}}
    (out/'validacion_comparaciones.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(summary,ensure_ascii=True))

if __name__=='__main__':main()
