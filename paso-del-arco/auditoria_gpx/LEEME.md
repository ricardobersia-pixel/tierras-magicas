# Auditoría GPX — Paso del Arco v2.1

- `gpx_metrics.json`: métricas por track (km haversine, km sin saltos >1 km, fechas, tiempos, altitudes, proximidad a bases, waypoints, superposiciones, SHA-256 de cada archivo).
- Los 24 GPX originales (RutasWKLC.zip) **no se versionan aquí** (autoría propia confirmada por el titular; se mantienen fuera del repositorio por contener ubicaciones del campo).
- Reproducir: `GPX_METRICS=... python3 -I scripts/gpx_analyze.py <carpeta_gpx> gpx_metrics.json` y `scripts/gpx_map.py`.
