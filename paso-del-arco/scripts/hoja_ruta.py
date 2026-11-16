# -*- coding: utf-8 -*-
"""Codificación de puntos de interés (ZONA-TIPO-NN) y hoja de ruta de relevamiento por jornadas.
Uso: hoja_ruta.py <dir_gpx> <out_dir>
Distancias: camino más corto sobre la red de las 24 trazas del titular (celdas ~20 m). Si un punto no tiene traza a <150 m,
el tramo final se estima como línea recta x 1,4 y se marca 'sin traza'."""
import sys, os, math, heapq, json
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ZONAS = [
 ("R", "Ruta pública", "Puntos sobre o junto a la RP12/RP13 (vía pública)."),
 ("O", "Campo oeste", "Campo, al oeste de la RP12 (Inicio, Chivero, Tranquera 1, Cerro Piñihue)."),
 ("E", "Campo este", "Campo, al este de la RP12 (Vaquero, Arroyo del Arco)."),
 ("N", "Sector norte", "Al norte del Cruce N (Aduana Vieja, Castillo). Si es parte del campo: A CONFIRMAR."),
 ("L", "Lagunas oeste", "Lagunas al oeste del campo (Pilhue, Corazón, del Arco). Si son parte del campo: A CONFIRMAR."),
 ("X", "Externo (alias heredado)", "Solo para códigos anteriores. Los puntos fuera del campo usan un TERRITORIO (A.. Argentina / C.. Chile)."),
 ("P", "Por posicionar", "Puntos sin coordenada. Al relevarlos reciben su código definitivo; el código P queda como alias."),
]
# Territorios fuera del campo: 3 letras = PAÍS (A Argentina / C Chile) + LUGAR (2 letras). Lista ampliable.
TERRITORIOS = [
 ("APE", "Argentina", "Villa Pehuenia y alrededores (incluye el lado argentino del Paso Icalma)"),
 ("AMO", "Argentina", "Moquehue"), ("AAL", "Argentina", "Aluminé"),
 ("ABM", "Argentina", "Batea Mahuida (Comunidad Mapuche Puel)"), ("ALT", "Argentina", "Litrán / RP13–RP23"),
 ("APP", "Argentina", "Primeros Pinos"), ("AZA", "Argentina", "Zapala"),
 ("CIC", "Chile", "Icalma (lado chileno; comuna de Lonquimay)"), ("CLQ", "Chile", "Lonquimay"),
 ("CME", "Chile", "Melipeuco"), ("CCG", "Chile", "Parque Nacional Conguillío"), ("CCU", "Chile", "Curacautín"),
]
TIPOS = [
 ("ACC", "Acceso / cruce de caminos"), ("BAS", "Base operativa (NN = número de base)"), ("TRQ", "Tranquera / portón"),
 ("CRZ", "Cruce de la RP12 para convoy"), ("VAD", "Vado"), ("PTE", "Puente"), ("AGU", "Vertiente / aguada / arroyo"),
 ("LAG", "Laguna"), ("MIR", "Mirador / punto panorámico"), ("CER", "Cerro / cumbre"), ("LIM", "Límite: alambrado, mojón, costa"),
 ("PAT", "Patrimonio histórico"), ("FOR", "Formación rocosa"), ("ARB", "Árbol singular"), ("PUE", "Puesto"),
 ("RSG", "Punto de riesgo (pendiente, piedra suelta, barranco)"), ("SRV", "Servicio (estacionamiento, baño, agua)"),
 ("FOT", "Punto de foto"), ("GAS", "Gastronomía: almuerzo, restaurante, cocina típica"), ("ALO", "Alojamiento / pernocte"),
 ("FRO", "Paso fronterizo: aduana, migraciones, hito"), ("CMB", "Combustible"), ("SAL", "Salud / emergencias / policía"),
 ("APR", "Área protegida: entrada o límite"), ("ALI", "Aliado / prestador"), ("OTR", "Otro / a identificar"),
]
# código, nombre, lat, lon, alias PDA-POI, origen, qué relevar
POI = [
 ("AMO-ALO-01", "Tierras Mágicas (complejo de origen, Moquehue)", -38.901100, -71.290900, "—", "CONF (sistema de reservas TM)", "Punto de salida: hora de partida, estacionamiento, carga de equipos"),
 ("R-ACC-01", "Acceso RP13/RP12 (Paso del Arco)", -38.902440, -71.064667, "PDA-POI-001", "CONF titular", "Foto de la intersección, cartelería y estado de la calzada"),
 ("R-MIR-01", "Vista del Aluminé", -38.896102, -71.056230, "PDA-POI-023", "EXT wpt 012", "Panorámica; lugar para detenerse fuera de la calzada"),
 ("R-ACC-02", "Cruce N (RP12 / camino desde el este)", -38.810607, -71.057450, "—", "INF (GPX)", "Foto del cruce; señalización; visibilidad"),
 ("O-TRQ-01", "Tranquera 1", -38.832922, -71.058162, "PDA-POI-002", "CONF titular", "Tipo de cierre, ancho, visibilidad al salir a la RP12"),
 ("O-BAS-01", "Base 1 — Inicio (quincho)", -38.832050, -71.066724, "PDA-POI-003", "CONF titular", "Exterior, interior, cocina, baño, agua, energía, señal celular"),
 ("O-BAS-03", "Base 3 — Chivero", -38.807993, -71.063218, "PDA-POI-005", "CONF titular", "GRABAR el camino de llegada; corrales, espacios para chicos"),
 ("O-OTR-01", "CP (a identificar)", -38.806765, -71.061762, "PDA-POI-010", "EXT wpt 003", "Identificar qué es; foto"),
 ("O-MIR-01", "Cima", -38.802437, -71.058298, "PDA-POI-009", "EXT wpt 003", "Panorámica 360°; acceso"),
 ("O-TRQ-02", "Entrada campo mecánico", -38.805388, -71.058735, "PDA-POI-011", "EXT wpt 024", "¿Tranquera desde la RP12? Lado de la ruta"),
 ("O-LIM-01", "Punto límite campo (¿Cerro Piñihue?)", -38.818238, -71.103710, "PDA-POI-012", "EXT wpt 003", "¿Alambrado, mojón o cumbre?"),
 ("E-BAS-02", "Base 2 — Vaquero", -38.814204, -71.050709, "PDA-POI-004", "CONF titular", "Infraestructura, fogón, agua, sombra; por dónde se cruza la RP12"),
 ("E-PTE-01", "Puente sobre el río (¿Arroyo del Arco?)", -38.811902, -71.032685, "PDA-POI-020", "EXT wpt 013", "Nombre del curso; estructura y carga del puente"),
 ("E-VAD-01", "Vado del río", -38.814332, -71.030565, "—", "EXT wpt 013", "Lecho, profundidad del día, marcas de crecida"),
 ("E-AGU-01", "Vertiente", -38.825382, -71.022712, "PDA-POI-022", "EXT wpt 013", "Caudal; ¿dentro del campo?"),
 ("N-PAT-01", "Aduana Vieja (Paso del Arco)", -38.791826, -71.058897, "PDA-POI-006", "EXT wpt 003", "Ruinas, estado, relato; ¿dentro del campo?"),
 ("N-VAD-01", "Vado Aduana Vieja", -38.790233, -71.059082, "PDA-POI-007", "EXT wpt 012", "Lecho y profundidad"),
 ("N-FOR-01", "Castillo / Grupo el Arco", -38.792104, -71.070767, "PDA-POI-008", "EXT wpt 003 = 024", "¿Es el arco que da nombre al paso? Fotos desde varios ángulos"),
 ("N-VAD-02", "Vado norte (024)", -38.784122, -71.092310, "PDA-POI-021", "EXT wpt 024", "Lecho y profundidad"),
 ("L-ACC-01", "Entrada Pilhue", -38.836738, -71.096347, "PDA-POI-014", "EXT wpt 010", "Tipo de acceso; tranquera"),
 ("L-LAG-01", "Laguna Pilhue", -38.836408, -71.097463, "PDA-POI-013", "EXT wpt 012", "Costa, acceso; ¿dentro del campo?"),
 ("L-LAG-02", "Laguna Corazón", -38.826952, -71.124900, "PDA-POI-015", "EXT wpt 012", "Fotos; titularidad"),
 ("L-ARB-01", "Araucaria Guacha", -38.824605, -71.153913, "PDA-POI-019", "EXT wpt 012", "Fotos"),
 ("L-LAG-03", "Laguna Escondida", -38.817470, -71.164700, "PDA-POI-018", "EXT wpt 012", "Fotos"),
 ("L-VAD-01", "Vado Laguna del Arco", -38.803313, -71.169027, "PDA-POI-017", "EXT wpt 012", "Lecho y profundidad"),
 ("L-LAG-04", "Laguna del Arco", -38.804152, -71.171810, "PDA-POI-016", "EXT wpt 012", "Fotos; titularidad"),
 ("ABM-CER-01", "Batea Mahuida (punto más alto de la traza 020; no es la cumbre)", -38.815728, -71.185668, "PDA-POI-024 · X-CER-01", "INF (GPX)", "Solo con autorización de la Comunidad Puel"),
 ("P-CER-01", "Cerro Piñihue (cumbre)", None, None, "PDA-POI-025", "CONF titular, sin coordenada", "Marcar cumbre y pie; ¿mirador?"),
 ("P-LIM-01", "Costa del Arroyo del Arco", None, None, "PDA-POI-026", "CONF titular, sin coordenada", "Un punto cada ~500 m (P-LIM-01a, 01b…)"),
 ("P-PUE-01", "Puesto del Arroyo del Arco", None, None, "PDA-POI-029", "CONF titular, sin coordenada", "Estado, acceso, uso posible"),
 ("P-LAG-01", "Lagunas Norte", None, None, "PDA-POI-027", "CONF titular, sin coordenada", "Un punto por laguna (P-LAG-01a, 01b…)"),
 ("P-MIR-01", "Mirador de las antenas", None, None, "PDA-POI-028", "CONF titular, sin coordenada", "Panorámica; señal celular"),
 ("P-TRQ-01", "Otras tranqueras", None, None, "PDA-POI-030", "CONF titular, sin coordenada", "Una por tranquera"),
 ("P-CRZ-01", "Cruces de la RP12 usados entre sectores", None, None, "PDA-POI-030", "CONF titular (existen)", "Visibilidad en ambos sentidos, banquina, pendiente"),
]
# Jornadas: (código, título, objetivo, secuencia de puntos, puntos P a buscar, notas)
JORNADAS = [
 ("REL-D0", "Traslado desde Tierras Mágicas",
  "Medir tiempos reales del traslado complejo → acceso → Tranquera 1 → Inicio y regreso, por estación (bloque R0).",
  ["AMO-ALO-01", "R-ACC-01", "R-MIR-01", "O-TRQ-01", "O-BAS-01", "AMO-ALO-01"],
  [],
  "Anotar hora en cada punto (ida y vuelta). Repetir en invierno con 4x4. Marcar puntos de encuentro posibles y lugares para detenerse fuera de la calzada."),
 ("REL-D1", "Acceso, RP12 y sector oeste núcleo",
  "Documentar la llegada del cliente y las bases 1 y 3; grabar el camino a Chivero.",
  ["R-ACC-01", "R-MIR-01", "O-TRQ-01", "O-BAS-01", "O-BAS-03", "O-OTR-01", "O-MIR-01", "O-TRQ-02", "R-ACC-02", "O-BAS-01"],
  ["P-TRQ-01", "P-CRZ-01"],
  "Grabar como tramo 'RP12' desde R-ACC-01 hasta O-TRQ-01. Marcar cada tranquera y cada lugar donde un convoy podría cruzar la RP12."),
 ("REL-D2", "Sector este: Vaquero y Arroyo del Arco",
  "Documentar la Base 2, el cruce de la RP12 hacia el este y la costa del Arroyo del Arco (límite este).",
  ["O-BAS-01", "R-ACC-02", "E-BAS-02", "E-PTE-01", "E-VAD-01", "E-AGU-01", "O-BAS-01"],
  ["P-CRZ-01", "P-LIM-01", "P-PUE-01"],
  "Vados en época de deshielo: revisar a pie antes de cruzar y no cruzar con corriente fuerte. Costa del arroyo: un punto cada ~500 m."),
 ("REL-D3", "Norte: Aduana Vieja, Castillo y Lagunas Norte",
  "Relevar el patrimonio y la formación que podrían dar identidad al lugar; ubicar las lagunas del norte y el mirador de las antenas.",
  ["O-BAS-01", "O-MIR-01", "N-PAT-01", "N-VAD-01", "N-FOR-01", "N-VAD-02", "O-BAS-01"],
  ["P-LAG-01", "P-MIR-01"],
  "Confirmar si estos puntos están dentro del campo. La ubicación de las Lagunas Norte y del mirador la conoce el titular: marcarlas al pasar."),
 ("REL-D4", "Oeste: límite, Cerro Piñihue y Laguna Pilhue",
  "Fijar el límite oeste de referencia y definir si Pilhue es un atractivo propio.",
  ["O-BAS-01", "O-LIM-01", "O-BAS-01", "L-ACC-01", "L-LAG-01", "O-BAS-01"],
  ["P-CER-01"],
  "Marcar alambrados y mojones a lo largo del recorrido. Si el Punto límite campo coincide con el Cerro Piñihue, registrar el código P-CER-01 como alias de O-LIM-01."),
 ("REL-D5", "Lagunas regionales y Batea Mahuida (opcional)",
  "Material de contexto para productos regionales; no es parte del campo hasta que se demuestre lo contrario.",
  ["O-BAS-01", "L-LAG-01", "L-LAG-02", "L-ARB-01", "L-LAG-03", "L-VAD-01", "L-LAG-04", "ABM-CER-01", "O-BAS-01"],
  [],
  "Solo por caminos habilitados. Batea Mahuida: únicamente con autorización de la Comunidad Mapuche Puel; si no la hay, fotografiar desde un lugar público."),
]
V_TRAZA_KMH = 20.0   # supuesto de planificación (XX Circuito campo registró ~17 km/h en huella; rutas 25–46 km/h)
MIN_POR_PUNTO = 15   # fotos + planilla
MIN_POR_P = 30       # búsqueda de un punto sin coordenada

