# Accidentes de Tránsito en Zonas Urbanas y Suburbanas (ATUS): evolución temporal y distribución territorial desde una API real

## Propósito

**Pregunta científica:** ¿Cómo han cambiado las muertes por accidentes de tránsito urbanos en México entre 1997 y 2025 y en qué entidades se concentran?

Este proyecto analiza los indicadores anuales de ATUS del INEGI mediante un flujo reproducible en Python y un reporte de Power BI de cinco páginas con mapas, filtros y gráficos. El alcance comprende zonas urbanas y suburbanas, 32 entidades y 29 años, de 1997 a 2025.

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

El recorrido del Power BI es: **Resumen Ejecutivo y Geografía**, **Distribución y Víctimas**, **Cantidad y gravedad**, **Cambios entre años** y **Análisis Territorial y Temporal**. La última conserva la matriz de entidad y año.

En Cantidad y gravedad, la dispersión muestra las 32 entidades y una referencia nacional; elegir entidades permite comparar las barras. En Cambios entre años, los selectores inicial/final permiten estudiar diferencias absolutas, porcentajes e índices con base 100. El periodo predeterminado es 2019–2025; los periodos invertidos producen un aviso y medidas vacías. Las tablas de selección de años están desconectadas y no modifican las relaciones analíticas.

**Control pandas de las comparaciones:** `python src/validar_comparaciones.py`. Genera `docs/control_comparacion_2019_2025.csv` (32 entidades y total nacional) y `docs/validacion_comparaciones.json`. Comprueba 435 pares de años, aditividad de las diferencias, periodos de un mismo año y denominadores cero. En el total nacional 2019–2025: +17,662 accidentes (+4.8692 %), +444 muertes (+10.7584 %) y +0.638943 muertes por 1,000 accidentes. Las medidas están documentadas en la carpeta Comparaciones del modelo. Este control se ejecuta en pandas; la comprobación visual y la ejecución de las medidas nuevas en Desktop corresponden a la revisión manual.

Para regenerar solo las dos hojas de comparación: `python src/ampliar_powerbi.py`. La API, las respuestas conservadas y las tres hojas iniciales no dependen de ese generador. El informe académico PDF de 14 páginas y las once diapositivas incluyen cantidad frente a gravedad y cambios entre 2019 y 2025; las hojas interactivas permiten explorar otros periodos y entidades.

- Los indicadores consultados son anuales y estatales. No contienen hora, día de semana, tipo de accidente, fuga, sexo ni municipio.
- Las muertes corresponden a personas fallecidas en el lugar del accidente. No incluyen fallecimientos posteriores.
- Los conteos territoriales dependen de la cobertura y de las prácticas de registro. Sin datos de población, vehículos o kilómetros recorridos, no constituyen tasas de riesgo comparables.
- Las notas oficiales sobre cobertura y disponibilidad se conservan en los catálogos `CL_NOTE` de `data/raw`.
- Cada gráfico utiliza una sola escala y las barras parten de cero. Los valores ausentes no se convierten en ceros.

## Documentación

- `docs/reporte_ATUS_API_academico.pdf`: pregunta, gran idea, resultados, gráficos y limitaciones.
- `docs/presentacion_ATUS_API_actualizada.pdf` y `.pptx`: once diapositivas con notas para la exposición en el archivo editable.
- `docs/GUION_DEFENSA.md`: recorrido de doce minutos y demostración de 60 segundos.
- `docs/REVISION_MANUAL_POWERBI.md`: comprobación de páginas y filtros.
- `docs/ENTREGA.md`: enlaces del repositorio y la versión de entrega.
- `docs/hallazgos.json`: resultados calculados por `src/analisis.py`.
- `docs/REVISION_PIA.md`: guía de revisión de los requisitos académicos.
- `docs/RELEASE_NOTES.md`: descripción del contenido para la publicación.

El informe académico se consulta en `docs/reporte_ATUS_API_academico.pdf`. Para recalcular los hallazgos desde los Parquet, ejecutar `python src/analisis.py`.

## Prácticas del semestre

Los ejercicios introductorios se conservan en carpetas independientes:

- [Prácticas de Git](practicas/git/): `paraquegaspull.py`, `pruebapush.py` y `re3.py`.
- [Práctica de LaTeX](practicas/latex/main.tex): documento introductorio `main.tex`.

Estos archivos son evidencias de aprendizaje y no forman parte del flujo de análisis ATUS. La configuración y las dependencias del PIA permanecen en la raíz.

## Herramientas de trabajo

Python y pandas se utilizan para la consulta, transformación y validación de datos; Power BI, para el modelo y las visualizaciones. Se utilizó asistencia de IA en la implementación y revisión técnica y editorial. La interpretación y la defensa académica corresponden al autor.
