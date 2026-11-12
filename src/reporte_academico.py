"""Informe académico ATUS original, con figuras vectoriales calculadas del Parquet.

Ejecutar desde la raíz: python src/reporte_academico.py
Requiere requirements.txt y requirements-docs.txt. No consulta la red.
No modifica el informe publicado ni la presentación.
"""
from pathlib import Path
import json
from html import escape
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/reporte_ATUS_API_academico.pdf'
df = pd.read_parquet(ROOT / 'data/processed/atus_anual_api.parquet')
dim = pd.read_parquet(ROOT / 'data/processed/dim_entidad.parquet')
cols = ['ACCIDENTES', 'MUERTOS', 'HERIDOS']
assert len(df) == 928 and not df.duplicated(['CVE_ENT', 'ANIO']).any()
assert not df[cols].isna().any().any() and (df[cols] >= 0).all().all()
assert set(df.ANIO) == set(range(1997, 2026)) and df.CVE_ENT.nunique() == 32
annual = df.groupby('ANIO')[cols].sum()
ent = df.groupby('CVE_ENT')[cols].sum().reset_index().merge(dim, on='CVE_ENT')
ent['RAZON'] = ent.MUERTOS / ent.ACCIDENTES * 1000
tot = df[cols].sum()
national = tot.MUERTOS / tot.ACCIDENTES * 1000
expected = json.loads((ROOT/'docs/hallazgos.json').read_text(encoding='utf8'))
assert all(int(tot[k]) == expected['totales'][k] for k in cols)
for row in expected['anual']:
    assert all(int(annual.loc[row['ANIO'],k]) == row[k] for k in cols)
top = ent.nlargest(5, 'MUERTOS')
share = top.MUERTOS.sum()/tot.MUERTOS*100
W,H = A4
M = 54
CW = W-2*M
NAVY, TEAL, ORANGE, GRAY, LIGHT = '#183349','#087E8B','#AF561C','#475569','#E5EDF1'
c = canvas.Canvas(str(OUT), pagesize=A4)
c.setTitle('ATUS 1997-2025: evolución temporal, distribución territorial y gravedad registrada')
c.setAuthor('Gerardo Pedro Hernández Cruz')
pages = []
def p(s, y, size=11, font='Times-Roman', color=NAVY, x=M, width=CW, leading=None):
    q=Paragraph(s, ParagraphStyle('body', fontName=font,fontSize=size,leading=leading or size*1.42,textColor=HexColor(color),spaceAfter=0))
    _,h=q.wrap(width,1000)
    if y-h < 48: raise ValueError(f'Texto fuera de página: {s[:50]}')
    q.drawOn(c,x,y-h)
    return y-h-10
def label(s,x,y,size=9,color=GRAY,font='Helvetica'):
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,s)
def page(n,section,title):
    if n>1:c.showPage()
    pages.append(title)
    c.setStrokeColor(HexColor(TEAL));c.setLineWidth(1.3);c.line(M,H-53,W-M,H-53)
    label('ATUS / INEGI',M,H-40,8,TEAL,'Helvetica-Bold')
    c.setFont('Helvetica',8);c.setFillColor(HexColor(GRAY));c.drawRightString(W-M,H-40,section.upper())
    c.setStrokeColor(HexColor(LIGHT));c.line(M,42,W-M,42)
    label('Cómputo Científico · Doctorado en Ingeniería Física · UANL',M,28,7.5)
    c.drawRightString(W-M,28,f'{n:02d}')
    return p(title,H-75,23,'Helvetica-Bold',leading=27)-12
