# -*- coding: utf-8 -*-
"""Propuesta de travesías 1, 3 y 5 días + codificación de rutas para Wikiloc.
Uso: propuesta_travesias.py <dir_gpx> <hoja_ruta.json> <out_dir>"""
import sys, os, math, heapq, json
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

GDIR, HJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
HR = json.load(open(HJ)); IDX = {p[0]: p for p in HR["poi"]}
NS = {"g": "http://www.topografix.com/GPX/1/1"}
V_KMH = 25.0; MIN_PUNTO = 20; MIN_ALMUERZO = 90

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(h))
C = 0.0002; key = lambda p: (round(p[0]/C), round(p[1]/C))
G, P, TR = {}, {}, []
for f in sorted(os.listdir(GDIR)):
    r = ET.parse(os.path.join(GDIR, f)).getroot()
    pts = [(float(p.get("lat")), float(p.get("lon"))) for p in r.iterfind(".//g:trkpt", NS)]; TR.append(pts)
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
    if da > 0.15 or db > 0.15: return hav(a, b) * 1.4, [a, b], True
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

# ------------------------------------------------------------------ rutas de un día (RUT) y travesías (TRV)
# secuencia: (código de punto, actividad en el punto, minutos de parada)
RUTAS = {
 "RUT-PDA-01": ("Travesía del Campo — día completo", "Campo (sectores oeste y este) + Aduana Vieja", [
    ("AMO-ALO-01", "Salida desde Tierras Mágicas / Milenka (retiro en la cabaña)", 0),
    ("R-MIR-01", "Mirador Vista del Aluminé (primera parada, fotos)", 15),
    ("O-TRQ-01", "Ingreso al campo por la Tranquera 1", 5),
    ("O-BAS-01", "Base 1 Inicio: bienvenida, briefing de seguridad, infusiones", 30),
    ("O-LIM-01", "Ramal oeste hasta el Punto límite (¿Cerro Piñihue?): panorámica", 25),
    ("O-MIR-01", "Cima: mirador sobre el campo", 20),
    ("N-PAT-01", "Aduana Vieja: historia del Paso del Arco", 25),
    ("N-FOR-01", "Castillo / Grupo el Arco: formación rocosa", 20),
    ("O-BAS-01", "Almuerzo de campo en el quincho de Base 1 Inicio", MIN_ALMUERZO),
    ("AMO-ALO-01", "Regreso al complejo", 0)]),
 "RUT-PDA-02": ("Campo oeste y Base 3 Chivero", "Campo oeste", [
    ("AMO-ALO-01", "Salida desde el complejo", 0),
    ("O-TRQ-01", "Ingreso por la Tranquera 1", 5),
    ("O-BAS-01", "Base 1 Inicio: briefing", 20),
    ("O-LIM-01", "Ramal oeste hasta el Punto límite (¿Cerro Piñihue?)", 25),
    ("O-BAS-03", "Base 3 Chivero: vida de campo", 30),
    ("O-MIR-01", "Cima: mirador", 20),
    ("O-BAS-01", "Almuerzo en el quincho de Base 1 Inicio", MIN_ALMUERZO),
    ("AMO-ALO-01", "Regreso al complejo", 0)]),
 "RUT-PDA-03": ("Norte histórico: Aduana Vieja y el Arco", "Campo + sector norte", [
    ("AMO-ALO-01", "Salida desde el complejo", 0),
    ("R-MIR-01", "Vista del Aluminé", 10),
    ("O-TRQ-01", "Tranquera 1", 5),
    ("O-MIR-01", "Cima", 15),
    ("N-PAT-01", "Aduana Vieja", 30),
    ("N-VAD-01", "Vado Aduana Vieja (según caudal)", 15),
    ("N-FOR-01", "Castillo / Grupo el Arco", 25),
    ("O-BAS-01", "Almuerzo en el quincho de Base 1 Inicio", MIN_ALMUERZO),
    ("AMO-ALO-01", "Regreso al complejo", 0)]),
 "RUT-PDA-04": ("Campo este: Vaquero y el río (¿Arroyo del Arco?)", "Campo este", [
    ("AMO-ALO-01", "Salida desde el complejo", 0),
    ("O-TRQ-01", "Tranquera 1", 5),
    ("O-BAS-01", "Base 1 Inicio: briefing", 20),
    ("E-BAS-02", "Base 2 Vaquero (cruce de la RP12 con procedimiento)", 30),
    ("E-PTE-01", "Puente sobre el río", 15),
    ("E-VAD-01", "Vado del río (según caudal)", 15),
    ("E-AGU-01", "Vertiente", 15),
    ("O-BAS-01", "Almuerzo en el quincho de Base 1 Inicio", MIN_ALMUERZO),
    ("AMO-ALO-01", "Regreso al complejo", 0)]),
 "RUT-AR-01": ("Lagunas y araucarias del oeste", "Zona AR (autorizaciones PEND)", [
    ("AMO-ALO-01", "Salida desde el complejo", 0),
    ("L-LAG-01", "Laguna Pilhue", 25),
    ("L-LAG-02", "Laguna Corazón", 25),
    ("L-ARB-01", "Araucaria Guacha", 15),
    ("L-LAG-03", "Laguna Escondida: almuerzo frío / picnic sin fuego", MIN_ALMUERZO),
    ("L-LAG-04", "Laguna del Arco", 30),
    ("AMO-ALO-01", "Regreso al complejo", 0)]),
 "RUT-AR-02": ("Volcán Batea Mahuida (solo con autorización de la Comunidad Puel)", "Zona AR, territorio comunitario", [
    ("AMO-ALO-01", "Salida desde el complejo", 0),
    ("ABM-CER-01", "Batea Mahuida: punto alto registrado (no es la cumbre); visita guiada por la comunidad", 120),
    ("AMO-ALO-01", "Regreso al complejo; tarde libre en el lago", 0)]),
}
# FORZAR_ACCESO: los traslados al campo van y vuelven por el acceso confirmado RP13/RP12 (no por caminos de terceros)
for _c, (_n, _a, _seq) in RUTAS.items():
    if _c.startswith("RUT-PDA"):
        if _seq[1][0] != "R-ACC-01": _seq.insert(1, ("R-ACC-01", "Acceso RP13/RP12 (Paso del Arco): se toma la RP12", 0))
        _seq.insert(len(_seq) - 1, ("R-ACC-01", "Acceso RP13/RP12: regreso por la RP13", 0))
