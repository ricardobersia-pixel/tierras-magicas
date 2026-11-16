# -*- coding: utf-8 -*-
"""v3.1: Milenka confirmado (contiguo a Tierras Mágicas, 3 cabañas de 6 pax) y ambos como primeros asociados."""
import sys, re
D = sys.argv[1]
def ed(p, R):
    s = open(p).read()
    for a, b in R:
        if a not in s: raise SystemExit(f"MISSING {p}: {a[:80]}")
        s = s.replace(a, b)
    open(p, "w").write(s)
def ed_line(p, contains, new):
    L = open(p).read().split("\n"); idx = [i for i, l in enumerate(L) if contains in l]
    if len(idx) != 1: raise SystemExit(f"line match {len(idx)} for {contains[:60]}")
    L[idx[0]] = new; open(p, "w").write("\n".join(L))

P = D + "/build_plan_v3.py"
ed(P, [
 ('p = doc.add_paragraph(); r = p.add_run("Plan de Negocios v3 — Reformulado desde cero"); r.font.size = Pt(15)',
  'p = doc.add_paragraph(); r = p.add_run("Plan de Negocios v3.1 — Reformulado desde cero"); r.font.size = Pt(15)'),
 ('P("Versión 3.0 · 16/11/2026 · Documento de trabajo para decisión del titular. Reemplaza a las versiones 1 a 2.5, que pasan a ser antecedentes.',
  'P("Versión 3.1 · 16/11/2026 (incorpora a Milenka: contiguo a Tierras Mágicas, 3 cabañas de 6 plazas; ambos son los primeros asociados) · Documento de trabajo para decisión del titular. Reemplaza a las versiones 1 a 2.5, que pasan a ser antecedentes.'),
 ('("Huéspedes de Milenka", "Complejo aliado (datos PEND)", "Ídem", "1 — piloto"),',
  '("Huéspedes de Milenka", "Complejo contiguo a Tierras Mágicas, 3 cabañas de 6 plazas (CONF)", "Ídem", "1 — piloto"),'),
 ('("Plazas", "16 en cabañas + 4 en dormi (CONF)", "PEND", "Configuración del sistema de reservas"),',
  '("Plazas", "16 en cabañas + 4 en dormi (CONF)", "18 (3 cabañas × 6, CONF titular)", "Sistema de reservas TM · titular"),'),
 ('("Ocupación anual", "PEND (el panel de TM la calcula)", "PEND", "Registros de cada complejo"),',
  '("Ocupación anual", "PEND (el panel de TM la calcula)", "PEND", "Registros de cada complejo"),'),
 ('("Estadía media", "≥ 2–3 noches por política (CONF); media real PEND", "PEND", "Registros"),',
  '("Estadía media", "≥ 2–3 noches por política (CONF); media real PEND", "PEND (política de estadía mínima también)", "Registros"),'),
 ('    ("Demanda cautiva insuficiente (TM pequeño; Milenka sin datos)", "Crítico",',
  '    ("Demanda cautiva insuficiente (TM + Milenka = 34 plazas)", "Crítico",'),
 ('("1–2", "Confirmar datos de Milenka (ubicación, plazas, ocupación, vínculo) y de Tierras Mágicas (ocupación y estadía media del panel)", "Titular", "Tabla de complejos"),',
  '("1–2", "Cargar ocupación y estadía media de Tierras Mágicas (panel) y de Milenka; acordar condiciones con Milenka", "Titular", "Tabla de complejos completa"),'),
 ('("Milenka: ubicación, plazas, ocupación, vínculo y condiciones", "Demanda y acuerdo", "Titular"),',
  '("Milenka: ocupación, estadía media, condiciones del acuerdo y coordenada (plazas y ubicación ya CONF)", "Demanda y acuerdo", "Titular / Milenka"),'),
 ('"Confirmar el vínculo con Milenka y la lista de complejos a invitar.",',
  '"Acordar con Milenka las condiciones (comisión o paquete) y definir la lista de complejos a invitar después.",'),
 ("Tierras Mágicas = AMO-ALO-01 (Moquehue); Milenka y los asociados reciben su código ALO al relevarlos.",
  "Tierras Mágicas = AMO-ALO-01 y Milenka = AMO-ALO-02 (Moquehue, contiguos); los demás asociados reciben su código ALO al relevarlos."),
 ('("Complejos asociados", "TERRITORIO-ALO-NN", "AMO-ALO-01 Tierras Mágicas (Moquehue)"),',
  '("Complejos asociados", "TERRITORIO-ALO-NN", "AMO-ALO-01 Tierras Mágicas · AMO-ALO-02 Milenka"),'),
 ('"Tierras Mágicas → acceso RP13/RP12 → Tranquera 1; Milenka → acceso; tiempos reales por estación;',
  '"Tierras Mágicas y Milenka (contiguos: un solo punto de salida) → acceso RP13/RP12 → Tranquera 1; tiempos reales por estación;'),
])
ed_line(P, 'B("Tierras Mágicas tiene 3 cabañas (6 + 6 + 4 plazas)',
 'B("Los dos primeros asociados están juntos en Moquehue: Tierras Mágicas tiene 3 cabañas (6 + 6 + 4 plazas) más un dormi para 4 personas, con estadía mínima de 2 a 3 noches (CONF: sistema de reservas); Milenka, contiguo, tiene 3 cabañas de 6 plazas (CONF titular). Suman 34 plazas. Aun con ocupación plena, el techo es ≈6.200 huéspedes por año con estadías de 2 noches y ≈4.100 con estadías de 3 (34 × 365 ÷ estadía). La demanda real será una fracción de ese techo: el piloto puede apoyarse en estos dos complejos, pero la escala del negocio depende de sumar más asociados.", "Escala de la demanda cautiva (CONF + INF).")')