def sub(s,y):return p(s,y,13,'Helvetica-Bold',TEAL)
def table(rows,y,widths):
    data=[[Paragraph(str(v),ParagraphStyle('cell',fontName='Helvetica-Bold' if i==0 else 'Helvetica',fontSize=9,leading=12,textColor=HexColor('#FFFFFF' if i==0 else NAVY))) for v in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(NAVY)),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#F0F5F7'),HexColor('#FFFFFF')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,-1),(-1,-1),.5,HexColor(LIGHT))]))
    _,h=t.wrap(CW,1000)
    if y-h<55:raise ValueError('Tabla demasiado larga')
    t.drawOn(c,M,y-h);return y-h-16
def caption(num,s,y):
    y=p(f'<b>Figura {num}.</b> {s}',y,9,'Helvetica',GRAY,leading=12)
    return p('Fuente: elaboración propia con API ATUS / INEGI, 1997-2025. Licencia de datos: libre uso INEGI [3].',y,8,'Helvetica',GRAY,leading=11)
def chart(y,height,xmin,xmax,ymax,xticks,yticks,unit):
    left=M+46;right=W-M-8;bottom=y-height
    label(unit,M,y+18,9,NAVY,'Helvetica-Bold')
    for v in yticks:
        yy=bottom+height*v/ymax
        c.setStrokeColor(HexColor(LIGHT));c.setLineWidth(.6);c.line(left,yy,right,yy)
        c.setFont('Helvetica',8);c.setFillColor(HexColor(GRAY));c.drawRightString(left-8,yy-3,f'{v:,.0f}')
    for v,txt in xticks:
        xx=left+(v-xmin)/(xmax-xmin)*(right-left)
        c.setFont('Helvetica',8);c.setFillColor(HexColor(GRAY));c.drawCentredString(xx,bottom-16,txt)
    return (lambda x:left+(x-xmin)/(xmax-xmin)*(right-left)),(lambda v:bottom+height*v/ymax),bottom
def line(xs,ys,fx,fy,color=TEAL,dashed=False,markers=False):
    c.setStrokeColor(HexColor(color));c.setLineWidth(1.8);c.setDash(5,3) if dashed else c.setDash()
    path=c.beginPath();path.moveTo(fx(xs[0]),fy(ys[0]))
    for x,y in zip(xs[1:],ys[1:]):path.lineTo(fx(x),fy(y))
    c.drawPath(path);c.setDash()
    if markers:
        c.setFillColor(HexColor(color))
        for x,y in zip(xs,ys):c.circle(fx(x),fy(y),2.3,fill=1,stroke=0)
def fmt(v):return f'{int(v):,}'

# Portada tipográfica original. No se reutilizan imágenes del documento de referencia.
y=page(1,'Producto Integrador de Aprendizaje','')
y=p('UNIVERSIDAD AUTÓNOMA DE NUEVO LEÓN',H-112,12,'Helvetica-Bold')
y=p('Facultad de Ciencias Físico Matemáticas<br/>Doctorado en Ingeniería Física',y,12,'Helvetica')
y=p('INFORME ACADÉMICO',H-230,10,'Helvetica-Bold',TEAL)
y=p('Accidentes de tránsito en zonas urbanas y suburbanas de México',y-8,30,'Times-Bold',leading=35)
y=p('Evolución temporal y distribución territorial desde una API real',y-6,17,'Helvetica',GRAY,leading=23)
y=p('1997-2025',y-12,29,'Helvetica-Bold',TEAL)
y=p('Cantidad de accidentes y gravedad registrada',y-12,12,'Helvetica')
y=p('<b>M. C. Gerardo Pedro Hernández Cruz</b><br/>Cómputo Científico (D06)<br/>Docente: Dr. Guillermo Ezequiel Sánchez Guerrero',225,11,'Helvetica',leading=18)
p('Noviembre de 2026',112,11,'Helvetica')

y=page(2,'Resumen y contenido','Una lectura conjunta de cantidad y gravedad')
y=sub('Resumen',y)
y=p(f'Se analizan los indicadores anuales de accidentes de tránsito terrestre en zonas urbanas y suburbanas (ATUS) del INEGI para las 32 entidades de México entre 1997 y 2025. El conjunto contiene 928 registros de entidad-año y se obtiene mediante la API del Banco de Indicadores. Python conserva las respuestas JSON y prepara archivos Parquet; Power BI organiza la exploración temporal y territorial.',y)
y=p(f'El acumulado comprende {fmt(tot.ACCIDENTES)} accidentes, {fmt(tot.MUERTOS)} personas muertas en el lugar y {fmt(tot.HERIDOS)} heridas. La razón nacional es de {national:.2f} muertes por 1,000 accidentes. Las muertes disminuyen 48.4 % entre 2011 y 2019 y aumentan 10.8 % entre 2019 y 2025. En este último periodo, los accidentes aumentan 4.9 %. Cinco entidades concentran {share:.1f} % de las muertes acumuladas.',y)
y=p('La cantidad de accidentes y la razón de muertes por accidente aportan información distinta. Su lectura conjunta permite describir la gravedad registrada, pero no estimar el riesgo individual ni atribuir diferencias a la infraestructura sin mediciones adicionales.',y)
y=p('<b>Palabras clave:</b> ATUS, INEGI, API, reproducibilidad, Power BI, gravedad registrada.',y,9,'Helvetica',GRAY)
y=sub('Contenido',y-8)
rows=[['Apartado','Página'],['1. Pregunta, propósito y datos','3'],['2. Flujo reproducible en Python','4'],['3. Modelo y medidas en Power BI','5'],['4. Validación de los cálculos','6'],['5. Resultados: evolución temporal','7'],['6. Resultados: cantidad y gravedad','8'],['7. Resultados: cambios entre años','9'],['8. Resultados: concentración territorial','10'],['9. Discusión, límites y siguiente paso','11'],['10. Conclusiones y referencias','12']]
table(rows,y,[CW-65,65])

y=page(3,'1 / Pregunta y datos','El análisis distingue volumen y gravedad registrada')
y=sub('Pregunta científica',y)
y=p('¿Cómo han cambiado las muertes por accidentes de tránsito urbanos y suburbanos en México entre 1997 y 2025 y en qué entidades se concentran?',y,13,'Times-Bold')
y=sub('Gran idea',y)
y=p('La prevención debe enfocarse no solo en reducir la cantidad de accidentes, sino también en su gravedad, considerando la evolución de las muertes y su distribución territorial.',y,12,'Times-Bold')
y=sub('Propósito y alcance',y)
y=p('El objetivo es describir la evolución de las muertes y su distribución territorial, contrastando los conteos con las muertes por cada 1,000 accidentes registrados. Se construye una cadena trazable de consulta, transformación, cálculo y visualización. El estudio es descriptivo, con unidad de observación entidad-año; no representa expedientes individuales ni un diseño causal.',y)
y=p('La fuente es ATUS [1], consultada a través de la API del Banco de Indicadores [2]. Se conserva la edición descargada en el repositorio. Las cifras del informe corresponden a esa copia y no a una consulta que se actualice al abrir el PDF.',y)
y=table([['Variable','ID de la API','Unidad'],['Accidentes','1006000039','Accidentes'],['Víctimas muertas','6200009438','Personas'],['Víctimas heridas','6200009439','Personas']],y,[205,120,CW-325])
y=p('<b>Tabla 1.</b> Indicadores consultados. Fuente: configuración del proyecto y API del INEGI. Licencia: libre uso INEGI [3].',y,8.5,'Helvetica',GRAY)
y=sub('Cobertura analítica',y)
p('32 entidades × 29 años = 928 registros. El código nacional 00 se usa como control independiente y no se agrega nuevamente a las entidades. La fecha técnica del 1 de enero representa el año del registro, no el día de ocurrencia del accidente.',y)

y=page(4,'2 / Método','El flujo conserva los datos y su procedencia')
y=p('La configuración define los tres indicadores, las entidades y el periodo. El script src/atus_api.py consulta la serie histórica en español y guarda cada respuesta con metadatos. El token se lee de una variable de entorno o de un archivo local excluido del repositorio.',y)
steps=[('01','Consulta','API del INEGI, indicadores y catálogos'),('02','Conservación','JSON originales y huella SHA-256 en data/raw'),('03','Transformación','Tipos, claves, cobertura y unión por entidad-año'),('04','Exportación','Parquet y metadatos de procedencia'),('05','Análisis','pandas, medidas DAX y reporte Power BI')]
for num,name,desc in steps:
    c.setFillColor(HexColor('#F0F5F7'));c.roundRect(M,y-48,CW,48,5,fill=1,stroke=0)
    label(num,M+12,y-29,17,TEAL,'Helvetica-Bold')
    p(f'<b>{name}</b> · {desc}',y-12,10,'Helvetica',x=M+55,width=CW-70)
    y-=61
y=caption(1,'Flujo de procesamiento del proyecto. Esquema original a partir de src/atus_api.py; la numeración indica la secuencia de procesamiento.',y)
y=sub('Controles de preparación',y)
y=p('Se comprueban claves únicas, cobertura de los 29 años y 32 entidades, conteos enteros y valores ausentes. Las ausencias no se reemplazan por cero. La huella SHA-256 permite detectar cambios en las respuestas conservadas. Los Parquet contienen procedencia y mantienen las claves de entidad como texto de dos dígitos.',y)
y=sub('Reproducción',y)
y=p('<font face="Courier">python src/atus_api.py</font><br/>Consulta la API y genera los Parquet con la configuración del proyecto.<br/><font face="Courier">python src/atus_api.py --offline</font><br/>Reconstruye los datos desde los JSON conservados, sin red ni token.',y,10)
p('La modalidad offline reproduce la edición analizada. Una descarga nueva puede incorporar revisiones del proveedor y debe conservarse como otra edición.',y,10)

y=page(5,'3 / Modelo analítico','El modelo separa hechos, fechas y entidades')
y=p('El proyecto ATUS_API_Profesional.pbip utiliza un modelo en estrella. La tabla de hechos contiene los conteos; las dimensiones aportan el calendario y los nombres territoriales. Las relaciones son de uno a muchos, con propagación del filtro desde las dimensiones hacia los hechos.',y)
y=table([['Tabla','Función y relación'],['dim_fecha','Calendario continuo, marcado como tabla de fechas. FECHA (1) a FECHA (*) de los hechos.'],['dim_entidad','Catálogo de entidades. CVE_ENT (1) a CVE_ENT (*) de los hechos.'],['atus_anual_api','928 filas entidad-año. ACCIDENTES, MUERTOS y HERIDOS.'],['Tablas auxiliares','Seleccion_Inicio, Seleccion_Fin y dim_tipo_victima están desconectadas.'] ],y,[145,CW-145])
y=p('<b>Tabla 2.</b> Estructura del modelo. Fuente: definiciones TMDL del proyecto; código con licencia MIT. Las relaciones no se infieren a partir de las figuras.',y,8.5,'Helvetica',GRAY)
y=sub('Medidas explícitas',y)
code='Total de Accidentes = SUM(atus_anual_api[ACCIDENTES])\nTotal de Muertos = SUM(atus_anual_api[MUERTOS])\nTotal de Heridos = SUM(atus_anual_api[HERIDOS])\nMuertos por 1000 accidentes =\n    DIVIDE([Total de Muertos], [Total de Accidentes]) * 1000'
y=p('<font face="Courier">'+escape(code).replace('\n','<br/>')+'</font>',y,8.8,leading=14)
y=p('La razón se calcula sobre las sumas del contexto seleccionado. No se promedian razones estatales. DIVIDE devuelve un valor vacío si no existe un denominador válido. El parámetro RutaDatos permite trasladar el proyecto a otra computadora.',y)
y=sub('Lectura del reporte interactivo',y)
p('Las cinco páginas son Resumen Ejecutivo y Geografía, Distribución y Víctimas, Cantidad y gravedad, Cambios entre años y Análisis Territorial y Temporal. Las comparaciones usan dos selectores desconectados. Las series que conservan todos los años explicitan esa excepción al filtro de año; el filtro de entidad continúa aplicándose.',y)

y=page(6,'4 / Validación','Las sumas coinciden con el control nacional')
y=p('La validación distingue el cálculo de los indicadores y su presentación. Para los conteos, el flujo compara la suma estatal de cada año con la serie nacional descargada por separado. Son 87 contrastes: tres variables por 29 años. La coincidencia comprueba consistencia aritmética dentro de la fuente; no demuestra ausencia de subregistro.',y)
y=table([['Medida','Equivalente en pandas','Valor nacional'],['Accidentes','df.ACCIDENTES.sum()',fmt(tot.ACCIDENTES)],['Muertes','df.MUERTOS.sum()',fmt(tot.MUERTOS)],['Heridos','df.HERIDOS.sum()',fmt(tot.HERIDOS)],['Muertes por 1,000','sum(MUERTOS) /\nsum(ACCIDENTES) × 1,000',f'{national:.4f}']],y,[115,222,CW-337])
y=p('<b>Tabla 3.</b> Valores de control para el contexto nacional completo, 1997-2025. Accidentes y personas en las primeras tres filas; personas por 1,000 accidentes en la cuarta. Fuente: Parquet ATUS / INEGI; libre uso [3].',y,8.5,'Helvetica',GRAY)
y=sub('Comprobación por entidad',y)
code='resumen = df.groupby("CVE_ENT")[\n    ["ACCIDENTES", "MUERTOS"]\n].sum()\nden = resumen.ACCIDENTES.replace(0, float("nan"))\nresumen["RAZON"] = resumen.MUERTOS / den * 1000'
y=p('<font face="Courier">'+escape(code).replace('\n','<br/>')+'</font>',y,9,leading=14)
y=p('El mismo filtro debe aplicarse en ambas herramientas antes de comparar una tarjeta o una tabla. Por ejemplo, al seleccionar una entidad y un intervalo, pandas debe restringirse a esa entidad y esos años. La razón nacional no es la media de la columna RAZON.',y)
y=sub('Alcance de la evidencia',y)
y=p('El control src/validar_comparaciones.py documenta 435 pares de años, diferencias aditivas, extremos iguales y denominadores cero. Los resultados se conservan en docs/validacion_comparaciones.json. Esta evidencia procede de pandas; no constituye una nueva ejecución de las medidas DAX en Power BI Desktop.',y)
p('La revisión manual del PBIP debe contrastar tarjetas y filtros con estos valores. El informe no atribuye al motor DAX verificaciones realizadas únicamente en Python.',y,10,'Times-Italic')

y=page(7,'5 / Resultados temporales','Las muertes bajaron 48% de 2011 a 2019')
y=p('El descenso entre 2011 y 2019 no describe toda la trayectoria. La serie alcanza 7,994 muertes en 2011, registra 4,127 en 2019 y cierra 2025 con 4,571. Este último valor supera al de 2019 en 444 personas, equivalentes a 10.8 %. El comportamiento anual no es monotónico.',y)
fx,fy,b=chart(y-27,175,1997,2025,9000,[(v,str(v)) for v in [1997,2004,2011,2019,2025]],[0,3000,6000,9000],'Personas muertas en el lugar del accidente')
line(list(annual.index),list(annual.MUERTOS),fx,fy)
for year in [2011,2019,2025]:
    c.setFillColor(HexColor(TEAL));c.circle(fx(year),fy(annual.loc[year,'MUERTOS']),3,fill=1,stroke=0)
y=caption(2,'Muertes registradas por año. Los puntos destacados corresponden a 2011, 2019 y 2025. Eje horizontal: año; eje vertical: personas.',b-33)
fx,fy,b=chart(y-35,145,1997,2025,30,[(v,str(v)) for v in [1997,2004,2011,2019,2025]],[0,10,20,30],'Muertes por 1,000 accidentes registrados')
line(list(annual.index),list(annual.MUERTOS/annual.ACCIDENTES*1000),fx,fy,ORANGE)
y=caption(3,'Razón anual calculada con los totales nacionales. Es un cociente de personas y accidentes registrados, no una tasa por población.',b-33)
p('La razón pasa de 24.34 en 1997 a 11.38 en 2019 y 12.02 en 2025. El descenso del cociente puede reflejar cambios tanto en las muertes como en el volumen o registro de accidentes. Las dos figuras usan escalas separadas y explícitas, sin doble eje.',y)

y=page(8,'6 / Cantidad y gravedad','Más accidentes no implica una mayor razón de muertes')
y=p('Cada entidad combina un volumen de accidentes y una razón de muertes por accidente. Compararlas en un plano permite distinguir concentración de incidentes y gravedad registrada sin convertir ninguno de esos indicadores en una medida de riesgo individual.',y)
fx,fy,b=chart(y-30,205,0,2.2,40,[(v,str(v)) for v in [0,.5,1,1.5,2]],[0,10,20,30,40],'Muertes por 1,000 accidentes registrados')
c.setDash(4,3);c.setStrokeColor(HexColor(GRAY));c.setLineWidth(.8);c.line(fx(0),fy(national),fx(2.2),fy(national));c.setDash()
for _,r in ent.iterrows():
    x=fx(r.ACCIDENTES/1e6);yy=fy(r.RAZON);c.setFillColor(HexColor(ORANGE if r.CVE_ENT=='19' else TEAL));c.circle(x,yy,3,fill=1,stroke=0)
for key,txt,dx,dy in [('19','Nuevo León',-61,12),('25','Sinaloa',8,8),('14','Jalisco',8,-10)]:
    r=ent[ent.CVE_ENT==key].iloc[0];label(txt,fx(r.ACCIDENTES/1e6)+dx,fy(r.RAZON)+dy,8,NAVY)
label('Referencia nacional: 14.01',fx(1.35),fy(national)+7,8)
label('Accidentes acumulados (millones)',M+165,b-35,9)
y=caption(4,'Dispersión de las 32 entidades, acumulado 1997-2025. Cada punto tiene el mismo tamaño. Línea discontinua: razón nacional, calculada con las sumas.',b-53)
y=table([['Entidad','Accidentes','Muertes por 1,000']]+[[name,fmt(ent[ent.CVE_ENT==key].iloc[0].ACCIDENTES),f'{ent[ent.CVE_ENT==key].iloc[0].RAZON:.2f}'] for key,name in [('19','Nuevo León'),('25','Sinaloa'),('14','Jalisco')]],y,[165,145,CW-310])
y=p('<b>Tabla 4.</b> Tres casos de contraste de la figura 4. Fuente: ATUS / INEGI; libre uso [3].',y,8.5,'Helvetica',GRAY)
p('Nuevo León acumula el mayor número de accidentes, con una razón de 3.68 por mil. Sinaloa registra 279,209 accidentes y una razón de 31.04, frente a 1,062,253 y 12.39 en Jalisco: aproximadamente 2.5 veces la razón, con menor volumen. Este contraste no demuestra que una entidad sea más segura que otra.',y)

y=page(9,'7 / Comparación de periodos','Las muertes crecieron más que los accidentes de 2019 a 2025')
y=p('Una base común de 100 en 2019 permite comparar cambios relativos entre variables con magnitudes distintas. El índice se define como 100 × valor del año / valor de 2019. Una distancia de diez puntos sobre la base equivale a un aumento de 10 % respecto de ese año.',y)
sel=annual.loc[2019:2025]
fx,fy,b=chart(y-30,185,2019,2025,140,[(v,str(v)) for v in sel.index],[0,40,80,100,140],'Índice nacional (2019 = 100)')
line(list(sel.index),list(sel.ACCIDENTES/sel.loc[2019,'ACCIDENTES']*100),fx,fy,TEAL,markers=True)
line(list(sel.index),list(sel.MUERTOS/sel.loc[2019,'MUERTOS']*100),fx,fy,ORANGE,True,True)
label('Accidentes: línea continua',M+25,b-38,9,TEAL);label('Muertes: línea discontinua',M+255,b-38,9,ORANGE)
y=caption(5,'Evolución relativa de accidentes y muertes. Eje horizontal: año; eje vertical: índice sin unidades, con una sola escala para ambas series.',b-57)
rows=[['Indicador','2019','2025','Cambio']]
for key,name in [('ACCIDENTES','Accidentes'),('MUERTOS','Muertes')]:
    a=int(sel.loc[2019,key]);z=int(sel.loc[2025,key]);rows.append([name,fmt(a),fmt(z),f'+{fmt(z-a)}<br/>+{(z/a-1)*100:.2f} %'])
y=table(rows,y,[130,110,110,CW-350])
y=p('<b>Tabla 5.</b> Accidentes y personas muertas; diferencias absolutas y relativas entre los extremos. Fuente: ATUS / INEGI; libre uso [3].',y,8.5,'Helvetica',GRAY)
p('La razón aumenta de 11.38 a 12.02 muertes por 1,000 accidentes, una diferencia de 0.64 por mil. El balance de extremos no implica crecimiento continuo: las dos curvas muestran oscilaciones. El reporte interactivo permite elegir otros años para evitar que una sola comparación se interprete como descripción de todo el periodo.',y)

y=page(10,'8 / Distribución territorial','Cinco entidades concentran el 37.3% de las muertes')
y=p('México, Jalisco, Chihuahua, Sinaloa y Michoacán de Ocampo reúnen 57,423 de las 154,152 muertes acumuladas. La concentración identifica dónde se registra una parte importante del total; no indica la probabilidad de morir al viajar ni la situación actual de cada entidad.',y)
left=M+120;right=W-M-32;topY=y-30;barw=right-left
label('Personas muertas, acumulado 1997-2025',M,topY+14,9,NAVY,'Helvetica-Bold')
for tick in [0,5000,10000,15000]:
    xx=left+tick/18000*barw;c.setStrokeColor(HexColor(LIGHT));c.line(xx,topY-205,xx,topY)
    label(f'{tick:,}',xx-12,topY-223,8)
for i,(_,r) in enumerate(top.iterrows()):
    yy=topY-22-i*40;c.setFillColor(HexColor(TEAL));c.rect(left,yy-8,r.MUERTOS/18000*barw,17,fill=1,stroke=0)
    label(r.NOM_ENTIDAD.replace(' de Ocampo',''),M,yy-3,9,NAVY)
    label(fmt(r.MUERTOS),left+r.MUERTOS/18000*barw+5,yy-3,8,NAVY)
y=caption(6,'Cinco entidades con mayor número acumulado de muertes. Barras con origen en cero; las etiquetas permiten leer los valores sin depender del color.',topY-245)
y=sub('Concentración y razón responden preguntas distintas',y)
y=p('Un territorio puede aportar muchas muertes por su volumen de accidentes, por una razón elevada o por ambas condiciones. Por eso el orden de esta figura no sustituye a la dispersión de la figura 4. La concentración es una participación del total; la razón usa los accidentes registrados como denominador.',y)
y=p('El acumulado de 29 años resume la carga registrada durante todo el periodo. No debe usarse como ranking de desempeño reciente. Para estudiar cambios actuales, es necesario restringir años y observar diferencias absolutas junto con sus bases de comparación.',y)
y=sub('Vínculo con Power BI',y)
p('El mapa sirve para seleccionar entidades y situarlas geográficamente. Las tablas y las barras permiten verificar los valores con precisión; la matriz entidad-año permite seguir la trayectoria. La lectura territorial se apoya en estas vistas complementarias y no en el tamaño visual del estado en el mapa.',y)

y=page(11,'9 / Discusión','Los registros describen patrones, no causas')
y=sub('Interpretación de los resultados',y)
y=p('El descenso hasta 2019, el aumento posterior y la heterogeneidad territorial sustentan una lectura conjunta de cantidad y gravedad. La razón incorpora una dimensión que el conteo de accidentes no muestra por sí solo, pero su denominador también depende del registro. Por ello, su utilidad es descriptiva y comparativa bajo las limitaciones de la fuente.',y)
y=table([['Limitación','Consecuencia para la interpretación'],['Muertes en el lugar','No representa mortalidad a 30 días ni permite conocer todas las consecuencias posteriores.'],['Ausencia de exposición','Sin viajes, población expuesta o kilómetros recorridos no se calcula riesgo individual.'],['Registro de accidentes leves','Un menor registro del denominador puede elevar la razón aun sin cambios equivalentes en la gravedad real.'],['Agregación entidad-año','No identifica horarios, domingos, tipos de choque, fuga, cruces ni corredores concretos.'],['Cobertura y revisiones','Las notas de la fuente y su edición condicionan las comparaciones temporales y territoriales.']],y,[145,CW-145])
y=p('<b>Tabla 6.</b> Límites de interpretación del conjunto analizado. Elaboración propia a partir del alcance de las variables y de la documentación del proyecto.',y,8.5,'Helvetica',GRAY)
y=sub('Siguiente paso: infraestructura y exposición',y)
y=p('Un estudio local puede seleccionar corredores, georreferenciar accidentes y medir aforos, velocidades, geometría, iluminación y protección peatonal. Esas variables permitirían formular hipótesis físicas y contrastar si los conflictos y las consecuencias cambian con las condiciones de la vía.',y)
p('Para evaluar una intervención se propone un diseño antes-después con corredores comparables, periodos equivalentes, control de cambios en la exposición y atención a la regresión a la media. Es una propuesta de investigación: estos mecanismos no se han medido ni demostrado con los agregados estatales del presente informe.',y)

y=page(12,'10 / Cierre y referencias','La prevención debe considerar cantidad y gravedad')
y=sub('Conclusiones',y)
y=p('Las muertes registradas disminuyeron entre 2011 y 2019, pero el cierre de 2025 supera al de 2019. En ese intervalo reciente, las muertes crecen proporcionalmente más que los accidentes. Territorialmente, cinco entidades concentran 37.3 % de las muertes acumuladas y el orden por volumen de accidentes difiere del orden por razón de muertes.',y)
y=p('La prevención debe enfocarse no solo en reducir la cantidad de accidentes, sino también en su gravedad, considerando la evolución de las muertes y su distribución territorial. Los indicadores permiten formular prioridades de estudio; las decisiones sobre infraestructura requieren información local y exposición comparable.',y)
y=sub('Referencias y materiales reproducibles',y)
refs=[('[1] INEGI. Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas (ATUS).','https://www.inegi.org.mx/programas/accidentes/'),('[2] INEGI. API del Banco de Indicadores. Documentación de consultas y catálogos.','https://www.inegi.org.mx/servicios/api-indicadores/'),('[3] INEGI. Términos de uso y libre uso de la información.','https://www.inegi.org.mx/inegi/terminos.html'),('[4] Hernández Cruz, G. P. Repositorio del PIA: código, datos, modelo y evidencias.','https://github.com/Gerar93Dot/Computo-cientifico-ok')]
for title,url in refs:
    y=p(escape(title)+'<br/><link href="'+url+'" color="'+TEAL+'">'+url+'</link>',y,9.5,'Helvetica',leading=13)
y=p('Referencias web consultadas el 12 de noviembre de 2026. Los análisis corresponden a la edición de los datos conservada en data/raw y documentada en data/processed/procedencia.json.',y,9,'Helvetica',GRAY)
y=sub('Archivos de cálculo',y)
y=p('src/atus_api.py: consulta y preparación.<br/>src/analisis.py: hallazgos del conjunto procesado.<br/>src/validar_comparaciones.py: control de cambios entre años.<br/>src/reporte_academico.py: este informe y sus figuras desde los Parquet.<br/>reportes/ATUS_API_Profesional.pbip: modelo y reporte interactivo.',y,9.5,'Helvetica',leading=14)
y=sub('Autoría y herramientas',y)
p('Se empleó asistencia de IA para implementación y revisión editorial. La interpretación y defensa académica corresponden al autor. Las figuras son elaboraciones del proyecto a partir de los datos del INEGI; no representan una interpretación oficial del Instituto. El código usa licencia MIT y los datos mantienen los términos de libre uso del INEGI.',y,9.5)
c.save()
print(json.dumps({'output':str(OUT),'pages':len(pages),'records':len(df),'totals':{k:int(tot[k]) for k in cols},'national_ratio':float(national)},ensure_ascii=False))



