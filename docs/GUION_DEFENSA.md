# Guion de exposición y defensa

Diez diapositivas, 12 minutos. Bloques: 0-1 pregunta; 1-4 datos y flujo; 4-6 modelo; 6-10 historia; 10-12 limitaciones y siguiente paso.

## 1. La prevención también debe atender la gravedad

**0:00-1:00**

Explicar la pregunta científica y expresar la gran idea. Delimitar 1997-2025, zonas urbanas y suburbanas y análisis estatal. La gravedad se aproxima mediante muertes en el lugar por 1,000 accidentes registrados.

## 2. Los datos abarcan 32 entidades durante 29 años

**1:00-2:00**

Mostrar la unidad entidad-año: 32 entidades por 29 años, 928 registros. Accidentes, muertos y heridos son conteos de la API. La serie nacional es un control y no se suma otra vez a los registros estatales.

## 3. El flujo reproduce los datos sin depender de la red

**2:00-4:00**

De 2:00 a 3:00 explicar la consulta real a la API, los JSON conservados con SHA-256 y el Parquet tipado. De 3:00 a 4:00 realizar la demostración: 0-15 s mostrar JSON y metadatos; 15-40 s ejecutar python src/atus_api.py --offline; 40-60 s mostrar los Parquet y 928 filas. Explicar que offline reproduce respuestas obtenidas de la API, no una consulta nueva. No mostrar el token. Plan B: docs/DEMOSTRACION_OFFLINE.txt y las capturas de docs/evidencia.

## 4. El modelo relaciona cada registro con su año y entidad

**4:00-5:00**

Explicar dim_fecha (1) y dim_entidad (1) hacia atus_anual_api (*), con filtros unidireccionales. La fecha 1 de enero es una clave anual, no la fecha del accidente. RutaDatos parametriza el origen. Seleccion_Inicio y Seleccion_Fin no tienen relaciones: sus valores entran en las medidas para comparar extremos.

## 5. Las sumas coinciden con el control nacional

**5:00-6:00**

Mostrar tres medidas SUM documentadas y sus equivalentes pandas, bajo los mismos filtros. Los 87 contrastes comparan tres conteos por 29 años con la serie nacional de la API. Para la razón se dividen sumas, no se promedian razones. El control de las comparaciones en pandas comprende 435 pares de años; distingue esa evidencia de ejecutar las medidas nuevas en Desktop. Consultar docs/control_comparacion_2019_2025.csv durante la revisión manual.

## 6. De 2019 a 2025, las muertes crecieron más que los accidentes

**6:00-7:20**

Hallazgo temporal. En 2019 se registran 362,729 accidentes y 4,127 muertes; en 2025, 380,391 y 4,571. Son +17,662 accidentes (+4.87 %) y +444 muertes (+10.76 %). El índice parte de 100 en ambas series y evita un doble eje. La razón cambia de 11.38 a 12.02 por mil. La comparación de extremos no implica crecimiento continuo ni atribuye causas; el descenso de 2011 a 2019 se conserva en el informe.

## 7. Más accidentes no implica una mayor razón de muertes

**7:20-8:40**

Hallazgo cantidad-gravedad. Cada punto es una entidad, con accidentes acumulados en X y muertes por 1,000 accidentes en Y. Nuevo León registra 2,067,245 accidentes y 7,613 muertes: razón 3.68, frente a 14.01 nacional. El volumen no basta para describir la gravedad registrada. La razón nacional se calcula con los totales, no con el promedio estatal. No concluir que una entidad es más segura: diferencias en exposición y registro alteran la comparación.

## 8. Cinco entidades concentran el 37.3% de las muertes

**8:40-10:00**

Hallazgo territorial. México, Jalisco, Chihuahua, Sinaloa y Michoacán de Ocampo concentran 37.3 % de las muertes acumuladas. Explicar la diferencia entre concentración absoluta y razón por accidente. El acumulado de 29 años no representa por sí solo la situación actual. La hoja Cambios entre años permite explorar qué entidades contribuyen a los aumentos y descensos.

## 9. Los registros describen patrones, no causas

**10:00-11:00**

Reconocer límites: fallecidos en el lugar y no a 30 días; falta de exposición por viajes o kilómetros; posibles diferencias de registro de accidentes leves; agregados anuales y estatales que no identifican horarios, circunstancias ni cruces peligrosos. Una razón mayor no demuestra peor infraestructura ni riesgo individual mayor.

## 10. La prevención debe considerar cantidad y gravedad

**11:00-12:00**

Proponer un estudio local de corredores: accidentes georreferenciados, aforos, velocidades, iluminación, geometría y protección peatonal. Evaluar antes-después con corredores comparables, ajuste por exposición y regresión a la media. No atribuir las diferencias estatales a estos mecanismos sin medición. Repetir la gran idea y cerrar con la URL del repositorio.

## Preparación personal

Ensayar dos veces con cronómetro. Revisar que la pregunta, la gran idea y los títulos expresen el planteamiento propio del autor, como exige el apartado 5 del PIA. Poder explicar las funciones del código y cada medida. La evidencia pandas no sustituye a comprobar los filtros de Power BI.
