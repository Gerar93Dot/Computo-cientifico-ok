# Revisión frente a las indicaciones del PIA

La consigna requiere Power BI: usar mapas y gráficos interactivos es compatible. La apariencia del reporte no sustituye la trazabilidad de los datos ni la validación.

| Requisito | Evidencia / estado |
|---|---|
| README, propósito, reproducción y datos | README raíz |
| LICENSE y CITATION.cff | Archivos raíz con licencia y datos de citación |
| API real, crudos JSON | src/atus_api.py y data/raw |
| Parquet tipados y procedencia | data/processed y metadatos internos |
| Dependencias == y comando único | requirements.txt y README |
| PBIP, parámetro, estrella y fechas | reportes/ATUS_API_Profesional.pbip |
| Tres medidas contra pandas | README y validacion_medidas.json |
| Pregunta | Evolución de las muertes y concentración territorial entre 1997 y 2025 |
| Gran idea | La prevención debe enfocarse no solo en reducir la cantidad de accidentes, sino también en su gravedad, considerando la evolución de las muertes y su distribución territorial. |
| Títulos-mensaje y PDF del reporte | docs/reporte_ATUS_API_academico.pdf; comprobar legibilidad, unidades, fuente y licencia |
| PDF de diapositivas, demostración y defensa | presentacion_ATUS_API_actualizada.pdf, GUION_DEFENSA.md, DEMOSTRACION_OFFLINE.txt y evidencia/; ensayo a cargo del autor |
| Historial y release v1.0.0 en GitHub | Repositorio Gerar93Dot/Computo-cientifico-ok; enlaces en ENTREGA.md |
| Acceso docente, Issues y enlaces Teams | Pendiente; ninguna configuración externa se ha modificado |

## Conceptos para la defensa

1. Un registro de esta API es un agregado entidad-año, no un accidente individual.
2. El control nacional no entra en el modelo de hechos: evita duplicar el total.
3. Los tres indicadores suman 10,999,723 accidentes, 154,152 personas muertas y 3,347,199 personas heridas en 1997–2025.
4. Muertos por mil accidentes mide una relación entre conteos registrados, no riesgo vial ajustado por exposición.
5. La comparación territorial usa conteos. Sin población, vehículos o kilómetros no se puede afirmar que una entidad sea más peligrosa.
6. Los fallecidos de ATUS corresponden al lugar del accidente; no equivalen a todas las muertes viales posteriores.

## Comprobación final antes de publicar

- Abrir el PBIP desde esta carpeta y revisar sus cinco páginas y filtros.
- Verificar los PDFs finales, unidades, fuente y licencia por visual.
- Explicar con palabras propias la pregunta, gran idea, títulos y cada función del código.
- Revisar el contenido a versionar: nunca .env, .venv ni cachés .pbi.
- Crear commits con mensajes descriptivos.
- Publicar el release con notas y comprobar los enlaces; agregar fecha y URL reales a CITATION.cff cuando existan.
- Ensayar 10–12 minutos y la demostración de 60 segundos. Conservar el modo offline como alternativa sin red.