TRAVESIAS = [
 ("PLAN-1", "RUT-PDA-01", "1 día", "Travesía del Campo", "Excursión de día completo para huéspedes alojados en Tierras Mágicas o Milenka (cualquier estadía).",
  [("D1", "RUT-PDA-01", None)], 0),
 ("PLAN-3", "TRV-AR-01", "3 días · 3 noches", "Campo, lagunas y Paso del Arco",
  "Llegada la tarde anterior (check-in 15:00), tres días de travesía y salida al terminar el tercer día. 3 noches: cumple la estadía mínima de temporada Alta y Alta Premium.",
  [("D1", "RUT-PDA-02", None), ("D2", "RUT-AR-01", "RUT-PDA-04"), ("D3", "RUT-PDA-03", None)], 3),
 ("PLAN-5", "TRV-AR-02", "5 días · 5 noches", "Gran Travesía Paso del Arco",
  "Llegada la tarde anterior, cinco días de travesía (uno opcional de lago) y salida al terminar el quinto día. 5 noches: cumple incluso la estadía mínima de Fin de año.",
  [("D1", "RUT-PDA-02", None), ("D2", "RUT-PDA-04", None), ("D3", "RUT-AR-01", "RUT-PDA-01"), ("D4", "RUT-PDA-03", None), ("D5", "RUT-AR-02", "LAGO")], 5),
]

