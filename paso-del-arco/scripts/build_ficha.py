# -*- coding: utf-8 -*-
"""Ficha de bolsillo: cómo nombrar puntos en Wikiloc. Uso: build_ficha.py <hoja_ruta.json> <out.docx>"""
import sys, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
HR = json.load(open(sys.argv[1]))
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(9)
for s in doc.sections: s.left_margin = s.right_margin = Cm(1.4); s.top_margin = s.bottom_margin = Cm(1.2)
def shade(c, col):
    pr = c._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), col); pr.append(sh)
def T(h, rows, w, size=8.5):
    t = doc.add_table(rows=1, cols=len(h)); t.style = "Table Grid"; t.autofit = False
    for i, x in enumerate(h):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(x); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "1F3A2E")
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""; r = cs[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(size)
            if i == 0: r.bold = True
    for i, x in enumerate(w): t.columns[i].width = Cm(x)
    for row in t.rows:
        for i, x in enumerate(w): row.cells[i].width = Cm(x)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
def H(t):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E); p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
def P(t, b=False, i=False, size=None):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = b; r.italic = i; p.paragraph_format.space_after = Pt(2)
    if size: r.font.size = Pt(size)

p = doc.add_paragraph(); r = p.add_run("FICHA DE BOLSILLO — Cómo nombrar los puntos en Wikiloc"); r.bold = True; r.font.size = Pt(14); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)
P("Paso del Arco Adventure · Relevamiento con fotos · v2 (incluye rutas fuera del campo y Chile) · 16/11/2026", i=True)

H("1. El nombre del punto: ZONA  TIPO  NÚMERO  (texto libre)")
P("o bas 1 Inicio   =   O-BAS-01   (Oeste · Base · 01)", b=True, size=12)
P("Se puede escribir como resulte cómodo en el celular: minúsculas, con espacios, sin guiones, sin el cero inicial. 'o bas 1', 'OBAS01' y 'O-BAS-01' se leen igual. Después del número se puede agregar texto libre (el nombre del lugar).")
T(["Situación", "Qué escribir", "Ejemplo"], [
    ("Punto que ya existe (está en el GPX de la jornada)", "Su código, tal como aparece en el mapa de Wikiloc", "l lag 1 Pilhue"),
    ("Punto NUEVO", "Zona (o territorio) + tipo + N + número del día", "e vad n1   ·   cic gas n1 cocinería"),
    ("Punto P que estaba sin coordenada", "Su código P (si son varios: letra al final)", "p lag 1a   ·   p lag 1b"),
    ("No sé en qué zona está", "Usar P como zona", "p mir n1"),
    ("Vuelvo a un punto ya marcado otro día", "El mismo código (no uno nuevo)", "n pat 1"),
], [5.8, 6.4, 5.6])
P("El número definitivo de los puntos nuevos se asigna al importar el GPX: no hace falta saber cuál es el próximo libre.", i=True)

H("2. Zonas (1 letra)")
T(["Letra", "Zona", "Letra", "Zona"], [
    ("R", "Ruta pública (RP12 / RP13)", "N", "Norte: Aduana Vieja, Castillo"),
    ("O", "Campo oeste de la RP12 (Inicio, Chivero)", "L", "Lagunas del oeste (Pilhue, Corazón, del Arco)"),
    ("E", "Campo este de la RP12 (Vaquero, Arroyo del Arco)", "X", "Externo / de terceros"),
    ("P", "No sé / por ubicar", "", ""),
], [1.2, 7.6, 1.2, 7.8])

H("3. Tipos (3 letras)")
tp = HR["tipos"]; half = (len(tp) + 1) // 2
T(["Tipo", "Qué es", "Tipo", "Qué es"], [(tp[i][0], tp[i][1], *(tp[i+half] if i+half < len(tp) else ("", ""))) for i in range(half)], [1.4, 7.4, 1.4, 7.6], size=8)
P("Si dudás entre dos tipos, elegí uno y explicalo en la descripción. Si no encaja ninguno: OTR.", i=True)

