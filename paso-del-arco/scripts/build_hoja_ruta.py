# -*- coding: utf-8 -*-
"""Documento de campo: codificación de puntos + hoja de ruta por jornada con mapas. Uso: build_hoja_ruta.py <dir_gpx> <hoja_ruta.json> <out_dir>"""
import sys, os, math, json
import xml.etree.ElementTree as ET
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NS = {"g": "http://www.topografix.com/GPX/1/1"}
gdir, hj, out = sys.argv[1], sys.argv[2], sys.argv[3]
HR = json.load(open(hj)); IDX = {p[0]: p for p in HR["poi"]}
tracks = []
for f in sorted(os.listdir(gdir)):
    r = ET.parse(os.path.join(gdir, f)).getroot()
    tracks.append([(float(p.get("lat")), float(p.get("lon"))) for p in r.iterfind(".//g:trkpt", NS)])
k = math.cos(math.radians(38.83))
ZCOL = {"A": "#762a83", "C": "#762a83", "R": "#c00000", "O": "#1b7837", "E": "#2166ac", "N": "#8c510a", "L": "#01665e", "X": "#762a83", "P": "#777777"}

def mapa(j, fname, ext=None, sub=""):
    pts = [IDX[c] for c in j["secuencia"]]
    lats = [p[2] for p in pts] + [g[0] for g in j["geom"]]; lons = [p[3] for p in pts] + [g[1] for g in j["geom"]]
    pad = 0.006
    ext = ext or (min(lats)-pad, max(lats)+pad, min(lons)-pad/k, max(lons)+pad/k)
    w = 7.2; h = w * (ext[1]-ext[0]) / ((ext[3]-ext[2]) * k); h = max(3.5, min(h, 9.5))
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    for t in tracks:
        ys, xs = zip(*t); ax.plot(xs, ys, color="#c9c9c9", lw=0.7, zorder=1)
    if j["geom"]:
        ys, xs = zip(*j["geom"]); ax.plot(xs, ys, color="#ff7f00", lw=2.6, zorder=2, label="Recorrido sugerido")
    seen = []
    for c in j["secuencia"]:
        if c in seen: continue
        seen.append(c); p = IDX[c]; z = c[0]
        if not (ext[0] <= p[2] <= ext[1] and ext[2] <= p[3] <= ext[3]): continue
        ax.plot(p[3], p[2], "o", ms=9, color=ZCOL[z], mec="white", zorder=4)
        ax.annotate(f"{len(seen)}  {c}", (p[3], p[2]), fontsize=7.5, weight="bold", xytext=(6, 4), textcoords="offset points", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
    ax.set_xlim(ext[2], ext[3]); ax.set_ylim(ext[0], ext[1]); ax.set_aspect(1 / k)
    ax.tick_params(labelsize=6); ax.grid(True, lw=0.3, alpha=0.5)
    x0 = ext[2] + (ext[3]-ext[2]) * 0.04; y0 = ext[0] + (ext[1]-ext[0]) * 0.04; dl = 1 / (111.32 * k)
    ax.plot([x0, x0 + dl], [y0, y0], "k-", lw=3); ax.annotate("1 km", (x0, y0), xytext=(0, 4), textcoords="offset points", fontsize=7)
    ax.set_title(f"{j['codigo']} — {j['titulo']}{sub}", fontsize=9)
    ax.legend(loc="upper right", fontsize=7)
    fig.savefig(fname, bbox_inches="tight"); plt.close(fig)

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(9.5)
for s in doc.sections: s.left_margin = s.right_margin = Cm(1.6); s.top_margin = s.bottom_margin = Cm(1.5)
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
def P(t, b=False, i=False, size=None):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = b; r.italic = i
    if size: r.font.size = Pt(size)
    return p
def B(t, lab=None):
    p = doc.add_paragraph(style="List Bullet")
    if lab: r = p.add_run(lab + " "); r.bold = True
    p.add_run(t)

p = doc.add_paragraph(); r = p.add_run("PASO DEL ARCO ADVENTURE"); r.bold = True; r.font.size = Pt(18); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)
P("Hoja de ruta del relevamiento de puntos de interés con fotografías · Codificación de puntos v1", b=True, size=12)
P("Versión 1.5 · 16/11/2026 (REL-D0: traslado desde Tierras Mágicas y Milenka, con coordenada de Milenka; nombres adaptados a Wikiloc; territorios fuera del campo: A=Argentina, C=Chile; Batea Mahuida = ABM-CER-01) · Documento de campo para el titular. Distancias calculadas sobre las 24 trazas grabadas por el titular; los tiempos son estimaciones de planificación, no duraciones medidas. No representa límites legales ni accesos autorizados.", i=True)