def calc(code):
    nombre, ambito, seq = RUTAS[code]
    legs, geom, t, tot = [], [], 9 * 60, 0.0
    rows = [(seq[0][0], seq[0][1], 0.0, 0.0, "09:00")]
    for (a, _, _), (b, act, stop) in zip(seq[:-1], seq[1:]):
        pa, pb = IDX[a], IDX[b]
        km, g, est = route((pa[2], pa[3]), (pb[2], pb[3]))
        tot += km; geom += g; t += km / V_KMH * 60
        rows.append((b, act, km, tot, f"{int(t//60):02d}:{int(t%60):02d}" + (" *" if est else "")))
        t += stop
    h_veh = tot / V_KMH
    return {"codigo": code, "nombre": nombre, "ambito": ambito, "filas": rows, "km": round(tot, 1), "h_veh": round(h_veh, 1),
            "fin": f"{int(t//60):02d}:{int(t%60):02d}", "geom": geom}
R = {c: calc(c) for c in RUTAS}
for c, r in R.items(): print(c, r["km"], "km", r["h_veh"], "h veh; fin", r["fin"])

k_ = math.cos(math.radians(38.85))
def mapa(code, fname):
    r = R[code]; pts = [IDX[c] for c, *_ in RUTAS[code][2]]
    lats = [p[2] for p in pts] + [g[0] for g in r["geom"]]; lons = [p[3] for p in pts] + [g[1] for g in r["geom"]]
    pad = 0.008; ext = (min(lats)-pad, max(lats)+pad, min(lons)-pad/k_, max(lons)+pad/k_)
    w = 7.0; h = max(3.6, min(w * (ext[1]-ext[0]) / ((ext[3]-ext[2]) * k_), 8))
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    for t in TR:
        ys, xs = zip(*t); ax.plot(xs, ys, color="#cfcfcf", lw=0.6, zorder=1)
    ys, xs = zip(*r["geom"]); ax.plot(xs, ys, color="#ff7f00", lw=2.4, zorder=2, label=code)
    seen = []
    for c, *_ in RUTAS[code][2]:
        if c in seen: continue
        seen.append(c); p = IDX[c]
        ax.plot(p[3], p[2], "o", ms=8, color="#1b7837" if len(c.split("-")[0]) == 1 else "#762a83", mec="white", zorder=4)
        ax.annotate(f"{len(seen)} {c}", (p[3], p[2]), fontsize=7, weight="bold", xytext=(5, 4), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8), zorder=5)
    ax.set_xlim(ext[2], ext[3]); ax.set_ylim(ext[0], ext[1]); ax.set_aspect(1 / k_); ax.tick_params(labelsize=6); ax.grid(True, lw=0.3, alpha=0.5)
    x0 = ext[2] + (ext[3]-ext[2]) * 0.04; y0 = ext[0] + (ext[1]-ext[0]) * 0.04; dl = 2 / (111.32 * k_)
    ax.plot([x0, x0 + dl], [y0, y0], "k-", lw=3); ax.annotate("2 km", (x0, y0), xytext=(0, 4), textcoords="offset points", fontsize=7)
    ax.set_title(f"{code} — {RUTAS[code][0]}", fontsize=9); ax.legend(loc="upper right", fontsize=7)
    fig.savefig(fname, bbox_inches="tight"); plt.close(fig)