ed_line(P, 'P("Techo de Tierras Mágicas (INF)',
 'P("Techo conjunto de Tierras Mágicas + Milenka (INF): 34 plazas × 365 ÷ estadía media → ≈6.200 huéspedes/año con 2 noches; ≈4.100 con 3 noches (TM sola ≈2.900 / ≈1.950; Milenka sola ≈3.300 / ≈2.200). Es un máximo teórico con ocupación del 100%: la demanda real será una fracción. Ventaja operativa: al estar contiguos, comparten un único punto de salida y se pueden juntar huéspedes de ambos en la misma salida.", i=True)')
ed(P, [('B("Del complejo al acceso RP13/RP12 hay ≈27,5 km',
        'B("De los complejos (Tierras Mágicas y Milenka, contiguos) al acceso RP13/RP12 hay ≈27,5 km'),
       ('B("Acuerdo marco con Tierras Mágicas y Milenka (comisión o precio neto, materiales, reservas, cancelaciones).',
        'B("Acuerdo marco con Tierras Mágicas y Milenka, los primeros asociados (CONF): comisión o precio neto, materiales, reservas, cancelaciones; salidas compartidas entre huéspedes de ambos.')])
ed(P, [('fig.savefig(MAPA', 'ax.annotate("+ MILENKA (contiguo)", (TM[1], TM[0]), fontsize=8, xytext=(8, -14), textcoords="offset points", color="#7a5c00")\nfig.savefig(MAPA')])
ed(P, [('"Plan_de_Negocios_Paso_del_Arco_v3.docx"', '"Plan_de_Negocios_Paso_del_Arco_v3_1.docx"')])

M = D + "/build_modelo_v3.py"
ed(M, [
 ('("Milenka", "PEND", None, "PEND: plazas, ubicación, vínculo"),',
  '("Milenka", "AMO-ALO-02", 18, "CONF titular: contiguo a Tierras Mágicas, 3 cabañas de 6 plazas. Primer asociado junto con TM."),'),
 ('ws.cell(e + 6, 1, "Es un máximo: la demanda real es una fracción (ocupación < 100% y tasa de compra < 100%).").font = Font(italic=True)',
  '''ws.cell(e + 6, 1, "Techo conjunto TM + Milenka, estadía de 2 noches"); ws.cell(e + 6, 3, "=(C4+C5)*365/2").number_format = NUM
ws.cell(e + 7, 1, "Techo conjunto TM + Milenka, estadía de 3 noches"); ws.cell(e + 7, 3, "=(C4+C5)*365/3").number_format = NUM
ws.cell(e + 8, 1, "Es un máximo: la demanda real es una fracción (ocupación < 100% y tasa de compra < 100%). TM y Milenka son contiguos: comparten punto de salida.").font = Font(italic=True)'''),
 ('("PASO DEL ARCO ADVENTURE — Modelo económico v3 (demanda desde complejos)", True),', '("PASO DEL ARCO ADVENTURE — Modelo económico v3.1 (demanda desde complejos)", True),'),
 ('Celdas verdes = dato confirmado (plazas de Tierras Mágicas, sistema de reservas).', 'Celdas verdes = dato confirmado (plazas de Tierras Mágicas por su sistema de reservas; plazas de Milenka por el titular).'),
 ("Techo teórico de Tierras Mágicas (100% ocupación)", "Techo teórico (100% ocupación)"),
 ("Huéspedes/año con estadía de 2 noches\"", "Tierras Mágicas, estadía de 2 noches\""),
 ("Huéspedes/año con estadía de 3 noches\"", "Tierras Mágicas, estadía de 3 noches\""),
])

H = D + "/hoja_ruta.py"
ed(H, [(' ("R-ACC-01", "Acceso RP13/RP12 (Paso del Arco)"',
        ' ("AMO-ALO-02", "Milenka (complejo contiguo a Tierras Mágicas)", None, None, "—", "CONF titular (sin coordenada)", "Marcar su entrada; punto de encuentro común con TM"),\n ("R-ACC-01", "Acceso RP13/RP12 (Paso del Arco)"'),
       ('  ["AMO-ALO-01", "R-ACC-01", "R-MIR-01", "O-TRQ-01", "O-BAS-01", "AMO-ALO-01"],\n  [],',
        '  ["AMO-ALO-01", "R-ACC-01", "R-MIR-01", "O-TRQ-01", "O-BAS-01", "AMO-ALO-01"],\n  ["AMO-ALO-02"],'),
       ('"Traslado desde Tierras Mágicas"', '"Traslado desde Tierras Mágicas y Milenka"')])
print("ok")
