# -*- coding: utf-8 -*-
"""v2.3: respuestas del titular (16/11/2026) — RP12 pública, tranquera 1, campo dividido por RP12, límites de referencia,
transitabilidad invernal, autoría de los GPX y plan de relevamiento de puntos de interés con fotos."""
import json, os
from data_v21 import *

RP = json.load(open(os.environ["RP12_JSON"]))
RP12_TRACK = RP["tracks"]

TITULAR_V23 = [
 ("RP12", "CONF: pública en todo su recorrido. El campo está dividido por la RP12."),
 ("Límites de referencia", "CONF: desde el Cerro Piñihue hasta la costa del Arroyo del Arco (sin coordenadas; no es límite catastral)."),
 ("Primera tranquera", "CONF: -38.832922, -71.058162 (lado oeste de la RP12, a 25 m del eje; coincide a ≈65 m con el waypoint 'Tranquera' de XLeña)."),
 ("Transitabilidad", "CONF: hasta la primera tranquera, en invierno solo 4x4; el resto del año, vehículo de calle no bajo."),
 ("Autoría GPX", "CONF: las 24 trazas fueron grabadas por el titular."),
 ("Relevamiento próximo", "CONF: el titular planea grabar una traza con todos los puntos de interés y fotografías."),
 ("Laguna Pilhue / Aduana Vieja / Castillo dentro del campo", "PEND: el titular no puede determinarlo por ahora."),
 ("Significado de 'CP'", "PEND: el titular no lo recuerda."),
]

ACCESO = dict(ACCESO)
ACCESO["dato_titular"] = ("CONF: acceso = intersección RP13/RP12 (Paso del Arco) -38.902440, -71.064667. RP12 pública en todo su recorrido; "
                          "primera tranquera -38.832922, -71.058162 a ≈9,3 km por la RP12; en invierno, tramo solo para 4x4.")
ACCESO["metodo"] = ACCESO["metodo"].replace("NE (hacia las bases → RP12 por descarte, INF a confirmar)", "NE (hacia las bases = RP12: la tranquera informada por el titular está sobre ella)")
ACCESO["dist"] = [("Tranquera 1 (CONF)", 7.812, f"≈{RP['acc_a_tranquera_km']:.1f} km por RP12".replace(".", ","))] + [d for d in ACCESO["dist"] if not d[0].startswith("Tranquera")]
DIST_BASES = [d for d in DIST_BASES if not d[0].startswith("Acceso")] + [("Acceso RP13/RP12 (CONF)", n, km, txt) for n, km, txt in ACCESO["dist"]]

SECTORES = {"Inicio": "Oeste", "Chivero": "Oeste", "Vaquero": "Este", "Tranquera 1": "Oeste"}

# ---- Bases: sector respecto de la RP12
_bl = {
 "PDA-BASE-001": f" v2.3: sector OESTE de la RP12 ({RP['bases']['Inicio']['dist_RP12_km']*1000:.0f} m de la ruta); se llega por la Tranquera 1 (≈0,8 km). Fuera del invierno, el cliente puede llegar en vehículo de calle no bajo (CONF).",
 "PDA-BASE-002": f" v2.3: sector ESTE de la RP12 ({RP['bases']['Vaquero']['dist_RP12_km']*1000:.0f} m de la ruta): ir de Inicio o Chivero a Vaquero obliga a CRUZAR la RP12.",
 "PDA-BASE-003": f" v2.3: sector OESTE de la RP12 ({RP['bases']['Chivero']['dist_RP12_km']*1000:.0f} m de la ruta).",
 "PDA-BASE-004": " v2.3: el titular ubica el límite del campo en la costa del Arroyo del Arco. HIP: el cruce 'Río/Puente/Vado' (1,6–1,7 km al E de Vaquero) podría ser ese arroyo; confirmar en el relevamiento.",
}
BASES = [tuple(list(b[:6]) + [b[6] + _bl[b[0]], b[7]]) for b in BASES]