def gpx(code, fname, titulo=None):
    r = R[code]; seq = RUTAS[code][2]
    L = ['<?xml version="1.0" encoding="UTF-8"?>', '<gpx version="1.1" creator="Paso del Arco - propuesta de travesías" xmlns="http://www.topografix.com/GPX/1/1">',
         f'<metadata><name>{escape(titulo or code + " " + RUTAS[code][0])}</name><desc>{escape("Ruta PROPUESTA para relevar. Recorrido sugerido sobre las trazas del titular; no es una ruta aprobada ni autorizada.")}</desc></metadata>']
    seen = []
    for c, act, _ in seq:
        if c in seen: continue
        seen.append(c); p = IDX[c]
        L.append(f'<wpt lat="{p[2]:.6f}" lon="{p[3]:.6f}"><name>{escape(f"{len(seen):02d} {c} {p[1]}")}</name><desc>{escape(act)}</desc></wpt>')
    L.append(f"<rte><name>{escape(code)}</name>")
    for c, _, _ in seq:
        p = IDX[c]; L.append(f'<rtept lat="{p[2]:.6f}" lon="{p[3]:.6f}"><name>{escape(c)}</name></rtept>')
    L.append("</rte>")
    L.append(f"<trk><name>{escape(code + ' recorrido sugerido')}</name><trkseg>")
    for la, lo in r["geom"][::2]: L.append(f'<trkpt lat="{la:.6f}" lon="{lo:.6f}"></trkpt>')
    L.append("</trkseg></trk></gpx>")
    open(fname, "w", encoding="utf-8").write("\n".join(L))

GDIR_OUT = os.path.join(OUT, "gpx_rutas"); os.makedirs(GDIR_OUT, exist_ok=True)
MAPDIR = os.path.join(OUT, "mapas"); os.makedirs(MAPDIR, exist_ok=True)
for c in RUTAS:
    mapa(c, os.path.join(MAPDIR, f"{c}.png")); gpx(c, os.path.join(GDIR_OUT, f"{c}.gpx"))

# ------------------------------------------------------------------ documento
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)
for s in doc.sections: s.left_margin = s.right_margin = Cm(1.8); s.top_margin = s.bottom_margin = Cm(1.6)
def shade(c, col):
    pr = c._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), col); pr.append(sh)
def T(h, rows, w, size=8):
    t = doc.add_table(rows=1, cols=len(h)); t.style = "Table Grid"; t.autofit = False
    for i, x in enumerate(h):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(x); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "1F3A2E")
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""; r = cs[i].paragraphs[0].add_run("" if v is None else str(v)); r.font.size = Pt(size)
    for i, x in enumerate(w): t.columns[i].width = Cm(x)
    for row in t.rows:
        for i, x in enumerate(w): row.cells[i].width = Cm(x)
    doc.add_paragraph(); return t
def H(t, l=1): doc.add_heading(t, level=l)
def Pp(t, b=False, i=False):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = b; r.italic = i; return p
def B(t, lab=None):
    p = doc.add_paragraph(style="List Bullet")
    if lab: r = p.add_run(lab + " "); r.bold = True
    p.add_run(t)
def fmt(x): return f"{x:.1f}".replace(".", ",")

p = doc.add_paragraph(); r = p.add_run("PASO DEL ARCO ADVENTURE"); r.bold = True; r.font.size = Pt(20); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)
p = doc.add_paragraph(); r = p.add_run("Propuesta de Travesías — planes de 1, 3 y 5 días · Codificación de rutas para Wikiloc"); r.font.size = Pt(13)
Pp("Versión 1.1 · 16/11/2026 · Propuesta de producto para relevar y validar. Las rutas son PROPUESTAS sobre las trazas del titular: no están aprobadas, medidas comercialmente ni autorizadas. Sin precios propios: se muestra la referencia de mercado informada por el titular.", i=True)

