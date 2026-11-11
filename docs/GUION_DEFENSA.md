# Guion de exposición y defensa

Duración objetivo: 11 minutos. Diez diapositivas. Usar las notas del PowerPoint como apoyo para preparar la explicación, sin leerlas durante la exposición.

| Tiempo | Diapositiva | Qué explicar |
|---|---|---|
| 0:00–1:00 | 1 | Pregunta científica y gran idea. Delimitar zonas urbanas y suburbanas, años y entidades. |
| 1:00–2:00 | 2 | Tres indicadores; una fila por entidad y año. 32 × 29 = 928 filas. |
| 2:00–3:00 | 3 | Demostración del flujo durante 60 segundos. |
| 3:00–4:15 | 4 | Relaciones uno a muchos, fechas, tipos y parámetro RutaDatos. |
| 4:15–5:30 | 5 | Medidas SUM en DAX, equivalentes pandas y 87 contrastes nacionales. |
| 5:30–6:45 | 6 | Descenso de 2011 a 2019 y valor de 2025. No afirmar crecimiento continuo. |
| 6:45–7:45 | 7 | Razón de muertos por 1,000 accidentes; explicar numerador y denominador. |
| 7:45–9:00 | 8 | Concentración territorial y ausencia de una tasa ajustada de riesgo. |
| 9:00–10:15 | 9 | Cobertura, diferencias de registro, muertes en el lugar y ausencia de exposición. |
| 10:15–11:00 | 10 | Gran idea, siguiente paso y URL del repositorio. |

## Demostración de 60 segundos

Antes de presentar, abrir una terminal en la raíz del proyecto, activar el entorno y dejar disponibles las carpetas `data/raw` y `data/processed`. No mostrar el archivo `.env` ni el token.

1. **0–15 s:** mostrar un JSON de `data/raw` y el campo SHA-256 de su `.meta.json`.
2. **15–40 s:** ejecutar `python src/atus_api.py --offline`. Explicar que reproduce respuestas reales conservadas, sin consultar la red.
3. **40–50 s:** mostrar el mensaje de 928 filas y la coincidencia nacional.
4. **50–60 s:** mostrar los Parquet y abrir el reporte de Power BI previamente cargado.

La consulta en línea utiliza `python src/atus_api.py`; `--refresh` solicita respuestas nuevas y debe ejecutarse con una copia de respaldo si se necesita conservar la edición analizada.

## Plan alternativo

Si falla la ejecución o el equipo de proyección, mostrar `DEMOSTRACION_OFFLINE.txt`, que contiene una ejecución registrada, y las capturas disponibles en `docs/evidencia`. Identificarlo como evidencia guardada, no como una consulta en vivo. El PDF de diapositivas también funciona sin PowerPoint ni conexión.

## Preguntas para practicar

**¿Obtendré lo mismo dentro de seis meses?** El modo offline verifica SHA-256 y reproduce los JSON conservados. Una consulta nueva puede recibir revisiones del INEGI; se registra la procedencia de cada edición.

**¿Por qué las medidas DAX son correctas?** Usan sumas explícitas de los conteos. El cálculo equivalente en pandas y la serie nacional independiente permiten comprobar los totales. Al filtrar año y entidad debe compararse el mismo subconjunto.

**¿Por qué no se suma la serie nacional a las entidades?** Representa los mismos fenómenos a otro nivel geográfico; incluirla en la tabla de hechos duplicaría los totales.

**¿Qué significa FECHA = 1 de enero?** Es una clave anual para relacionar la tabla de hechos con el calendario, no la fecha individual de un accidente.

**¿Qué significa 14.0142?** Es el total de personas muertas dividido por el total de accidentes del período, multiplicado por 1,000. No es el promedio simple de las razones estatales ni una probabilidad individual.

**¿Puede concluirse qué estado es más peligroso?** Los conteos muestran concentración. Sin población, vehículos o kilómetros recorridos y sin considerar cobertura, no se obtiene una comparación ajustada del riesgo.

**¿Por qué no hay análisis por hora o causa?** Las consultas utilizadas son agregados anuales por entidad; no contienen circunstancias individuales. Ese análisis requeriría otra fuente y un alcance diferente.

**¿Qué hace la tabla de tipos de víctima?** Contiene etiquetas para la visualización. Está desconectada y una medida SWITCH selecciona la suma de muertos o heridos según la etiqueta.

## Ensayo personal

Realizar dos ensayos completos en voz alta con cronómetro. Explicar cada función del código y practicar la demostración. Si una respuesta se desconoce, reconocerlo y explicar cómo se comprobaría. El archivo no acredita que los ensayos se hayan realizado.
