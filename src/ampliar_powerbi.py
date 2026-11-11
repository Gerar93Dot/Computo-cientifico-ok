"""Genera las hojas de cantidad/gravedad y cambios entre años del PBIP.

Solo usa la biblioteca estándar. Conserva las tres páginas existentes.
Ejecutar desde el repositorio: python src/ampliar_powerbi.py
"""
from pathlib import Path
from copy import deepcopy
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reportes/ATUS_API_Profesional.Report'
MODEL = ROOT / 'reportes/ATUS_API_Profesional.SemanticModel/definition'
PAGES = REPORT / 'definition/pages'
F, E, D = 'atus_anual_api', 'dim_entidad', 'dim_fecha'
BLUE, ORANGE, TEAL = '#5CC8FF', '#FFB45C', '#63DBBE'
TEXT, MUTED, BG = '#E6EDF3', '#B5C5D8', '#0F1419'
ACC, DEAD, RATE = 'Total de Accidentes', 'Total de Muertos', 'Muertos por 1000 accidentes'

def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf8')
def lit(s): return {'expr': {'Literal': {'Value': "'" + s.replace("'", "''") + "'"}}}
def num(n): return {'expr': {'Literal': {'Value': str(n) + 'D'}}}
def boolean(b): return {'expr': {'Literal': {'Value': str(b).lower()}}}
def color(s): return {'solid': {'color': lit(s)}}
def field(t, n, m=False): return {'Measure' if m else 'Column': {'Expression': {'SourceRef': {'Entity': t}}, 'Property': n}}
def proj(t, n, m=False, label=None): return {'field': field(t,n,m), 'queryRef': t+'.'+n, 'nativeQueryRef': label or n, 'active': True}
def roles(**kw): return {k: {'projections': v} for k,v in kw.items()}

templates = {}
for p in PAGES.glob('*/visuals/*/visual.json'):
    if p.parts[-4] in ('cantidad_gravedad', 'cambios_periodo'): continue
    v = read(p)
    templates.setdefault(v['visual']['visualType'], v)

def container(title, unit):
    return {
        'title': [{'properties': {'show': boolean(True), 'text': lit(title), 'fontColor': color(TEXT), 'fontSize': num(14), 'titleWrap': boolean(True)}}],
        'subTitle': [{'properties': {'show': boolean(True), 'text': lit(unit+' | INEGI ATUS / API | Libre uso INEGI'), 'fontColor': color(MUTED), 'fontSize': num(9)}}],
        'background': [{'properties': {'show': boolean(True), 'color': color('#1A2230'), 'transparency': num(0)}}],
        'padding': [{'properties': {k:num(10) for k in ('top','bottom','left','right')}}],
        'border': [{'properties': {'show': boolean(True), 'color': color('#2C405A'), 'radius': num(8)}}],
        'general': [{'properties': {'altText': lit(title+'. '+unit+'. Fuente INEGI ATUS.')}}],
    }

def put(kind,x,y,w,h,title='',unit='',query=None,objects=None):
    idx = len(visuals)+1
    name = current['name']+f'v{idx:02}'
    v = {'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json',
         'name':name,'position':dict(x=x,y=y,width=w,height=h,z=idx*1000,tabOrder=idx*1000),
         'visual':{'visualType':kind,'objects':objects or {},'visualContainerObjects':container(title,unit),'drillFilterOtherVisuals':True}}
    if query: v['visual']['query']=query
    visuals.append(v)
    return v

