"""Reporte de lectura complementario al PBIP, generado desde hallazgos.json."""
import json
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics import renderPDF

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / 'docs/hallazgos.json').read_text(encoding='utf8'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=ROOT / 'docs/reporte_ATUS_API.pdf', help='Ruta del PDF de salida.')
OUT = parser.parse_args().output
OUT.parent.mkdir(parents=True, exist_ok=True)
c = canvas.Canvas(str(OUT), pagesize=(842, 595))
c.setTitle('ATUS: evolución temporal y distribución territorial, 1997-2025')
c.setAuthor('Gerardo Pedro Hernández Cruz')
navy, teal, gray = '#12263A', '#087E8B', '#475569'
def text(value, x, y, width=740, size=12, color=navy, bold=False):
    p = Paragraph(value, ParagraphStyle('p', fontName='Helvetica-Bold' if bold else 'Helvetica', fontSize=size, leading=size*1.32, textColor=HexColor(color)))
    _, h = p.wrap(width, 500)
    p.drawOn(c, x, y-h)
    return y-h

def base(number, title):
    c.setFillColor(HexColor(navy)); c.rect(0, 522, 842, 73, fill=1, stroke=0)
    text('ATUS / INEGI · CÓMPUTO CIENTÍFICO · FCFM-UANL',42,578,760,10,'#FFFFFF')
    text(title,42,558,760,22,'#FFFFFF',True)
    text('Fuente: API de indicadores INEGI, ATUS. Zonas urbanas y suburbanas. Edición conservada en data/raw.',42,38,760,8,gray)
    text('Licencia de datos: https://www.inegi.org.mx/inegi/terminos.html · Cálculos reproducibles con pandas.',42,25,740,8,gray)
    c.setFont('Helvetica',9); c.setFillColor(HexColor(gray)); c.drawRightString(800,16,str(number))

def line_chart(key, x, y, width, height, maximum, ticks, unit):
    # Ejes parten de cero; no hay un segundo eje.
    records=d['anual']; left=x+48; bottom=y; right=x+width
    c.setFont('Helvetica',9)
    for tick in ticks:
        yy=bottom+height*tick/maximum
        c.setStrokeColor(HexColor('#E2E8F0')); c.line(left,yy,right,yy)
        c.setFillColor(HexColor(gray)); c.drawRightString(left-8,yy-3,f'{tick:,.0f}')
    points=[(left+(r['ANIO']-1997)/28*(width-48),bottom+r[key]/maximum*height) for r in records]
    p=c.beginPath(); p.moveTo(*points[0])
    for point in points[1:]:p.lineTo(*point)
    c.setStrokeColor(HexColor(teal)); c.setLineWidth(2.2); c.drawPath(p)
    for year in [1997,2004,2011,2019,2025]:
        xx=left+(year-1997)/28*(width-48)
        c.setFillColor(HexColor(gray)); c.drawCentredString(xx,bottom-17,str(year))
    text(unit,left,y+height+22,width-48,9,gray)

base(1,'Muertes registradas: evolución temporal y territorial')
text('Pregunta',42,500,160,11,teal,True)
text('¿Cómo han cambiado las muertes por accidentes de tránsito urbanos en México entre 1997 y 2025 y en qué entidades se concentran?',42,480,750,17,navy,True)
text('Gran idea',42,418,750,11,teal,True)
text('La prevención debe enfocarse no solo en reducir la cantidad de accidentes, sino también en su gravedad, considerando la evolución de las muertes y su distribución territorial.',42,398,750,15)
values=[('10,999,723','accidentes registrados'),('154,152','personas muertas'),('3,347,199','personas heridas'),('14.0','muertos por 1,000 accidentes')]
for i,(value,label) in enumerate(values):
    xx=42+i*196
    text(value,xx,320,185,26,teal,True);text(label,xx,278,185,11)
text('Alcance del análisis',42,230,750,14,navy,True)
text('Los indicadores contienen 928 registros agregados: 32 entidades durante 29 años. El análisis describe la evolución anual de las muertes y su distribución territorial mediante conteos y razones. La unidad de observación es la entidad-año; no incluye circunstancias individuales de los accidentes.',42,205,750,12)
text('Fuente y validación',42,139,750,12,navy,True)
text('Los datos proceden de la API del Banco de Indicadores del INEGI. La suma de las 32 entidades coincide con la serie nacional en los tres indicadores para cada año: 87 comprobaciones. El acumulado del período comprende 154,152 personas muertas.',42,117,750,11)
c.showPage()