H("1. La travesía en una frase")
Pp("Travesías 4x4 guiadas en un campo privado de montaña y en la zona de Paso del Arco, para grupos de 1 a 4 personas que se alojan en Tierras Mágicas o Milenka, con salidas compartidas, almuerzo de campo y todo resuelto desde la cabaña.", b=True)
T(["Elemento", "Definición"], [
    ("Quién opera", "Sociedad de travesías Tierras Mágicas – Milenka"),
    ("Para quién", "Huéspedes de los dos complejos; grupos de 1 a 4 personas (CONF). Salidas compartidas entre ambos complejos (CONF)."),
    ("Dónde", "Campo (dividido por la RP12, bases Inicio, Vaquero y Chivero) y zona aledaña (lagunas, Aduana Vieja, Batea Mahuida con autorización)."),
    ("Punto de partida", "Tierras Mágicas / Milenka (≈40 m entre sí). Traslado ≈27,5 km hasta el acceso RP13/RP12 y ≈34–37 km hasta la Tranquera 1 (INF)."),
    ("Diferencial", "Acceso a un campo privado, salidas desde la cabaña, grupos chicos, almuerzo de campo, 4x4 responsable (huellas fijas, sin áreas protegidas)."),
    ("Referencia de mercado", "Prestadores similares: travesía de 5 noches a USD 1.000 por persona y por día (USD 5.000), con guía, alojamiento, desayuno, almuerzo y cena (CONF titular). Los planes más cortos, proporcionales."),
], [3.5, 14])

H("2. Qué incluye cada plan")
T(["Incluye", "Plan 1 día", "Plan 3 días", "Plan 5 días", "Estado"], [
    ("Guía de travesía habilitado", "✔", "✔", "✔", "Requisito legal PEND (capacitación municipal 4x4)"),
    ("Vehículo 4x4 con conductor habilitado, combustible y traslado desde la cabaña", "✔", "✔", "✔", "Aliado habilitado al inicio"),
    ("Briefing de seguridad, radio, botiquín, kit de recuperación", "✔", "✔", "✔", "Equipamiento Etapa 0"),
    ("Seguro de accidentes personales y responsabilidad civil", "✔", "✔", "✔", "Cotización PEND"),
    ("Infusiones, agua y snacks durante la travesía", "✔", "✔", "✔", ""),
    ("Almuerzo de campo (quincho de Base 1 Inicio o picnic sin fuego)", "✔", "✔ × 3", "✔ × 5", "Quién cocina y habilitación PEND; régimen de fuego"),
    ("Alojamiento en cabaña de Tierras Mágicas o Milenka", "— (ya alojados)", "3 noches", "5 noches", "Según cuadro tarifario común (CONF)"),
    ("Desayuno", "—", "✔ × 3", "✔ × 5", "Los complejos hoy no lo ofrecen: canasta en la cabaña o servicio a definir (PEND)"),
    ("Cena (incluye cena de bienvenida la noche de llegada)", "—", "✔ × 3", "✔ × 5", "Cocina propia, catering o restaurante aliado (PEND)"),
    ("Tina caliente, sauna, kayaks y stand up del complejo", "Según estadía", "✔", "✔", "Ya incluidos en la estadía (CONF; con turnos)"),
    ("Mapa y ficha del recorrido; fotos del día", "✔", "✔", "✔", "Fotos: opcional"),
], [6.4, 2.3, 2.3, 2.3, 4.2], size=7.5)
Pp("No incluye: traslado hasta Moquehue; bebidas alcohólicas; pases o servicios de terceros (p. ej. Batea Mahuida); propinas; equipo personal; gastos personales.", i=True)
Pp("Requisitos para el pasajero (a definir con el seguro y el guía): edad mínima, condición física baja–media, ropa de abrigo y calzado cerrado, protector solar, declaración de salud y aceptación de riesgos.", i=True)

