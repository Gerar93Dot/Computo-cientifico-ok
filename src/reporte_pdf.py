"""Reporte de lectura complementario al PBIP, generado desde hallazgos.json."""
import json
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

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

base(3,'La distribución territorial requiere contexto')
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
text('Sin población, vehículos o kilómetros recorridos no hay una tasa de riesgo comparable. ATUS registra fallecidos en el lugar del accidente; los criterios de registro pueden diferir entre entidades. No se infieren horarios ni situaciones de mayor gravedad.',440,207,350,12)
text('Reproducibilidad',42,105,750,12,navy,True)
text('API JSON conservados con SHA-256; Parquet con procedencia; 87 contrastes nacionales coincidentes. Código: src/atus_api.py y src/analisis.py. El PBIP complementa este documento con filtros y mapa por entidad.',42,84,750,10)
c.save()
print(OUT)
