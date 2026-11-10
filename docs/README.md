# Documentación del análisis ATUS

## Orden de revisión

1. [Reporte del análisis](reporte_ATUS_API.pdf): pregunta científica, gran idea, resultados y limitaciones.
2. [README del proyecto](../README.md): fuente de datos, instalación, reproducción, modelo y validación de medidas.
3. [Proyecto de Power BI](../reportes/ATUS_API_Profesional.pbip): abrir la carpeta completa del proyecto en Power BI Desktop, configurar `RutaDatos` y actualizar.
4. [Código de consulta API](../src/atus_api.py): descarga JSON, verifica cobertura y genera Parquet.
5. [Cálculo de hallazgos](../src/analisis.py) y [resultados](hallazgos.json).
6. [Lista de revisión académica](REVISION_PIA.md).
7. [Registro de verificación](VERIFICACION.md): comprobaciones realizadas y actividades antes del release final.

## Cómo revisar los datos

Los JSON recibidos de INEGI están en `data/raw`. Sus metadatos contienen fecha de consulta y SHA-256. Los Parquet y el control nacional se encuentran en `data/processed`. La tabla principal contiene 928 filas, una por entidad y año.

En Power BI, las gráficas temporales muestran el período 1997–2025 completo y responden al filtro de entidad. Las tarjetas y otros gráficos también responden al año seleccionado.

## Presentación y entrega

El PDF de diapositivas y el ensayo de defensa están pendientes. El release final del PIA debe incluirlos y comprobarse antes de entregar sus enlaces en Teams.