NS = {"g": "http://www.topografix.com/GPX/1/1"}
def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(h))
C = 0.0002; key = lambda p: (round(p[0]/C), round(p[1]/C))
G, P = {}, {}
for f in sorted(os.listdir(sys.argv[1])):
    r = ET.parse(os.path.join(sys.argv[1], f)).getroot()
    pts = [(float(p.get("lat")), float(p.get("lon"))) for p in r.iterfind(".//g:trkpt", NS)]
    for i, p in enumerate(pts):
        k = key(p); P.setdefault(k, p)
        if i and hav(pts[i-1], p) <= 0.2:
            k0 = key(pts[i-1])
            if k0 != k: G.setdefault(k0, set()).add(k); G.setdefault(k, set()).add(k0)
for k in list(G):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            k2 = (k[0]+dx, k[1]+dy)
            if k2 != k and k2 in G: G[k].add(k2); G[k2].add(k)
def nearest(pt):
    k = min(G, key=lambda k: hav(P[k], pt)); return k, hav(P[k], pt)
def route(a, b):
    ka, da = nearest(a); kb, db = nearest(b)
    if da > 0.15 or db > 0.15:
        return hav(a, b) * 1.4, [a, b], True
    dist = {ka: 0}; prev = {}; h = [(0, ka)]
    while h:
        d, u = heapq.heappop(h)
        if u == kb: break
        if d > dist[u]: continue
        for v in G[u]:
            nd = d + hav(P[u], P[v])
            if nd < dist.get(v, 9e9): dist[v] = nd; prev[v] = u; heapq.heappush(h, (nd, v))
    if kb not in dist: return hav(a, b) * 1.4, [a, b], True
    path = [kb]
    while path[-1] != ka: path.append(prev[path[-1]])
    return dist[kb] + da + db, [a] + [P[k] for k in path[::-1]] + [b], False

