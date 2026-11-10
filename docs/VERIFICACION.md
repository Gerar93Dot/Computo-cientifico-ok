# Verificación del proyecto ATUS

Fecha: 10 de noviembre de 2026.

## Flujo y datos

- Reproducción ejecutada con `python src/atus_api.py --offline` a partir de los JSON conservados.
- Integridad de las respuestas comprobada mediante SHA-256.
- Cobertura: 32 entidades, 29 años (1997–2025), 928 filas entidad-año.
- Las sumas estatales coinciden con el control nacional en los 87 contrastes anuales de las tres medidas.
- Parquet con tipos definidos y metadatos de procedencia; lectura posterior a la escritura comprobada.
- Totales: 10,999,723 accidentes; 154,152 personas muertas; 3,347,199 personas heridas.
- Razón del período: 14.014171 muertes por cada 1,000 accidentes registrados.
- Dependencias del flujo coincidentes con las versiones fijadas en requirements.txt.

## Código y Power BI

- Cuatro pruebas automatizadas aprobadas: valores ausentes, geografía y duplicados, cobertura y control nacional, y referencias del reporte.
- La validación rechaza discrepancias entre la suma estatal y el control nacional antes de generar Parquet.
- Se revisaron las relaciones del modelo, los tipos, la tabla de fechas y el parámetro RutaDatos.
- Las gráficas temporales conservan 1997–2025 al seleccionar un año; mantienen el filtro de entidad. La configuración está comprobada en los archivos del proyecto.
- La comprobación interactiva final de todas las páginas y filtros en Power BI Desktop permanece pendiente. Las pruebas de archivos no equivalen a esa comprobación.

## Documentación y publicación

- PDF de análisis de tres páginas revisado; pregunta, gran idea y cifras coherentes con el README y los datos.
- Fuente INEGI y licencia de datos identificadas; licencia MIT y metadatos de citación incluidos.
- Paquete de publicación revisado para excluir el token, archivos .env, cachés .pbi y entornos virtuales.
- Repositorio del proyecto: https://github.com/Gerar93Dot/Computo-cientifico-ok

## Antes del release final del PIA

- Completar la verificación interactiva de Power BI.
- Incorporar el PDF de diapositivas y preparar la demostración del flujo y la defensa.
- Comprobar los enlaces del release final y el acceso del docente.

Esta verificación documenta el alcance de las comprobaciones realizadas; no sustituye la revisión académica ni el ensayo de exposición.