base(2,'Las muertes bajaron 48% de 2011 a 2019')
text('El cierre de 2025 supera al de 2019 en 10.8 %',42,501,750,15,teal,True)
line_chart('MUERTOS',42,285,750,150,9000,[0,3000,6000,9000],'Personas muertas en el lugar del accidente, por año')
text('2011: 7,994 muertes   ·   2019: 4,127   ·   2025: 4,571',90,253,700,12,navy,True)
line_chart('MUERTOS_POR_1000',42,98,750,105,30,[0,10,20,30],'Personas muertas por cada 1,000 accidentes registrados')
text('La razón pasa de 24.3 en 1997 a 11.4 en 2019 y 12.0 en 2025. Cada gráfico tiene una sola escala.',90,68,700,10)
c.showPage()

base(3,'Más accidentes no implica una mayor razón de muertes')
text('32 entidades, acumulado 1997-2025',42,500,750,15,teal,True)
text('X: millones de accidentes · Y: muertes por 1,000 accidentes · Un punto por entidad',42,477,750,10)
entities=d['entidades']; nl=next(r for r in entities if r['CVE_ENT']=='19')
others=[r for r in entities if r['CVE_ENT']!='19']
ratio=lambda r:r['MUERTOS']/r['ACCIDENTES']*1000
drawing=Drawing(750,235); scatter=LinePlot()
scatter.x=48;scatter.y=25;scatter.width=680;scatter.height=195
scatter.data=[[(r['ACCIDENTES']/1e6,ratio(r)) for r in others],[(nl['ACCIDENTES']/1e6,ratio(nl))]]
scatter.xValueAxis.valueMin=0;scatter.xValueAxis.valueMax=2.2;scatter.xValueAxis.valueSteps=[0,0.5,1,1.5,2]
scatter.yValueAxis.valueMin=0;scatter.yValueAxis.valueMax=40;scatter.yValueAxis.valueSteps=[0,10,20,30,40]
for axis in (scatter.xValueAxis,scatter.yValueAxis):
    axis.labels.fontSize=9;axis.labels.fillColor=HexColor(gray);axis.strokeColor=HexColor('#CBD5E1');axis.labelTextFormat='%g'
scatter.yValueAxis.visibleGrid=True;scatter.yValueAxis.gridStrokeColor=HexColor('#E2E8F0')
for i,col in enumerate([teal,'#B45309']):
    marker=makeMarker('Diamond' if i else 'Circle');marker.size=5;marker.fillColor=HexColor(col);marker.strokeColor=HexColor(col)
    scatter.lines[i].strokeColor=None;scatter.lines[i].symbol=marker
drawing.add(scatter);renderPDF.draw(drawing,c,42,235)
text('Diamante naranja: Nuevo León; círculos azules: otras entidades. Referencia nacional: 14.01 por mil.',90,230,700,9)
text('Fuente: INEGI, API ATUS · Libre uso: inegi.org.mx/inegi/terminos.html',90,213,700,8,gray)
text('Nuevo León lidera en accidentes y queda por debajo de la razón nacional',42,184,750,14,teal,True)
text(f"Acumula {nl['ACCIDENTES']:,} accidentes y {nl['MUERTOS']:,} muertes: {ratio(nl):.2f} por mil. El volumen no determina el orden de las razones registradas.",42,160,750,12)
ja=next(r for r in entities if r['CVE_ENT']=='14');si=next(r for r in entities if r['CVE_ENT']=='25')
text(f"Sinaloa registra {si['ACCIDENTES']:,} accidentes y {ratio(si):.2f} muertes por mil; Jalisco, {ja['ACCIDENTES']:,} y {ratio(ja):.2f}. Sinaloa tiene menos accidentes y una razón {ratio(si)/ratio(ja):.1f} veces mayor.",42,112,750,12)
text('La razón describe el registro: sin exposición y cobertura comparable no identifica la entidad más segura.',42,64,750,10,gray)
c.showPage()