H("3. Plan 1 día — RUT-PDA-01 «Travesía del Campo»")
r1 = R["RUT-PDA-01"]
Pp(TRAVESIAS[0][4])
Pp(f"≈{fmt(r1['km'])} km en total (incluye ≈55 km de traslado ida y vuelta por la RP13 hasta el acceso) · ≈{fmt(r1['h_veh'])} h de vehículo · salida 09:00, regreso estimado {r1['fin']}.", b=True)
doc.add_picture(os.path.join(MAPDIR, "RUT-PDA-01.png"), width=Inches(5.6))
T(["Código", "Parada", "km tramo", "km acum.", "Hora est."], [(c, a, fmt(km), fmt(ac), h) for c, a, km, ac, h in r1["filas"]], [2.4, 9.4, 1.6, 1.6, 1.8], size=7.5)
Pp(f"Horarios de planificación: {int(V_KMH)} km/h promedio (ruta y huella), {MIN_PUNTO}–30 min por parada, {MIN_ALMUERZO} min de almuerzo. Se reemplazan por los tiempos medidos en el relevamiento.", i=True)
B("Si llueve o hay viento fuerte: recorte al circuito Inicio–Cima–Aduana Vieja (sin el ramal al Punto límite). Si el vado o la huella no están transitables: regreso por el mismo camino.", "Alternativa:")
B("La estadía mínima de los complejos (2 a 5 noches según temporada, CONF) impide vender un 'día todo incluido con 1 noche'. El plan de 1 día se ofrece a quienes ya están alojados; la versión todo incluido empieza en el plan de 3 días.", "Por qué no hay 'todo incluido' de 1 día:")

for code, trv, dur, nombre, desc, dias, noches in TRAVESIAS[1:]:
    doc.add_page_break()
    H(f"{'4' if code == 'PLAN-3' else '5'}. Plan {dur} — {trv} «{nombre}»")
    Pp(desc)
    rows = [("Noche de llegada", "Check-in 15:00 en Tierras Mágicas o Milenka · tarde libre en el lago (kayak, stand up, tina) · briefing general · cena de bienvenida", "—", "—")]
    tot = 0.0
    for d, rc, alt in dias:
        rr = R[rc]; tot += rr["km"]
        altt = "" if not alt else (" · Alternativa: " + ("mañana de lago en el complejo y almuerzo de despedida" if alt == "LAGO" else f"{alt} {RUTAS[alt][0]}"))
        rows.append((f"{d} · {trv}.{d}", f"{rc} {RUTAS[rc][0]}{altt}", fmt(rr["km"]), f"09:00–{rr['fin']}"))
    rows.append(("Último día", "Check-out 10:00 con guardado de equipaje; salida después de la travesía", "—", "—"))
    T(["Día", "Ruta y actividad", "km", "Horario est."], rows, [3.2, 10.4, 1.4, 2.5], size=7.5)
    Pp(f"Total ≈{fmt(tot)} km en {len(dias)} días · {noches} noches · desayunos, almuerzos y cenas incluidos ({len(dias)} de cada uno; la primera cena es la de bienvenida).", b=True)
    for d, rc, alt in dias:
        rr = R[rc]
        H(f"{trv}.{d} — {rc} {RUTAS[rc][0]}", 2)
        Pp(f"Ámbito: {RUTAS[rc][1]} · ≈{fmt(rr['km'])} km · ≈{fmt(rr['h_veh'])} h de vehículo · regreso estimado {rr['fin']}.")
        doc.add_picture(os.path.join(MAPDIR, f"{rc}.png"), width=Inches(4.6))
        T(["Código", "Parada", "km acum.", "Hora est."], [(c, a, fmt(ac), h) for c, a, km, ac, h in rr["filas"]], [2.4, 10.6, 1.8, 2.2], size=7.2)
        if rc == "RUT-AR-01":
            B("Las lagunas están fuera del campo (titularidad PEND): sin autorización escrita se reemplaza este día por la alternativa indicada. Vados en época de deshielo: revisar a pie.", "Condición:")
        if rc == "RUT-AR-02":
            B("Solo con acuerdo de la Comunidad Mapuche Puel, que administra Batea Mahuida. Sin acuerdo: mañana de lago en el complejo y almuerzo de despedida.", "Condición:")
        if rc == "RUT-PDA-04":
            B("Vaquero está al este de la RP12: el convoy cruza la ruta por un punto fijo, con guía a pie y señalización.", "Cruce de la RP12:")