doc.add_heading("1. Codificación de puntos", level=1)
P("Formato:  ZONA-TIPO-NN   →   ejemplo  O-BAS-01  =  sector Oeste · Base · número 01 (Base 1, Inicio).", b=True)
B("Se lee de izquierda a derecha: dónde está, qué es y cuál es.", "Lectura:")
B("Forma canónica con mayúsculas y guiones (L-LAG-01). En Wikiloc se puede escribir como sea cómodo en el celular: 'l lag 1 Pilhue', 'LLAG01' o 'L-LAG-01' se leen igual; el importador lo normaliza. Ver la Ficha de bolsillo.", "Escritura:")
B("Zona + tipo + N + número del día ('e vad n1'). El número definitivo se asigna al importar.", "Puntos nuevos:")
B("Un código nunca se reutiliza. Si un punto cambia de zona o de nombre, recibe un código nuevo y el anterior queda como alias.", "Estabilidad:")
B("Las bases conservan su número: O-BAS-01 Inicio, E-BAS-02 Vaquero, O-BAS-03 Chivero.", "Bases:")
B("Fuera del campo, la zona se reemplaza por un territorio de 3 letras: A = Argentina, C = Chile + lugar (ej. CIC-GAS-01 almuerzo en Icalma). Ver Ficha de bolsillo v2.", "Fuera del campo:")
B("Los puntos P (sin coordenada) reciben su código definitivo al relevarlos. Si son varios del mismo tipo, se usan sufijos de letra provisorios (P-LAG-01a, P-LAG-01b…).", "Puntos por posicionar:")
doc.add_heading("Zonas", level=2)
T(["Letra", "Zona", "Criterio"], HR["zonas"], [1.5, 3, 13])
doc.add_heading("Tipos", level=2)
T(["Tipo", "Significado", "Tipo", "Significado"], [(HR["tipos"][i][0], HR["tipos"][i][1], *(HR["tipos"][i+10] if i+10 < len(HR["tipos"]) else ("", ""))) for i in range(10)], [1.5, 7, 1.5, 7.5])
doc.add_heading("Códigos de rutas, tramos, relevamientos y fotos", level=2)
T(["Elemento", "Formato", "Ejemplo"], [
    ("Punto", "ZONA-TIPO-NN", "N-PAT-01 Aduana Vieja"),
    ("Tramo entre dos puntos", "PUNTO>PUNTO", "O-BAS-01>O-MIR-01"),
    ("Ruta o circuito de producto", "RUT-ZONA-NN (zona principal del recorrido; M si combina zonas)", "RUT-O-01 Bucle norte; RUT-M-01 Inicio–Vaquero"),
    ("Jornada de relevamiento (traza en Wikiloc)", "REL Dn AAAAMMDD", "REL D1 20261120"),
    ("Foto", "Sin renombrar: se asocia al punto por hora y ubicación (GPS de la cámara activado)", "Adjunta al punto en Wikiloc + original en la galería"),
    ("Descripción del punto", "Etiquetas cortas: C: (dentro del campo S/N/?) A: (4x4/4x2/pie) E: (B/R/M) R: (riesgo)", "C:S A:4x2 E:R R:vado profundo"),
    ("Punto de riesgo nuevo", "ZONA-RSG-NN", "O-RSG-01 Pendiente con piedra suelta"),
], [4.5, 6.5, 6.5])
P("Para armar una ruta nueva alcanza con listar los códigos en orden (ej. RUT-O-01: O-BAS-01 > O-BAS-03 > O-MIR-01 > N-PAT-01 > N-FOR-01 > O-BAS-01). La zona de cada código muestra de un vistazo si la ruta sale del campo (R, N, L o X) y si cruza la RP12 (pasa de O a E).", i=True)

doc.add_heading("2. Catálogo de puntos codificados", level=1)
T(["Código", "Punto", "Coordenada", "Alias anterior", "Origen", "Jornada"],
  [(c, n, "PEND" if la is None else f"{la:.6f}, {lo:.6f}", al, o, next((j["codigo"] for j in HR["jornadas"] if c in j["secuencia"] or c in j["buscar"]), "—"))
   for c, n, la, lo, al, o, q in HR["poi"]], [2, 5.4, 3.4, 2.2, 3, 1.6], size=7.5)

doc.add_heading("3. Resumen de jornadas", level=1)
T(["Jornada", "Recorrido", "Puntos", "Puntos a buscar", "km", "h conducción", "h en puntos", "h total"],
  [(j["codigo"], j["titulo"], len(dict.fromkeys(j["secuencia"])), len(j["buscar"]), j["km_total"], j["h_conduccion"], j["h_puntos"], j["h_total"]) for j in HR["jornadas"]],
  [1.7, 5.5, 1.3, 1.6, 1.3, 1.8, 1.8, 1.4])