# ---- Circuitos: km sobre RP12 y ajustes
_new = []
for c in CIRCUITOS:
    c2 = list(c); r = RP12_TRACK[c[1]]
    c2[7] = c2[7] + f" · Sobre RP12 (tramo acceso–Cruce N): {r['km_sobre_RP12']:.1f} km ({r['pct_sobre_RP12']:.0f}%)"
    if c[0] == "PDA-EX-019":
        c2[8], c2[9] = 5, 3
        c2[10] = c2[10] + " v2.3: el 69% de sus km va sobre la RP12 PÚBLICA (CONF): es un recorrido de ruta, no un circuito interno."
        c2[12] = "Traslado escénico acceso→bases; no producto 4x4 propio."
        c2[14] = "Sin inspección de producto; relevar estado de la RP12 por estación."
        c2[17] = "Ola 2 (acceso)"; c2[18] = (2, 3, 3, 2, 2)
    if c[0] == "PDA-EX-022":
        c2[10] = c2[10] + " v2.3: solo 3,2 km (14%) van sobre la RP12; ≈20 km por huellas fuera de la ruta. Cruza la RP12 para conectar los sectores oeste y este."
        c2[14] = "Campo Ola 1, PRIMERO; registrar cada cruce de la RP12 y su visibilidad."
    if c[0] == "PDA-EX-003":
        c2[10] = c2[10] + " v2.3: 38% de sus km sobre la RP12; el ramal oeste hacia el Punto límite campo (¿Cerro Piñihue?) es off-RP12."
    _new.append(tuple(c2))
CIRCUITOS = _new

# ---- Discrepancias / faltantes / riesgos
_x = {"X15": ("Confirmado por el titular: las trazas son propias.", "Resuelta"),
      "X17": ("Confirmado: la RP12 es pública en todo su recorrido y divide el campo. Sobre el tramo acceso–Cruce N: 019 = 69%, 003 = 38%, 022 = 14% de sus km.", "Resuelta (v2.3)")}
DISCREPANCIAS = [(d[0], d[1], d[2], d[3], _x[d[0]][0], _x[d[0]][1]) if d[0] in _x else d for d in DISCREPANCIAS]
_f = {"D23": ("Acceso", "Coordenada de la intersección RP13/RP12", "Recepción, logística", "RECIBIDA y verificada (rama NE = RP12)", "Resuelta"),
      "D24": ("Acceso", "Carácter de la RP12 y tranquera de ingreso", "Encuadre legal", "CONF: RP12 pública; Tranquera 1 -38.832922, -71.058162; campo dividido por la RP12", "Resuelta"),
      "D25": ("GPX", "Autoría de las trazas", "Uso y publicación", "CONF: propias del titular", "Resuelta"),
      "D26": ("Territorio", "¿Laguna Pilhue, Aduana Vieja y Castillo están dentro del campo?", "Atractivos propios", "Titular: no determinable ahora → resolver con mensura o en el relevamiento de puntos", "Alta"),
      "D27": ("Territorio", "Significado del waypoint 'CP'", "Interpretación", "Titular no lo recuerda → re-identificar en el relevamiento (186 m de Chivero)", "Baja")}
FALTANTES = [(f[0],) + _f[f[0]] if f[0] in _f else f for f in FALTANTES] + [
 ("D29", "Territorio", "Coordenadas de Cerro Piñihue (cumbre/límite) y de la costa del Arroyo del Arco", "Polígono de referencia", "Relevamiento POI del titular", "Alta"),
 ("D30", "Producto", "Coordenadas y fotos de Lagunas Norte, Mirador de las antenas y demás tranqueras", "Portafolio y fichas", "Relevamiento POI del titular", "Alta"),
 ("D31", "Operación", "Puntos de cruce de la RP12 entre sectores oeste y este: visibilidad, banquinas, señalización", "Seguridad del convoy", "Relevamiento + consulta a Vialidad", "Alta"),
]
RIESGOS = [(r[0], r[1], "CONF: RP12 pública y divide el campo. Llegada a las bases por ≈9,3 km de RP12 (solo 4x4 en invierno); los productos cruzan la ruta entre sectores; traslado de pasajeros en vía pública requiere habilitación de transporte.", "Alta", r[4],
            "Cliente llega en vehículo propio hasta Inicio fuera del invierno; traslados en invierno solo con prestador de transporte habilitado; protocolo de cruce de ruta (puntos fijos, guía a pie, señalización temporal, velocidad).", r[6], r[7]) if r[0] == "R15" else r for r in RIESGOS]