out = sys.argv[2]; os.makedirs(out, exist_ok=True)
IDX = {p[0]: p for p in POI}
res = {"zonas": ZONAS, "territorios": TERRITORIOS, "tipos": TIPOS, "poi": POI, "jornadas": [], "supuestos": {"v_kmh": V_TRAZA_KMH, "min_punto": MIN_POR_PUNTO, "min_P": MIN_POR_P}}
for code, tit, obj, seq, buscar, notas in JORNADAS:
    legs = []; geom = []; tot = 0.0
    full = seq  # la secuencia ya incluye el regreso a la base
    for a, b in zip(full[:-1], full[1:]):
        pa, pb = IDX[a], IDX[b]
        km, g, est = route((pa[2], pa[3]), (pb[2], pb[3]))
        legs.append({"de": a, "a": b, "km": round(km, 2), "estimado_sin_traza": est})
        tot += km; geom += g
    h_mov = tot / V_TRAZA_KMH; h_pts = (len(set(seq) - {"O-BAS-01"} if seq[0] == "O-BAS-01" else set(seq)) * MIN_POR_PUNTO + len(buscar) * MIN_POR_P) / 60
    res["jornadas"].append({"codigo": code, "titulo": tit, "objetivo": obj, "secuencia": seq, "buscar": buscar, "notas": notas,
                            "tramos": legs, "km_total": round(tot, 1), "h_conduccion": round(h_mov, 1), "h_puntos": round(h_pts, 1),
                            "h_total": round(h_mov + h_pts, 1), "geom": geom[::2]})
    # GPX por jornada: waypoints en orden + ruta
    L = ['<?xml version="1.0" encoding="UTF-8"?>', f'<gpx version="1.1" creator="Paso del Arco - hoja de ruta" xmlns="http://www.topografix.com/GPX/1/1">',
         f'<metadata><name>{escape(code + " " + tit)}</name><desc>{escape(obj)}</desc></metadata>']
    vis = list(dict.fromkeys(seq))
    for n, c in enumerate(vis, 1):
        p = IDX[c]
        L.append(f'<wpt lat="{p[2]:.6f}" lon="{p[3]:.6f}"><name>{escape(f"{n:02d} {c} {p[1]}")}</name><desc>{escape(p[6])}</desc><sym>Flag</sym></wpt>')
    L.append(f'<rte><name>{escape(code)}</name>')
    for n, c in enumerate(seq, 1):
        p = IDX[c]; L.append(f'<rtept lat="{p[2]:.6f}" lon="{p[3]:.6f}"><name>{escape(c)}</name></rtept>')
    L.append("</rte>")
    L.append(f'<trk><name>{escape(code + " recorrido sugerido (sobre trazas del titular)")}</name><trkseg>')
    for la, lo in geom[::2]: L.append(f'<trkpt lat="{la:.6f}" lon="{lo:.6f}"></trkpt>')
    L.append("</trkseg></trk></gpx>")
    open(os.path.join(out, f"{code}_{tit.split(':')[0].replace(' ', '_').replace(',', '')[:40]}.gpx"), "w", encoding="utf-8").write("\n".join(L))
    print(code, tit, "km", round(tot, 1), "h_cond", round(h_mov, 1), "h_pts", round(h_pts, 1), "estimados:", [l["de"] + ">" + l["a"] for l in legs if l["estimado_sin_traza"]])
# GPX con todos los puntos codificados
L = ['<?xml version="1.0" encoding="UTF-8"?>', '<gpx version="1.1" creator="Paso del Arco - codificación v1" xmlns="http://www.topografix.com/GPX/1/1">',
     '<metadata><name>PDA puntos codificados v1</name><desc>Formato ZONA-TIPO-NN. No representa límites ni accesos autorizados.</desc></metadata>']
for c, n, la, lo, al, o, q in POI:
    if la is None: continue
    L.append(f'<wpt lat="{la:.6f}" lon="{lo:.6f}"><name>{escape(c + " " + n)}</name><desc>{escape(f"Alias: {al}. Origen: {o}. Relevar: {q}")}</desc></wpt>')
L.append("</gpx>")
open(os.path.join(out, "PDA_puntos_codificados_v1.gpx"), "w", encoding="utf-8").write("\n".join(L))
json.dump(res, open(os.path.join(out, "hoja_ruta.json"), "w"), ensure_ascii=False, indent=1)