H("4. La descripción del punto (opcional, etiquetas cortas)")
T(["Etiqueta", "Significa", "Valores"], [
    ("C:", "¿Dentro del campo?", "S · N · ?"),
    ("A:", "Cómo se llega", "4x4 · 4x2 · pie"),
    ("E:", "Estado", "B (bueno) · R (regular) · M (malo)"),
    ("R:", "Riesgo (texto)", "va al final: todo lo que sigue a R: es el riesgo"),
], [2, 6, 9.8])
P("Ejemplo:   C:S A:4x2 E:R vista al lago, señal 2 rayas R:salida ciega hacia el norte", b=True)
P("Lo que no lleva etiqueta queda como observación. Si no hay tiempo, alcanza con el nombre del punto.")

H("5. Fotos, traza y entrega")
for a, b in [
    ("Fotos", "Adjuntalas al punto en Wikiloc y dejá también las originales en la galería del celular, con la ubicación de la cámara activada y la hora del teléfono en automático. No hace falta renombrarlas: se asocian a cada punto por hora y ubicación."),
    ("Traza", "Una por jornada, con nombre 'REL D1 20261120' (jornada y fecha). Marcá con un punto R CRZ n1, n2… cada lugar donde cruzás la RP12."),
    ("Icono", "Elegí el icono de Wikiloc que más se parezca. Es solo visual: el dato que importa es el código en el nombre."),
    ("Entrega", "Descargá el GPX de cada traza desde Wikiloc (incluye los puntos con nombre y descripción, pero no las fotos) y enviá aparte la carpeta de fotos originales."),
]:
    P(f"{a}: {b}")
H("6. Fuera del campo: territorio en lugar de zona")
P("cic gas n1 cocinería   →   CIC-GAS-01  (Chile · Icalma · Gastronomía; número asignado al importar)", b=True, size=11)
P("Si el código empieza con A o C, el punto está fuera del campo: A = Argentina, C = Chile. Las otras dos letras son el lugar.")
tr = HR["territorios"]; h2 = (len(tr) + 1) // 2
T(["Cód.", "Lugar", "Cód.", "Lugar"], [(tr[i][0], tr[i][2], *((tr[i+h2][0], tr[i+h2][2]) if i+h2 < len(tr) else ("", ""))) for i in range(h2)], [1.4, 7.4, 1.4, 7.6], size=8)
P("Lugar nuevo: crear el código con la letra del país + 2 letras del nombre (ej. CTE Temuco) y avisar; el importador lo marca para agregarlo a la tabla.", i=True)
H("7. Rutas y travesías")
T(["Qué", "Código", "Ejemplo"], [
    ("Ruta de un día", "RUT + ámbito + número. Ámbito: PDA campo · AR Argentina · CL Chile · BI cruza la frontera", "RUT-BI-01"),
    ("Travesía de varios días", "TRV + ámbito + número; cada día .D1, .D2…", "TRV-BI-01.D3"),
    ("Pernocte", "El punto ALO o BAS donde termina el día", "CME-ALO-01"),
], [3.6, 9.4, 4.8], size=8)
P("Ejemplo de día binacional — RUT-BI-01: O-BAS-01 > R-ACC-01 > APE-FRO-01 > CIC-FRO-01 > CIC-GAS-01 > (regreso por el mismo camino) > O-BAS-01", size=8.5)
P("Ejemplo de 4 días — TRV-BI-01: D1 y D2 en el campo · D3 campo → Paso Icalma → Melipeuco (noche CME-ALO-01) · D4 Melipeuco → Icalma → campo", size=8.5)

H("8. Errores que el importador detecta (y conviene evitar)")
for t in ["Tipo inexistente (ej. 'e vaq 1'): usar uno de la lista (Vaquero es e bas 2).", "Territorio fuera de la tabla (ej. 'cxx'): se acepta, pero queda marcado para agregarlo.",
          "Punto sin código (ej. 'Mirador lindo'): queda para revisar a mano.",
          "Escribir 0 (cero) en lugar de O: se corrige solo, pero mejor evitarlo.",
          "Marcar como nuevo un punto que ya existía: el importador avisa si está a menos de 60 m de uno conocido."]:
    P("• " + t)
doc.save(sys.argv[2]); print("ok")