IMPLEMENTACION = [(t[0], t[1], t[2], t[3], "HECHO v2.2–2.3 (acceso, RP12, tranquera)" if t[0] == "T03b" else t[4], t[5]) for t in IMPLEMENTACION]
IMPLEMENTACION.insert(4, ("T03c", "Etapa 0", "Relevamiento de puntos de interés con fotos (titular), según protocolo y GPX base PDA-POI v1", "Titular", "Sem 1–4", "GPX + fotos geolocalizadas + planilla 19"))

# ---- Portafolio: implicancias de acceso
PORTAFOLIO = [tuple(list(p[:6]) + [p[6] + (" Fuera del invierno, el cliente puede llegar a Inicio en su vehículo (CONF); en invierno, traslado 4x4 habilitado desde el acceso." if p[0] in ("P01", "P02", "P04", "P05", "P06") else "")] + list(p[7:])) for p in PORTAFOLIO]

# ---- Puntos de interés para el relevamiento
# (código, nombre, tipo, lat, lon, origen, estado, qué relevar)
POI = [
 ("PDA-POI-001", "Acceso RP13/RP12 (Paso del Arco)", "Acceso", -38.902440, -71.064667, "CONF titular", "Coordenada confirmada", "Foto de la intersección y señalización; estado del camino"),
 ("PDA-POI-002", "Tranquera 1 (RP12)", "Tranquera", -38.832922, -71.058162, "CONF titular", "Coordenada confirmada", "Foto, tipo de cierre, ancho, visibilidad desde la RP12"),
 ("PDA-POI-003", "Base 1 — Inicio (quincho)", "Base", -38.832050, -71.066724, "CONF titular", "Coordenada confirmada", "Fotos exteriores/interiores, cocina, baño, agua, energía, señal"),
 ("PDA-POI-004", "Base 2 — Vaquero", "Base", -38.814204, -71.050709, "CONF titular", "Coordenada confirmada", "Fotos, infraestructura existente, fogón, agua, sombra"),
 ("PDA-POI-005", "Base 3 — Chivero", "Base", -38.807993, -71.063218, "CONF titular", "Coordenada confirmada; camino sin traza", "Grabar el camino desde la RP12; fotos, corrales, espacios para chicos"),
 ("PDA-POI-006", "Aduana Vieja (Paso del Arco)", "Patrimonio", -38.791826, -71.058897, "EXT wpt 003 (012 lo ubica a 85 m)", "Verificar", "Fotos, estado de ruinas, ¿dentro del campo?"),
 ("PDA-POI-007", "Vado Aduana Vieja", "Vado", -38.790233, -71.059082, "EXT wpt 012", "Verificar", "Fondo, profundidad típica, crecidas"),
 ("PDA-POI-008", "Castillo / Grupo el Arco", "Formación", -38.792104, -71.070767, "EXT wpt 003 = 024", "Verificar", "Fotos; ¿es el 'arco' que da nombre al paso?"),
 ("PDA-POI-009", "Cima", "Mirador", -38.802437, -71.058298, "EXT wpt 003", "Verificar", "Foto panorámica 360°, acceso"),
 ("PDA-POI-010", "CP (significado a re-identificar)", "Otro", -38.806765, -71.061762, "EXT wpt 003", "Re-identificar", "Foto y descripción"),
 ("PDA-POI-011", "Entrada campo mecánico", "Tranquera/acceso", -38.805388, -71.058735, "EXT wpt 024", "Verificar", "¿Es otra tranquera desde la RP12?"),
 ("PDA-POI-012", "Punto límite campo (¿Cerro Piñihue?)", "Límite", -38.818238, -71.103710, "EXT wpt 003", "Verificar", "¿Coincide con el Cerro Piñihue o con un alambrado?"),
 ("PDA-POI-013", "Laguna Pilhue", "Laguna", -38.836408, -71.097463, "EXT wpt 012", "Verificar", "Fotos, acceso, ¿dentro del campo?"),
 ("PDA-POI-014", "Entrada Pilhue", "Acceso", -38.836738, -71.096347, "EXT wpt 010", "Verificar", "Tipo de acceso"),
 ("PDA-POI-015", "Laguna Corazón", "Laguna", -38.826952, -71.124900, "EXT wpt 012", "Verificar", "Fotos, acceso, titularidad"),
 ("PDA-POI-016", "Laguna del Arco", "Laguna", -38.804152, -71.171810, "EXT wpt 012", "Verificar", "Fotos, acceso, titularidad"),
 ("PDA-POI-017", "Vado Laguna del Arco", "Vado", -38.803313, -71.169027, "EXT wpt 012", "Verificar", "Fondo y profundidad"),
 ("PDA-POI-018", "Laguna Escondida", "Laguna", -38.817470, -71.164700, "EXT wpt 012", "Verificar", "Fotos"),
 ("PDA-POI-019", "Araucaria Guacha", "Árbol singular", -38.824605, -71.153913, "EXT wpt 012", "Verificar", "Fotos"),
 ("PDA-POI-020", "Río / Puente / Vado (¿Arroyo del Arco?)", "Vado/Puente", -38.811902, -71.032685, "EXT wpt 013 (Puente)", "Verificar", "Nombre del curso de agua; carga del puente; ¿costa límite del campo?"),
 ("PDA-POI-021", "Vado (024)", "Vado", -38.784122, -71.092310, "EXT wpt 024", "Verificar", "Fondo y profundidad"),
 ("PDA-POI-022", "Vertiente", "Agua", -38.825382, -71.022712, "EXT wpt 013", "Verificar", "Caudal; ¿potable? (análisis)"),
 ("PDA-POI-023", "Vista del Aluminé", "Mirador", -38.896102, -71.056230, "EXT wpt 012", "Verificar", "Foto panorámica (1 km del acceso)"),
 ("PDA-POI-024", "Batea Mahuida — punto más alto registrado (020)", "Cerro", -38.815728, -71.185668, "INF: punto de mayor altitud de la traza 020; NO es la cumbre", "Referencia", "Solo con autorización de la Comunidad Puel"),
 ("PDA-POI-025", "Cerro Piñihue (cumbre)", "Cerro/Límite", None, None, "CONF titular (sin coordenada)", "PEND", "Cumbre y pie del cerro; ¿mirador?"),
 ("PDA-POI-026", "Costa del Arroyo del Arco (límite)", "Límite", None, None, "CONF titular (sin coordenada)", "PEND", "Puntos cada ~500 m sobre la costa"),
 ("PDA-POI-027", "Lagunas Norte", "Laguna", None, None, "CONF titular (sin coordenada)", "PEND", "Cada laguna como punto separado"),
 ("PDA-POI-028", "Mirador de las antenas", "Mirador", None, None, "CONF titular (sin coordenada)", "PEND", "Panorámica; ¿señal celular?"),
 ("PDA-POI-029", "Puesto del Arroyo del Arco", "Puesto", None, None, "CONF titular (sin coordenada)", "PEND", "Estado, acceso, uso posible"),
 ("PDA-POI-030", "Otras tranqueras y cruces de la RP12", "Tranquera/cruce", None, None, "CONF titular (existen; sin coordenadas)", "PEND", "Cada una con foto; visibilidad del cruce"),
]