def textbox(text,x,y,w,h,size=16):
    v=put('textbox',x,y,w,h,objects={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':s,'textStyle':{'fontFamily':'Segoe UI','fontSize':f'{size}pt','color':TEXT}}]} for s in text.split('\n')]}}]})
    v['visual']['visualContainerObjects']={'title':[{'properties':{'show':boolean(False)}}], 'padding':[{'properties':{k:num(0) for k in ('top','bottom','left','right')}}]}
    return v

def start(pid,title,subtitle):
    global current,visuals
    visuals=[]
    current={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json','name':pid,'displayName':title,'displayOption':'FitToPage','width':1600,'height':900,
             'objects':{'background':[{'properties':{'color':color(BG),'transparency':num(0)}}]}}
    textbox(subtitle,24,14,1050,60,23)
    textbox('ATUS | 1997–2025 | Condiciones de uso: inegi.org.mx/inegi/terminos.html',24,866,1540,32,10)

def slicer(t,n,label,x,w,default=None):
    obj=deepcopy(templates['slicer']['visual']['objects'])
    obj['header'][0]['properties']['text']=lit(label)
    obj['data'][0]['properties'].pop('isInvertedSelectionMode',None)
    obj['selection']=[{'properties':{'singleSelect':boolean(default is not None),'selectAllCheckboxEnabled':boolean(default is None)}}]
    v=put('slicer',x,8,w,85,query={'queryState':roles(Values=[proj(t,n)])},objects=obj)
    v['visual']['visualContainerObjects']['title'][0]['properties']['show']=boolean(False)
    v['visual']['visualContainerObjects']['subTitle'][0]['properties']['show']=boolean(False)
    if default is not None:
        condition = {'In': {'Expressions': [{'Column': {'Expression': {'SourceRef': {'Source': 's'}}, 'Property': n}}], 'Values': [[{'Literal': {'Value': str(default)+'L'}}]]}}
        v['filterConfig'] = {'filters': [{'name': 'seleccion_'+t, 'field': field(t,n), 'type': 'Categorical', 'filter': {'Version': 2, 'From': [{'Name': 's', 'Entity': t, 'Type': 0}], 'Where': [{'Condition': condition}]}}]}
    return v

def card(m,title,unit,x,y,w,h=115,decimals=2):
    obj=deepcopy(templates['cardVisual']['visual']['objects'])
    obj['value'][0]['properties'].update(fontColor=color(TEAL),fontSize=num(24),decimalPlaces=num(decimals),displayUnits=num(1))
    obj['label'][0]['properties']['show']=boolean(False)
    return put('cardVisual',x,y,w,h,title,unit,{'queryState':roles(Data=[proj(F,m,True,title)])},obj)

def chart(kind,cat,measures,title,unit,x,y,w,h):
    obj=deepcopy(templates[kind]['visual']['objects'])
    obj['valueAxis']=[{'properties':{'show':boolean(True),'labelColor':color(MUTED),'fontSize':num(10),'gridlineShow':boolean(True)}}]
    if kind!='clusteredBarChart' or measures[0]!='Cambio muertes': obj['valueAxis'][0]['properties']['start']=num(0)
    obj['legend']=[{'properties':{'show':boolean(len(measures)>1),'position':lit('Top'),'labelColor':color(TEXT)}}]
    obj['labels']=[{'properties':{'show':boolean(kind=='clusteredBarChart'),'color':color(TEXT),'fontSize':num(10)}}]
    obj['dataPoint']=[{'properties':{'fill':color(BLUE)}}]+[{'properties':{'fill':color([BLUE,ORANGE][i%2])},'selector':{'metadata':F+'.'+m}} for i,m in enumerate(measures)]
    q={'queryState':roles(Category=[proj(*cat)],Y=[proj(F,m,True) for m in measures]),'sortDefinition':{'sort':[{'field':field(*cat),'direction':'Ascending'}],'isDefaultSort':True}}
    if kind=='clusteredBarChart': q['sortDefinition']['sort']=[{'field':field(F,measures[0],True),'direction':'Descending'}]
    return put(kind,x,y,w,h,title,unit,q,obj)

def table(cols,title,unit,x,y,w,h,widths):
    obj=deepcopy(templates['tableEx']['visual']['objects'])
    ps=[proj(*c) for c in cols]
    obj['columnHeaders'][0]['properties'].update(autoSizeColumnWidth=boolean(False),fontSize=num(10))
    obj['values'][0]['properties']['fontSize']=num(10)
    obj['grid'][0]['properties']['rowPadding']=num(2)
    obj['total']=[{'properties':{'totals':boolean(False)}}]
    obj['columnWidth']=[{'properties':{'value':num(width)},'selector':{'metadata':p['queryRef']}} for width,p in zip(widths,ps)]
    return put('tableEx',x,y,w,h,title,unit,{'queryState':roles(Values=ps)},obj)

def finish(enabled=(),ignored=()):
    current['visualInteractions']=[{'source':a['name'],'target':b['name'],'type':'NoFilter'} for a in visuals for b in visuals if a!=b and a['visual']['visualType'] not in ('slicer','textbox') and b['visual']['visualType']!='textbox']
    for a,b in enabled:
        current['visualInteractions']=[i for i in current['visualInteractions'] if (i['source'],i['target'])!=(a['name'],b['name'])]
        current['visualInteractions'].append({'source':a['name'],'target':b['name'],'type':'DataFilter'})
    for a,b in ignored: current['visualInteractions'].append({'source':a['name'],'target':b['name'],'type':'NoFilter'})
    for v in visuals: write(PAGES/current['name']/'visuals'/v['name']/'visual.json',v)
    write(PAGES/current['name']/'page.json',current)

def build():
    # Tablas de selección desconectadas: no alteran las relaciones del modelo en estrella.
    mp=MODEL/'model.tmdl'
    model=mp.read_text(encoding='utf8')
    for name in ('Seleccion_Inicio','Seleccion_Fin'):
        write(MODEL/'tables'/f'{name}.tmdl',f'''table {name}
\t/// Año seleccionado para comparar extremos; tabla sin relaciones.
\tcolumn ANIO
\t\tdataType: int64
\t\tformatString: 0
\t\tsummarizeBy: none
\t\tsourceColumn: ANIO

\tpartition {name} = m
\t\tmode: import
\t\tsource = Table.TransformColumnTypes(Table.FromList(List.Numbers(1997, 29), Splitter.SplitByNothing(), {{"ANIO"}}), {{{{"ANIO", Int64.Type}}}})
''')
        if 'ref table '+name not in model: model+='\nref table '+name+'\n'
    write(mp,model)
    measures={
        'Razon nacional':('CALCULATE([Muertos por 1000 accidentes], REMOVEFILTERS(dim_entidad))','0.00','Referencia que conserva el periodo y quita solo los filtros territoriales.'),
        'Inicio comparacion':('SELECTEDVALUE(Seleccion_Inicio[ANIO], 2019)','0','Año inicial elegido; 2019 cuando no hay una selección única.'),
        'Fin comparacion':('SELECTEDVALUE(Seleccion_Fin[ANIO], 2025)','0','Año final elegido; 2025 cuando no hay una selección única.'),
        'Periodo valido':('IF([Inicio comparacion] <= [Fin comparacion], 1, 0)','0','Evita presentar diferencias con un periodo invertido.'),
    }
    for base,measure in [('Accidentes',ACC),('Muertes',DEAD),('Razon',RATE)]:
        for suffix,year in [('inicio','Inicio comparacion'),('fin','Fin comparacion')]:
            measures[f'{base} {suffix}']=(f'VAR y = [{year}] RETURN IF([Periodo valido] = 1, CALCULATE([{measure}], REMOVEFILTERS(dim_fecha), TREATAS({{y}}, dim_fecha[ANIO])))','0.00' if base=='Razon' else '#,0','Valor del extremo seleccionado; conserva el contexto territorial.')
    for base in ['Accidentes','Muertes','Razon']:
        measures['Cambio '+base.lower()]=(f'IF([Periodo valido] = 1, [{base} fin] - [{base} inicio])','0.00' if base=='Razon' else '#,0','Diferencia final menos inicial; puede ser negativa.')
    for base in ['Accidentes','Muertes']:
        measures['Cambio porcentual '+base.lower()]=(f'DIVIDE([Cambio {base.lower()}], [{base} inicio])','0.0%','Variación relativa; denominador cero devuelve vacío.')
        measure=ACC if base=='Accidentes' else DEAD
        measures['Indice '+base.lower()]=(f'VAR y = SELECTEDVALUE(dim_fecha[ANIO]) RETURN IF([Periodo valido] = 1 && NOT ISBLANK(y) && y >= [Inicio comparacion] && y <= [Fin comparacion], DIVIDE([{measure}], [{base} inicio]) * 100)','0.0','Índice con base 100 en el año inicial; años fuera del intervalo quedan vacíos.')
    measures['Titulo cambios']=('IF([Periodo valido] = 1, "Cambios entre " & FORMAT([Inicio comparacion], "0") & " y " & FORMAT([Fin comparacion], "0"), "Selecciona un año final igual o posterior al inicial")',None,'Título dinámico y aviso para periodos invertidos.')
    source=MODEL/'tables/atus_anual_api.tmdl'
    content=source.read_text(encoding='utf8')
    marker='\t/// INICIO MEDIDAS COMPARACION'
    if marker in content: content=content[:content.index(marker)]
    block='\n'+marker+'\n'
    for name,(expression,fmt,desc) in measures.items():
        block+=f"\t/// {desc}\n\tmeasure '{name}' = {expression}\n"
        if fmt:block+=f'\t\tformatString: {fmt}\n'
        block+=f'\t\tdisplayFolder: Comparaciones\n\t\tlineageTag: {uuid.uuid5(uuid.NAMESPACE_URL,"atus-comparacion/"+name)}\n\n'
    write(source,content+block)

    start('cantidad_gravedad','Cantidad y gravedad','El volumen de accidentes no resume su gravedad registrada')
    sy=slicer(D,'ANIO','Año / periodo',1080,180)
    se=slicer(E,'NOM_ENTIDAD','Entidades para comparar',1270,306)
    obj=deepcopy(templates['lineChart']['visual']['objects'])
    obj.pop('lineStyles',None)
    for axis in ['categoryAxis','valueAxis']:
        obj[axis]=[{'properties':{'start':num(0),'show':boolean(True),'showAxisTitle':boolean(True),'labelColor':color(MUTED)}}]
    obj['legend']=[{'properties':{'show':boolean(False)}}]
    obj['dataPoint']=[{'properties':{'fill':color(BLUE)}}]
    obj['y1AxisReferenceLine']=[{'properties':{'show':boolean(True),'value':{'expr':field(F,'Razon nacional',True)},'lineColor':color(ORANGE),'transparency':num(0)},'selector':{'id':'nacional'}}]
    scatter=put('scatterChart',24,112,940,430,'Cada punto compara volumen y gravedad de una entidad','X: accidentes | Y: muertes / 1,000 accidentes',{'queryState':roles(Category=[proj(E,'NOM_ENTIDAD')],X=[proj(F,ACC,True,'Accidentes')],Y=[proj(F,RATE,True,'Muertes / 1,000 accidentes')],Tooltips=[proj(F,DEAD,True),proj(F,'Razon nacional',True)])},obj)
    reference=card('Razon nacional','Referencia nacional del periodo','muertes / 1,000 accidentes',980,112,596)
    detail=table([(E,'NOM_ENTIDAD'),(F,ACC,True),(F,DEAD,True),(F,RATE,True)],'Selecciona un punto para consultar su detalle','accidentes, personas y muertes / 1,000',980,244,596,298,[200,125,100,140])
    bar1=chart('clusteredBarChart',(E,'NOM_ENTIDAD'),[ACC],'Comparar volumen registrado','accidentes',24,558,768,230)
    bar2=chart('clusteredBarChart',(E,'NOM_ENTIDAD'),[RATE],'Comparar gravedad registrada','muertes / 1,000 accidentes',808,558,768,230)
    textbox('Elige dos entidades para comparar las barras; la dispersión conserva las 32. Clic en un punto: detalle y barras.\nLa razón no es riesgo individual: las diferencias de registro de accidentes leves pueden alterar el denominador.',24,804,1552,58,14)
    finish(enabled=[(scatter,v) for v in (detail,bar1,bar2)],ignored=[(se,scatter),(se,reference)])

    start('cambios_periodo','Cambios entre años','Los cambios en accidentes y muertes pueden ser distintos')
    slicer('Seleccion_Inicio','ANIO','Año inicial',1080,180,2019)
    slicer('Seleccion_Fin','ANIO','Año final',1270,180,2025)
    # El filtro territorial usa espacio propio para no superponer el encabezado.
    ent=slicer(E,'NOM_ENTIDAD','Entidad (todas = nacional)',24,350)
    ent['position'].update(y=94,height=75)
    period=put('cardVisual',390,94,1186,75,'','',{'queryState':roles(Data=[proj(F,'Titulo cambios',True)])},deepcopy(templates['cardVisual']['visual']['objects']))
    period['visual']['objects']['value'][0]['properties'].update(fontSize=num(18),fontColor=color(TEXT))
    period['visual']['objects']['label'][0]['properties']['show']=boolean(False)
    for key in ('title','subTitle'):period['visual']['visualContainerObjects'][key][0]['properties']['show']=boolean(False)
    for i,(m,t,u,dec) in enumerate([
        ('Cambio accidentes','Cambio en accidentes','accidentes',0),('Cambio porcentual accidentes','Variación de accidentes','porcentaje',1),
        ('Cambio muertes','Cambio en muertes','personas',0),('Cambio porcentual muertes','Variación de muertes','porcentaje',1),
        ('Cambio razon','Cambio de la razón','muertes / 1,000 accidentes',2)]):card(m,t,u,24+i*312,184,300,112,dec)
    chart('clusteredBarChart',(E,'NOM_ENTIDAD'),['Cambio muertes'],'Cada entidad contribuye al cambio de muertes','personas | final menos inicial | desplazar para ver las 32',24,312,670,330)
    chart('lineChart',(D,'ANIO'),['Indice accidentes','Indice muertes'],'Una base común compara los cambios relativos','índice: año inicial = 100 | azul: accidentes; naranja: muertes',710,312,866,330)
    table([(E,'NOM_ENTIDAD'),(F,'Accidentes inicio',True),(F,'Accidentes fin',True),(F,'Muertes inicio',True),(F,'Muertes fin',True),(F,'Razon inicio',True),(F,'Razon fin',True)],'Los valores de ambos años permiten verificar los cambios','accidentes, personas y muertes / 1,000',24,658,1552,184,[270,200,200,180,180,180,180])
    finish()
    metadata=read(PAGES/'pages.json')
    metadata['pageOrder']=['8b1a6ac879a0a1740f1b','74eaa1553ef898147305','cantidad_gravedad','cambios_periodo','514e3a3d1cf71f4da7c1']
    metadata['activePageName']=metadata['pageOrder'][0]
    write(PAGES/'pages.json',metadata)
    print('Cinco hojas guardadas. Análisis Territorial y Temporal queda al final.')

if __name__=='__main__': build()