base(4,'Las muertes crecieron más que los accidentes de 2019 a 2025')
text('Índice nacional: 2019 = 100 · Ambas series comparten un solo eje',42,500,750,13,teal,True)
recent=[r for r in d['anual'] if r['ANIO']>=2019];start=recent[0];end=recent[-1]
drawing=Drawing(750,260);lines=LinePlot();lines.x=48;lines.y=25;lines.width=680;lines.height=220
lines.data=[[(r['ANIO'],r[k]/start[k]*100) for r in recent] for k in ('ACCIDENTES','MUERTOS')]
lines.xValueAxis.valueMin=2019;lines.xValueAxis.valueMax=2025;lines.xValueAxis.valueSteps=list(range(2019,2026))
lines.yValueAxis.valueMin=0;lines.yValueAxis.valueMax=140;lines.yValueAxis.valueSteps=[0,40,80,100,140]
for axis in (lines.xValueAxis,lines.yValueAxis):
    axis.labels.fontSize=9;axis.labels.fillColor=HexColor(gray);axis.strokeColor=HexColor('#CBD5E1');axis.labelTextFormat='%g'
lines.yValueAxis.visibleGrid=True;lines.yValueAxis.gridStrokeColor=HexColor('#E2E8F0')
for i,col in enumerate([teal,'#B45309']):lines.lines[i].strokeColor=HexColor(col);lines.lines[i].strokeWidth=2
drawing.add(lines);renderPDF.draw(drawing,c,42,207)
text('Azul: accidentes · Naranja: muertes · Fuente: API ATUS / INEGI · Libre uso INEGI',90,204,700,9,gray)
for i,(k,label) in enumerate([('ACCIDENTES','Accidentes'),('MUERTOS','Muertes')]):
    x=42+i*390
    text(label,x,174,365,13,teal,True)
    text(f"2019: {start[k]:,} · 2025: {end[k]:,}<br/>Cambio: +{end[k]-start[k]:,} (+{(end[k]/start[k]-1)*100:.2f}%)",x,150,365,12)
text('La razón pasó de 11.38 a 12.02 muertes por cada 1,000 accidentes: +0.64 por mil. La comparación de extremos no supone crecimiento continuo ni demuestra una causa.',42,93,750,11)
text('Power BI permite elegir otros años y entidades; los índices conservan la base del año inicial.',42,59,750,9,gray)
c.showPage()

base(5,'La distribución territorial requiere contexto')
text('Cinco entidades concentran el 37.3 % de las muertes de 1997-2025',42,500,750,17,teal,True)
items=d['entidades'][:5]
for i,row in enumerate(items):
    yy=443-i*35
    text(row['NOM_ENTIDAD'],42,yy+12,180,11)
    c.setFillColor(HexColor(teal)); c.rect(230,yy-4,420*row['MUERTOS']/18000,17,fill=1,stroke=0)
    text(f"{row['MUERTOS']:,}",240+420*row['MUERTOS']/18000,yy+12,90,11,navy,True)
text('Personas muertas; acumulado del período. Barras desde cero. Fuente y licencia INEGI indicadas al pie.',42,263,750,9,gray)
text('Qué puede concluirse',42,232,360,14,navy,True)
text('La serie muestra un descenso entre 2011 y 2019 y un cierre de 2025 superior al de 2019. Las diferencias territoriales describen concentración de muertes registradas; orientan nuevas preguntas, sin demostrar causas.',42,207,350,12)
text('Qué no dicen estos datos',440,232,360,14,navy,True)
text('ATUS registra muertes en el lugar, no a 30 días. Sin exposición no se estima riesgo individual. El subregistro de accidentes leves puede elevar la razón. Siguiente paso: medir aforos, velocidades e infraestructura y evaluar corredores antes-después con comparación.',440,207,350,11)
text('Reproducibilidad',42,105,750,12,navy,True)
text('JSON con SHA-256; Parquet con procedencia; 87 contrastes de conteos nacionales y 435 pares de años comprobados en pandas. Código: src/atus_api.py, src/analisis.py y src/validar_comparaciones.py. Repositorio: github.com/Gerar93Dot/Computo-cientifico-ok.',42,84,750,10)
c.save()
print(OUT)