PROTOCOLO = [
 ("Equipo", "Celular con Wikiloc (o equivalente), batería extra, cámara con GPS activado (las fotos deben quedar geolocalizadas)."),
 ("Antes de salir", "Cargar el archivo 'PDA_POI_base_v1.gpx' para navegar a los 24 puntos conocidos y confirmarlos o corregirlos."),
 ("Grabación", "Registro continuo (1 punto cada 1–5 s). Una traza por jornada. Nombre: 'PDA-REL-AAAAMMDD'."),
 ("Waypoints", "Nombrar con el código y el nombre de la planilla (ej. 'PDA-POI-013 Laguna Pilhue'). Para puntos nuevos, seguir la numeración desde PDA-POI-031."),
 ("Fotos", "Por punto: 1 general, 1 de detalle y 1 del acceso (desde dónde se llega). En miradores, panorámica. Anotar la dirección de la toma."),
 ("RP12", "Marcar cada cruce y cada tramo de la ruta pública ('RP12 inicio/fin') para separar la ruta pública de las huellas internas."),
 ("Límites", "Marcar alambrados y mojones visibles; Cerro Piñihue y la costa del Arroyo del Arco cada ~500 m. Es una referencia, no reemplaza la mensura."),
 ("Datos por punto", "Completar en la hoja 19: dentro del campo (Sí/No/No sé), sector (O/E de la RP12), acceso (4x4/4x2/a pie), estado, riesgos, temporada, observaciones."),
 ("Entrega", "Exportar el GPX desde Wikiloc, más la carpeta de fotos originales (sin comprimir, para conservar la ubicación GPS)."),
]
