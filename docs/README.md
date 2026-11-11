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

- [Diapositivas en PDF](presentacion_ATUS_API.pdf): diez diapositivas para una exposición de aproximadamente once minutos.
- [Presentación editable](presentacion_ATUS_API.pptx): incluye notas para el expositor y gráficos editables.
- [Guion de defensa](GUION_DEFENSA.md): tiempos, demostración de 60 segundos y preguntas para practicar.
- [Ejecución registrada](DEMOSTRACION_OFFLINE.txt) y [capturas](evidencia/): apoyo para la demostración sin conexión.
- [Lista de revisión manual de Power BI](REVISION_MANUAL_POWERBI.md).
- [Enlaces de entrega](ENTREGA.md).

El autor debe realizar la revisión manual de Power BI y los ensayos en voz alta antes de presentar.
