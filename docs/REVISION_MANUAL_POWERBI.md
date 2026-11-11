# Revisión manual de Power BI

Abrir `reportes/ATUS_API_Profesional.pbip` junto con sus dos carpetas asociadas. Conservar toda la estructura del proyecto y la carpeta `data/processed`.

1. En Transformar datos > Administrar parámetros, establecer `RutaDatos` en la ruta absoluta de `data/processed`. Aplicar cambios y actualizar.
2. Sin filtros, comprobar 10,999,723 accidentes, 154,152 personas muertas y 3,347,199 heridas. Las tarjetas pueden abreviar las cifras a millones o miles; consultar el detalle o una tabla para los valores completos.
3. En **Resumen Ejecutivo y Geografía**, revisar tarjetas, mapa por entidad y evolución anual. Con un solo año seleccionado, la evolución conserva 1997–2025; el subtítulo lo indica.
4. En **Distribución y Víctimas**, seleccionar **Chiapas** y **2000**. El conteo de muertes de ese año es **89**; hubo **2,922** accidentes y la razón de ese año es **30.4586** por mil. La línea debe conservar todos los años de Chiapas y mostrar ese valor en 2000.
5. Probar otro año y otra entidad. El filtro de año afecta los gráficos de conteos; el de entidad también afecta las líneas temporales.
6. En **Análisis Territorial y Temporal**, comprobar que la tabla y el mapa de calor cambian con los filtros. Para 1999 y todas las entidades, el total de muertes es **5,525**.
7. Quitar las selecciones, comprobar que no aparecen mensajes de error y guardar si se hicieron cambios que deban conservarse.

La razón es `SUM(MUERTOS) / SUM(ACCIDENTES) * 1000`; no es un promedio simple de razones. Los rankings muestran conteos y no peligrosidad ajustada por población o exposición.

## Hojas de comparación

El orden tiene cinco hojas: Resumen Ejecutivo y Geografía; Distribución y Víctimas; Cantidad y gravedad; Cambios entre años; Análisis Territorial y Temporal.

Después de abrir el PBIP actualizado, pulsar Actualizar para cargar las dos tablas de selección de años. Se usan los mismos Parquet y no se necesita una consulta nueva a la API.

- **Cantidad y gravedad:** sin filtro anual, comprobar la razón nacional 14.0142. Cada punto representa una entidad. Seleccionar Sinaloa y Jalisco en el segmentador territorial: las barras deben compararlas y la dispersión debe conservar las 32 entidades. Un clic en un punto filtra detalle y barras. Quitar la selección para recuperar el contexto del segmentador. La referencia nacional conserva los años y elimina el filtro territorial.
- **Cambios entre años:** con 2019 y 2025 y todas las entidades, comprobar +17,662 accidentes, +4.8692 %, +444 muertes, +10.7584 % y +0.638943 muertes por 1,000 accidentes. Los índices nacionales deben partir de 100 en 2019 y terminar en 104.8692 y 110.7584. Seleccionar una entidad y contrastar con `control_comparacion_2019_2025.csv`.
- Elegir el mismo año en ambos extremos: cambios cero y un solo punto válido de índice. Elegir inicio posterior al fin: aviso de periodo inválido y medidas vacías. Es distinto de una serie histórica filtrada accidentalmente.
- Revisar etiquetas, referencia horizontal, desplazamiento de tablas y barras, y ausencia de errores. No se abrió Power BI para esta revisión: la evidencia automatizada cubre pandas y la estructura de los archivos, no el renderizado de Desktop.

Si se modifica el proyecto después de publicar un release, preparar una nueva versión y comprobarla antes de entregar. No sustituir silenciosamente el contenido de una versión entregada.
