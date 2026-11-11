# ATUS: evolución temporal y distribución territorial desde una API real

## Propósito

**Pregunta científica:** ¿Cómo han cambiado las muertes por accidentes de tránsito urbanos en México entre 1997 y 2025 y en qué entidades se concentran?

Este proyecto analiza los indicadores anuales de ATUS del INEGI mediante un flujo reproducible en Python y un reporte de Power BI de tres páginas con mapas, filtros y gráficos. El alcance comprende zonas urbanas y suburbanas, 32 entidades y 29 años, de 1997 a 2025.

**Gran idea:** La prevención debe enfocarse no solo en reducir la cantidad de accidentes, sino también en su gravedad, considerando la evolución de las muertes y su distribución territorial.

Se estudian muertes y muertos por cada 1,000 accidentes registrados. Estos agregados describen patrones temporales y territoriales; no identifican situaciones individuales ni demuestran la eficacia de medidas preventivas.

## Cómo reproducir

Requisitos: Python 3.12 y Power BI Desktop con soporte para proyectos PBIP. Desde esta carpeta, crear y activar un entorno e instalar las versiones verificadas:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Un comando para consultar la API y generar los Parquet:**

```powershell
python src/atus_api.py
```

Para esa consulta, copiar `.env.example` a `.env` y configurar localmente el token personal del INEGI. Nunca versionar `.env`. El script conserva las respuestas y aprovecha la caché verificada por SHA-256. Para solicitar una edición nueva: `python src/atus_api.py --refresh` (respaldar los crudos antes).

**Reproducción exacta de la descarga incluida, sin token ni red:**

```powershell
python src/atus_api.py --offline
```

Abrir `reportes/ATUS_API_Profesional.pbip`. En Transformar datos > Administrar parámetros, establecer `RutaDatos` a la ruta absoluta de `data/processed` del proyecto. Aplicar cambios y actualizar. Azure Maps necesita conexión para el mapa base; las tablas y gráficos usan los Parquet locales.

Comprobaciones adicionales:

```powershell
python -m unittest discover -s tests -v
python src/analisis.py
```

## Datos

Fuente: [API del Banco de Indicadores INEGI](https://www.inegi.org.mx/servicios/api-indicadores/), BISE, versión 2.0, español, serie histórica. Licencia de datos: [Términos de libre uso INEGI](https://www.inegi.org.mx/inegi/terminos.html). El código usa MIT; no cambia la licencia de los datos.

| Indicador | ID | Unidad |
|---|---|---|
| Accidentes | 1006000039 | Accidentes |
| Víctimas muertas | 6200009438 | Personas |
| Víctimas heridas | 6200009439 | Personas |

Cada indicador se consulta para las entidades `01` a `32`. La consulta `00` se conserva por separado como control nacional, sin sumarla nuevamente a las entidades. `data/raw` contiene los JSON originales y sus archivos `.meta.json` con fecha de descarga, URL sin token y SHA-256. `procedencia.json` y los metadatos internos de cada Parquet documentan el origen.

La tabla principal tiene **928 filas entidad-año**. Sus conteos son enteros; CVE_ENT es texto con dos dígitos. FECHA representa el 1 de enero de cada año como clave técnica, no la fecha del accidente. No se sustituyen ausencias por cero. La copia de los crudos permite repetir el análisis aunque el servicio revise sus series después.

## Modelo y medidas validadas

### Lectura de las gráficas temporales

Las gráficas de evolución conservan los años 1997–2025 aunque se seleccione un solo año en el segmentador. El filtro de entidad sí se aplica. El subtítulo identifica esta excepción; las tarjetas y los demás gráficos siguen respondiendo al año seleccionado. Así se evita que la evolución se reduzca a un punto por seleccionar un único año. No se generan datos mensuales ni se interpolan valores.

Modelo en estrella: `dim_entidad[CVE_ENT]` (1) a `atus_anual_api[CVE_ENT]` (*), y `dim_fecha[FECHA]` (1) a `atus_anual_api[FECHA]` (*), con filtro en una dirección. `dim_fecha` es continua y está marcada como tabla de fechas. `dim_tipo_victima` es una tabla auxiliar desconectada para presentar muertas/heridas mediante SWITCH.

| Medida DAX | Comprobación pandas | Resultado sin filtros, 1997–2025 |
|---|---|---:|
| `Total de Accidentes = SUM(atus_anual_api[ACCIDENTES])` | `df.ACCIDENTES.sum()` | 10,999,723 |
| `Total de Muertos = SUM(atus_anual_api[MUERTOS])` | `df.MUERTOS.sum()` | 154,152 |
| `Total de Heridos = SUM(atus_anual_api[HERIDOS])` | `df.HERIDOS.sum()` | 3,347,199 |
| `Muertos por 1000 accidentes = DIVIDE([Total de Muertos], [Total de Accidentes]) * 1000` | `df.MUERTOS.sum() / df.ACCIDENTES.sum() * 1000` | 14.0142 |

La razón usa sumas, no el promedio de las razones estatales. No es una tasa por población ni una probabilidad individual. La validación de las tres sumas frente a la serie nacional independiente coincide en **87 contrastes** (29 años por tres medidas), registrados en `data/processed/validacion_medidas.json`.

Las pruebas automatizadas comprueban la integridad de referencias del reporte y el tratamiento de valores ausentes, duplicados y cobertura. Para verificar la presentación, abrir el proyecto en Power BI Desktop y contrastar las tarjetas sin filtros con los valores de la tabla.

## Alcance y limitaciones

- Los indicadores consultados son anuales y estatales. No contienen hora, día de semana, tipo de accidente, fuga, sexo ni municipio.
- Las muertes corresponden a personas fallecidas en el lugar del accidente. No incluyen fallecimientos posteriores.
- Los conteos territoriales dependen de la cobertura y de las prácticas de registro. Sin datos de población, vehículos o kilómetros recorridos, no constituyen tasas de riesgo comparables.
- Las notas oficiales sobre cobertura y disponibilidad se conservan en los catálogos `CL_NOTE` de `data/raw`.
- Cada gráfico utiliza una sola escala y las barras parten de cero. Los valores ausentes no se convierten en ceros.

## Documentación

- `docs/reporte_ATUS_API.pdf`: pregunta, gran idea, resultados, gráficos y limitaciones.
- `docs/presentacion_ATUS_API.pdf` y `.pptx`: diez diapositivas con notas para la exposición en el archivo editable.
- `docs/GUION_DEFENSA.md`: recorrido de once minutos y demostración de 60 segundos.
- `docs/REVISION_MANUAL_POWERBI.md`: comprobación de páginas y filtros.
- `docs/ENTREGA.md`: enlaces del repositorio y la versión de entrega.
- `docs/hallazgos.json`: resultados calculados por `src/analisis.py`.
- `docs/REVISION_PIA.md`: guía de revisión de los requisitos académicos.
- `docs/RELEASE_NOTES.md`: descripción del contenido para la publicación.

Para generar el PDF, instalar `requirements-docs.txt` y ejecutar `python src/reporte_pdf.py` después de `python src/analisis.py`.

## Herramientas de trabajo

Python y pandas se utilizan para la consulta, transformación y validación de datos; Power BI, para el modelo y las visualizaciones. Se utilizó asistencia de IA en la implementación y revisión técnica y editorial. La interpretación y la defensa académica corresponden al autor.
