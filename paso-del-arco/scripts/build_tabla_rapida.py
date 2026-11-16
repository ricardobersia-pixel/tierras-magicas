# -*- coding: utf-8 -*-
"""Tabla de escritura rápida para Wikiloc. Uso: build_tabla_rapida.py <hoja_ruta.json> <rutas_propuestas.json> <out.docx>"""
import sys, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
HR = json.load(open(sys.argv[1])); RP = json.load(open(sys.argv[2]))
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(9)
for s in doc.sections: s.left_margin = s.right_margin = Cm(1.3); s.top_margin = s.bottom_margin = Cm(1.1)
def shade(c, col):
    pr = c._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), col); pr.append(sh)
def T(h, rows, w, size=8.5, bold_first=True, mono_first=True):
    t = doc.add_table(rows=1, cols=len(h)); t.style = "Table Grid"; t.autofit = False
    for i, x in enumerate(h):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(x); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "1F3A2E")
    for k, row in enumerate(rows):
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""; r = cs[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(size)
            if i == 0 and bold_first: r.bold = True
            if i == 0 and mono_first: r.font.name = "Consolas"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
            if k % 2: shade(cs[i], "F2F2F2")
    for i, x in enumerate(w): t.columns[i].width = Cm(x)
    for row in t.rows:
        for i, x in enumerate(w): row.cells[i].width = Cm(x)
    doc.add_paragraph().paragraph_format.space_after = Pt(0); return t
def H(t):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
def P(t, b=False, i=False, size=None):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = b; r.italic = i; p.paragraph_format.space_after = Pt(2)
    if size: r.font.size = Pt(size)

def rapido(code):
    z, t, n = code.split("-")
    num = n.lstrip("0") or "0"
    return f"{z.lower()} {t.lower()} {num}"

usos = {}
for rc, r in RP.items():
    for c, *_ in r["filas"]:
        usos.setdefault(c, [])
        if rc not in usos[c]: usos[c].append(rc)

p = doc.add_paragraph(); r = p.add_run("TABLA DE ESCRITURA RÁPIDA EN WIKILOC"); r.bold = True; r.font.size = Pt(15); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)
P("Paso del Arco Adventure · Sociedad de travesías Tierras Mágicas – Milenka · v1 · 16/11/2026", i=True)
P("Regla: se escribe ZONA TIPO NÚMERO en minúsculas, con espacios y sin ceros (ej. o bas 1). Después se puede agregar el nombre. El importador lo convierte al código (O-BAS-01).", b=True)

H("1. Puntos conocidos: qué escribir")
orden = {"A": 0, "O": 1, "E": 2, "N": 3, "L": 4, "R": 5, "C": 6, "P": 7}
pts = sorted(HR["poi"], key=lambda p: (0 if p[0].startswith("AMO") else (6 if len(p[0].split("-")[0]) == 3 else orden.get(p[0][0], 9)), p[0]))
T(["Escribir", "Código", "Punto", "Rutas"],
  [(rapido(c) + (" a/b…" if c.startswith("P-") else ""), c, n.split(" (")[0] if len(n) > 60 else n, ", ".join(x.replace("RUT-", "") for x in usos.get(c, [])) or "—")
   for c, n, la, lo, al, o, q in pts],
  [2.6, 2.6, 9.6, 4.1], size=8)

H("2. Puntos nuevos")
T(["Escribir", "Resultado", "Cuándo"], [
    ("o mir n1", "O-MIR-xx (número asignado al importar)", "Mirador nuevo en el campo oeste; n2, n3… en el mismo día"),
    ("e vad n1", "E-VAD-xx", "Vado nuevo en el campo este"),
    ("o ret n1", "O-RET-xx", "Punto de retorno o evacuación"),
    ("o com n1", "O-COM-xx", "Lugar con (o sin) señal; detalle en COM:"),
    ("r crz n1", "R-CRZ-xx", "Cruce de la RP12 usado por el convoy"),
    ("o rsg n1", "O-RSG-xx", "Punto de riesgo: pendiente, piedra suelta, barro"),
    ("p mir n1", "P-MIR-xx", "No sé en qué zona está"),
    ("cic gas n1", "CIC-GAS-xx", "Fuera del campo: Chile (C) · Icalma (IC) · gastronomía"),
], [2.6, 5.4, 10.9], size=8)

H("3. Tipos (3 letras)")
tp = HR["tipos"]; h2 = (len(tp) + 1) // 2
T(["Tipo", "Qué es", "Tipo", "Qué es"], [(tp[i][0].lower(), tp[i][1], *((tp[i+h2][0].lower(), tp[i+h2][1]) if i + h2 < len(tp) else ("", ""))) for i in range(h2)], [1.4, 8, 1.4, 8.1], size=7.8)

H("4. Zonas y territorios (primera palabra)")
zt = [(z[0].lower(), z[1]) for z in HR["zonas"] if z[0] != "X"] + [(t[0].lower(), f"{t[2]} ({t[1]})") for t in HR["territorios"]]
h3 = (len(zt) + 1) // 2
T(["Escribir", "Dónde", "Escribir", "Dónde"], [(zt[i][0], zt[i][1], *(zt[i+h3] if i + h3 < len(zt) else ("", ""))) for i in range(h3)], [1.6, 7.8, 1.6, 7.9], size=7.8)

H("5. Descripción del punto (etiquetas)")
T(["Escribir", "Significa", "Ejemplo"], [
    ("C:", "¿Dentro del campo? S · N · ?", "C:S"),
    ("A:", "Cómo se llega: 4x4 · 4x2 · pie", "A:4x4"),
    ("E:", "Estado: B · R · M", "E:R"),
    ("H:", "Horario llegada–salida", "H: 10:05–10:40"),
    ("COM:", "Señal de celular o radio", "COM: 2 rayas"),
    ("R:", "Riesgo (siempre al final)", "R: piedra suelta en bajada"),
], [1.8, 7, 10.1], size=8)
P("Ejemplo completo:  C:S A:4x4 E:B H: 11:20–11:45 COM: sin señal vista al lago R: barranco a la derecha", size=8.5)

H("6. Nombre de la traza al relevar cada ruta")
T(["Escribir como nombre de la traza", "GPX a seguir", "Ruta"], [(f"REL {rc} AAAAMMDD", f"{rc}.gpx", r["nombre"]) for rc, r in RP.items()] +
  [("REL D1 AAAAMMDD", "REL-D1 … REL-D5", "Exploración por jornadas (sin ruta)")], [6.2, 3.4, 9.3], size=8)
P("Descripción de la traza (primera línea): v1 · Estado: relevada · Temporada · Vehículo · Conductor · Personas · Clima", size=8.5)
doc.save(sys.argv[3]); print("ok")