doc.add_page_break()
H("6. Comparación de los planes")
cmp_rows = []
for code, trv, dur, nombre, desc, dias, noches in TRAVESIAS:
    km = sum(R[rc]["km"] for _, rc, _ in dias); hv = sum(R[rc]["h_veh"] for _, rc, _ in dias); nd = len(dias)
    cmp_rows.append((f"{code} ({trv})", dur, str(noches), fmt(km), fmt(hv), str(nd), str(nd if noches else 0), f"USD {1000*nd:,}".replace(",", ".") + (" (referencia: 5 noches = USD 5.000)" if nd == 5 else " (proporcional al de 5 noches)")))
T(["Plan", "Duración", "Noches", "km", "h de vehículo", "Almuerzos", "Desayunos y cenas", "Referencia de mercado por persona (proporcional a la travesía de 5 noches)"], cmp_rows, [2.8, 2.4, 1.3, 1.3, 1.6, 1.6, 2, 4.5], size=7.5)
Pp("La referencia (CONF titular) es la de prestadores similares para una travesía de 5 noches: USD 1.000 por persona y por día; los planes de 1 y 3 días se calculan en proporción. NO es un precio propio: incluye alojamiento y pensión completa. El precio se fija después de costear guía, vehículo, comidas, seguro y el alojamiento según el cuadro tarifario común (≈85 mil pesos por persona y noche en temporada Alta con descuento directo y 2,5 personas por cabaña, INF del modelo económico).", i=True)
B("Las salidas son compartidas entre huéspedes de los dos complejos: cada día tiene cupo por vehículo y un mínimo de personas para confirmarse (a definir con costos).", "Salidas:")
B("Verano, otoño y primavera. Invierno: solo con 4x4 en la RP12 (CONF) y productos específicos (prefactibilidad). En noviembre–diciembre, revisar vados por deshielo.", "Temporada:")
B("Clima: se confirma la tarde anterior; si se suspende, se reprograma dentro de la estadía o se reemplaza por la alternativa del día. Cancelación del alojamiento: políticas del complejo (CONF). Cancelación de la travesía: política propia a definir.", "Políticas:")

H("7. Codificación de rutas para relevar con Wikiloc")
Pp("Cada ruta propuesta tiene un GPX (carpeta gpx_rutas) con las paradas numeradas, la ruta y el recorrido sugerido. Se carga en Wikiloc, se sigue en el terreno y se graba una traza NUEVA con el código de la ruta. Así cada relevamiento queda asociado a su ruta sin ambigüedad.")
T(["Qué", "Código / formato", "Ejemplo", "Dónde se escribe en Wikiloc"], [
    ("Ruta de un día", "RUT-ÁMBITO-NN (ámbito: PDA campo · AR Argentina · CL Chile · BI binacional)", "RUT-PDA-01", "—"),
    ("Travesía de varios días", "TRV-ÁMBITO-NN · cada día .D1, .D2…", "TRV-AR-01.D2 = RUT-AR-01", "—"),
    ("Variante de una ruta", "Letra al final", "RUT-PDA-01b (por clima)", "—"),
    ("Traza grabada al relevar una ruta", "REL + código de ruta + fecha", "REL RUT-PDA-01 20261120", "Nombre de la traza"),
    ("Traza grabada explorando (sin ruta)", "REL + jornada + fecha", "REL D1 20261120", "Nombre de la traza"),
    ("Estado y datos de la ruta", "Primera línea de la descripción de la traza", "v1 · Estado: relevada · Temporada: verano · 4x4 · Guía: (nombre)", "Descripción de la traza"),
    ("Puntos de la ruta", "Código de punto ZONA/TERRITORIO-TIPO-NN", "o bas 1 · n pat 1 · l lag 1", "Nombre del waypoint"),
    ("Punto de retorno o evacuación", "Tipo RET", "o ret n1 (camino de salida si se corta la huella)", "Nombre del waypoint"),
    ("Señal de celular o radio", "Tipo COM + intensidad en la descripción", "o com n1 · desc: 'COM: 2 rayas Movistar'", "Nombre + descripción"),
    ("Tiempo en cada parada", "Etiqueta H: en la descripción (llegada–salida)", "H: 10:40–11:05", "Descripción del waypoint"),
], [3.6, 5.6, 4.4, 3.9], size=7.5)
H("Estados de una ruta (en la descripción de la traza)", 2)
T(["Estado", "Significado", "Qué falta para pasar al siguiente"], [
    ("Propuesta", "Diseñada en gabinete (GPX de esta propuesta)", "Recorrerla y grabarla"),
    ("Relevada", "Recorrida y grabada con puntos, fotos y tiempos", "Ficha de ruta, riesgos, autorizaciones"),
    ("Piloto", "Operada con pasajeros reales en el piloto", "Resultados del piloto sin incidentes"),
    ("Aprobada", "Lista para vender", "Revisión anual y por temporada"),
], [2.6, 7.4, 7.5])
H("Qué registrar al relevar cada ruta", 2)
for t_ in ["Hora de salida y llegada en cada parada (etiqueta H:) — reemplaza los horarios estimados.",
           "Puntos de retorno (RET) y señal (COM) a lo largo de la ruta.",
           "Cada cruce de la RP12 como R-CRZ con foto en ambos sentidos.",
           "Tramos difíciles como RSG (pendiente, piedra suelta, barro, vado profundo) con foto.",
           "Lugar del almuerzo y servicios (SRV): sombra, baño, agua.",
           "En la descripción de la traza: estado, temporada, vehículo, conductor, número de personas, clima del día."]:
    B(t_, "☐")