P(f"Supuestos: conducción a {HR['supuestos']['v_kmh']:.0f} km/h promedio (XX Circuito campo registró ~17 km/h en huella; la RP12 permite más); {HR['supuestos']['min_punto']} min por punto (fotos + planilla) y {HR['supuestos']['min_P']} min por punto a buscar. No incluye el viaje hasta el acceso ni las paradas largas. REL-D2 y REL-D3 pueden hacerse el mismo día (≈7 h). REL-D5 es opcional y depende de autorizaciones.", i=True)
doc.add_heading("Orden recomendado", level=2)
B("REL-D1 primero: confirma la llegada, la Tranquera 1 y las bases 1 y 3, y graba el camino a Chivero (el único tramo sin traza).")
B("REL-D2 y REL-D3 después: sector este y norte, con los vados (época de deshielo: ver seguridad).")
B("REL-D4: límite oeste y Laguna Pilhue. En los GPX no hay una huella directa entre el Punto límite campo y Pilhue: si existe, grabarla.")
B("REL-D5 al final y solo con autorizaciones.")

for j in HR["jornadas"]:
    doc.add_page_break()
    doc.add_heading(f"{j['codigo']} — {j['titulo']}", level=1)
    P("Objetivo: " + j["objetivo"])
    P(f"≈{j['km_total']} km · ≈{j['h_total']} h (conducción {j['h_conduccion']} h + puntos {j['h_puntos']} h). Inicio y fin: {j['secuencia'][0]} → {j['secuencia'][-1]}.", b=True)
    fn = os.path.join(out, f"mapa_{j['codigo']}.png"); mapa(j, fn)
    doc.add_picture(fn, width=Inches(6.6) if j["codigo"] != "REL-D1" else Inches(3.6))
    if j["codigo"] in ("REL-D1", "REL-D3"):
        fz = os.path.join(out, f"mapa_{j['codigo']}_zoom.png"); mapa(j, fz, ext=(-38.840, -38.783, -71.080, -71.045), sub=" (ampliación)")
        doc.add_picture(fz, width=Inches(5.2))
    rows = []; acum = 0.0; n = 0; seen = set()
    rows.append(("", j["secuencia"][0], IDX[j["secuencia"][0]][1], "0,0", "0,0", "Salida", "☐"))
    for l in j["tramos"]:
        acum += l["km"]; c = l["a"]; p_ = IDX[c]
        first = c not in seen and c != j["secuencia"][0]; seen.add(c)
        rows.append((str(len(seen)) if first else "", c, p_[1], f"{l['km']:.1f}".replace(".", ","), f"{acum:.1f}".replace(".", ","),
                     p_[6] if first else ("Regreso" if c == j["secuencia"][-1] else "Paso"), "☐"))
    T(["Nº", "Código", "Punto", "km tramo", "km acum.", "Qué relevar", "✓"], rows, [0.8, 2, 4.6, 1.4, 1.4, 6.2, 0.8], size=7.5)
    if j["buscar"]:
        P("Puntos a buscar en esta jornada (sin coordenada):", b=True)
        for c in j["buscar"]: B(f"{c} {IDX[c][1]}: {IDX[c][6]}.  ☐")
    P("Notas: " + j["notas"], i=True)

doc.add_page_break()
doc.add_heading("4. Seguridad y lista de control", level=1)
for t in ["Ir con dos vehículos o, como mínimo, avisar a alguien del recorrido y de la hora de regreso.",
          "Comunicación: celular cargado, batería externa; donde no haya señal, radio o comunicador satelital. Anotar dónde hay señal (dato útil para el proyecto).",
          "Vados (noviembre–diciembre, deshielo): revisar a pie antes de cruzar; no cruzar con corriente fuerte o fondo desconocido. Registrar la profundidad del día.",
          "RP12: detenerse siempre fuera de la calzada; los cruces del convoy se fotografían en ambos sentidos.",
          "Fuego: no hacer fuego durante el relevamiento (régimen de prevención de incendios vigente a verificar).",
          "Terceros y comunidades: no ingresar a campos ajenos ni a la zona de Batea Mahuida sin autorización.",
          "Botiquín, kit de recuperación 4x4, agua, abrigo y comida para todo el día."]:
    B(t, "☐")
doc.add_heading("5. Qué se entrega al final", level=1)
for t in ["GPX de cada jornada descargado de Wikiloc (traza 'REL Dn AAAAMMDD'; incluye los puntos con nombre y descripción).",
          "Carpeta de fotos originales sin comprimir (no hace falta renombrarlas).",
          "Opcional: la planilla 19. Si usaste las etiquetas C: A: E: R: en la descripción de cada punto, la planilla se completa sola al importar.",
          "No hace falta una lista aparte de puntos nuevos: salen del GPX."]:
    B(t, "☐")
P("Archivos para el celular: PDA_puntos_codificados_v1.gpx (todos los puntos) y REL-D1 … REL-D5 (.gpx, con puntos numerados, ruta y recorrido sugerido).", i=True)
doc.save(os.path.join(out, "Hoja_de_Ruta_Relevamiento_POI_Paso_del_Arco_v1_5.docx")); print("ok")
