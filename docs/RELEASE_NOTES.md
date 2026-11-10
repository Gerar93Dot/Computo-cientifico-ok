# ATUS API — v1.0.0

- Consulta de tres indicadores ATUS de INEGI para 32 entidades y control nacional.
- JSON originales verificables por SHA-256 y transformación a Parquet con procedencia.
- Modelo de Power BI en estrella, con fechas, parámetro de ruta y medidas contrastadas con pandas.
- Reporte de Power BI de tres páginas con mapas, filtros y gráficos de evolución temporal y distribución territorial.
- Resultados del período 1997–2025: 10,999,723 accidentes, 154,152 personas muertas y 3,347,199 personas heridas.

Limitaciones: agregados anuales, diferencias de registro territorial y ausencia de datos de exposición. Las consultas no incluyen causas, horarios ni circunstancias individuales. Los fallecimientos corresponden al lugar del accidente.