Pp("El importador (scripts/wikiloc_import.py) reconoce los nuevos tipos RET y COM y toma el código de ruta del nombre de la traza.", i=True)

H("8. Qué hay que resolver antes de vender")
T(["Tema", "Para qué plan", "Estado"], [
    ("Relevar y medir cada ruta (tiempos reales, dificultad, puntos de retorno)", "Todos", "Pendiente: relevamiento con Wikiloc"),
    ("Habilitación de guía y vehículo; seguro", "Todos", "PEND"),
    ("Quién prepara desayunos, almuerzos y cenas; habilitación bromatológica; régimen de fuego", "Todos (almuerzo); 3 y 5 días (pensión completa)", "PEND"),
    ("Autorización para las lagunas del oeste", "3 y 5 días (RUT-AR-01)", "PEND; hay alternativa dentro del campo"),
    ("Acuerdo con la Comunidad Puel (Batea Mahuida)", "5 días (RUT-AR-02)", "PEND; hay alternativa de lago"),
    ("Cupo por vehículo y mínimo de personas por salida", "Todos", "PEND (con costos)"),
    ("Precio por plan y política de cancelación de la travesía", "Todos", "PEND (con costos; referencia USD 1.000 por persona y día)"),
    ("Camino a Base 3 Chivero (sin traza)", "RUT-PDA-02", "Grabar en el relevamiento"),
], [8, 4.5, 5], size=8)

H("9. Próximos pasos")
for i, t_ in enumerate(["Relevar primero RUT-PDA-01 (es la base de los tres planes) con su GPX y la traza 'REL RUT-PDA-01 fecha'.",
                        "Relevar RUT-PDA-02, -03 y -04 (todo dentro del campo o del sector norte).",
                        "Gestionar la autorización de las lagunas y el contacto con la Comunidad Puel antes de relevar RUT-AR-01 y RUT-AR-02.",
                        "Definir el servicio de comidas (desayuno, almuerzo de campo, cena) y costearlo.",
                        "Con tiempos y costos reales: fijar precio por plan, cupos y política; preparar la ficha comercial de cada plan para los huéspedes."], 1):
    B(t_, f"{i}.")
doc.save(os.path.join(OUT, "Propuesta_Travesias_Paso_del_Arco_v1_1.docx"))
json.dump({c: {k: v for k, v in r.items() if k != "geom"} for c, r in R.items()}, open(os.path.join(OUT, "rutas_propuestas.json"), "w"), ensure_ascii=False, indent=1)
print("ok")
