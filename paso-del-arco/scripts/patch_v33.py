# -*- coding: utf-8 -*-
"""v3.3: ocupación y estadía de Milenka = Tierras Mágicas (comparables, CONF); salidas compartidas entre ambos (CONF)."""
import sys
D = sys.argv[1]
def ed(p, R):
    s = open(p).read()
    for a, b in R:
        if a not in s: raise SystemExit(f"MISSING {p}: {a[:80]}")
        s = s.replace(a, b)
    open(p, "w").write(s)

M = D + "/build_modelo_v3.py"
ed(M, [
 ('    for j, f in ((4, PCT), (5, DEC), (6, DEC), (7, PCT), (8, DEC)): inp(ws.cell(i, j), f)',
  '''    for j, f in ((4, PCT), (5, DEC), (6, DEC), (7, PCT), (8, DEC)): inp(ws.cell(i, j), f)
    if cod == "AMO-ALO-02":  # Milenka: ocupación y estadía comparables con TM (CONF titular)
        for j, f in ((4, PCT), (5, DEC)):
            c_ = ws.cell(i, j, f"={L(j)}4"); c_.number_format = f; c_.fill = CNF'''),
 ('TOT_SAL = f"\'01_Complejos\'!K{e+1}"', '''s0 = e + 10
ws.cell(s0, 1, "SALIDAS COMPARTIDAS (CONF: se comparten entre huéspedes de Tierras Mágicas y Milenka)").font = Font(bold=True)
ws.cell(s0 + 1, 1, "Personas en travesía por año (todos los complejos)"); ws.cell(s0 + 1, 3, f"=L{e+1}").number_format = NUM
ws.cell(s0 + 2, 1, "Personas por salida compartida (promedio según mix de productos, hoja 02)")
ws.cell(s0 + 3, 1, "SALIDAS OPERADAS por año (compartidas)").font = Font(bold=True); ws.cell(s0 + 3, 3, f'=IFERROR(C{s0+1}/C{s0+2},0)').number_format = DEC
ws.cell(s0 + 4, 1, "Referencia: salidas si cada grupo saliera solo (privadas)"); ws.cell(s0 + 4, 3, f"=K{e+1}").number_format = DEC
ws.cell(s0 + 5, 1, "Ahorro de salidas por compartir"); ws.cell(s0 + 5, 3, f'=IFERROR(1-C{s0+3}/C{s0+4},"")').number_format = PCT
ws.cell(s0 + 6, 1, "Milenka toma la ocupación y la estadía de Tierras Mágicas (CONF: comparables). Si en algún momento difieren, reemplazar la fórmula por el dato propio.").font = Font(italic=True)
WS01 = ws; PERS_CELL = (s0 + 2, 3)
TOT_SAL = f"'01_Complejos'!C{s0+3}"; TOT_PERS = f"'01_Complejos'!C{s0+1}"'''),
 ('MIX = VR[V[13]]; LAST = L(1 + len(prods))', '''MIX = VR[V[13]]; LAST = L(1 + len(prods))
c_ = WS01.cell(*PERS_CELL, f"=IFERROR(SUMPRODUCT('02_Productos'!B{VR[V[1]]}:{LAST}{VR[V[1]]},'02_Productos'!B{MIX}:{LAST}{MIX}),0)"); c_.number_format = DEC'''),
 ('("Salidas demandadas por todos los complejos", f"={TOT_SAL}", DEC),', '("Salidas operadas (compartidas) con los complejos cargados", f"={TOT_SAL}", DEC),'),
 ('("Salidas medias por complejo cargado", f"=IFERROR({TOT_SAL}/COUNTIF(\'01_Complejos\'!K4:K11,\\">0\\"),0)", DEC),',
  '("Salidas compartidas que aporta en promedio cada complejo cargado", f"=IFERROR({TOT_SAL}/COUNTIF(\'01_Complejos\'!L4:L11,\\">0\\"),0)", DEC),'),
 ('("PASO DEL ARCO ADVENTURE — Modelo económico v3.2 (demanda desde complejos)", True),', '("PASO DEL ARCO ADVENTURE — Modelo económico v3.3 (demanda desde complejos, salidas compartidas)", True),'),
])

P = D + "/build_plan_v3.py"
ed(P, [
 ('"Plan de Negocios v3.2 — Reformulado desde cero"', '"Plan de Negocios v3.3 — Reformulado desde cero"'),
 ('P("Versión 3.2 · 16/11/2026 (Milenka: -38.900986, -71.291336, a ≈40 m de Tierras Mágicas, 3 cabañas de 6 plazas, mismos cuadros tarifarios y políticas; ambos son los primeros asociados)',
  'P("Versión 3.3 · 16/11/2026 (Milenka: -38.900986, -71.291336, a ≈40 m de Tierras Mágicas, 3 cabañas de 6 plazas, mismos cuadros tarifarios, políticas, ocupación y estadía comparables; salidas compartidas entre huéspedes de ambos)'),
 ('("Ocupación anual", "PEND (el panel de TM la calcula)", "PEND", "Registros de cada complejo"),',
  '("Ocupación anual", "PEND (el panel de TM la calcula)", "Igual a TM (CONF: comparables)", "Panel de Tierras Mágicas"),'),
 ('"≥ 2–3 noches: mismas políticas que TM (CONF); media real PEND"', '"Igual a TM (CONF: comparables)"'),
 ('P("Salidas demandadas por complejo = plazas × 365 × ocupación ÷ estadía media ÷ tamaño de grupo × tasa de compra × travesías por estadía", b=True)',
  'P("Personas en travesía por año = Σ complejos (plazas × 365 × ocupación ÷ estadía media × tasa de compra × travesías por estadía)", b=True)\nP("Salidas operadas = personas en travesía ÷ personas por salida. Las salidas se comparten entre huéspedes de Tierras Mágicas y Milenka (CONF): los vehículos se llenan con huéspedes de ambos complejos en lugar de una salida por grupo.", b=True)'),
 ('("Milenka: ocupación y estadía media reales, condiciones del acuerdo (plazas, coordenada, tarifas y políticas ya CONF)", "Demanda y acuerdo", "Titular / Milenka"),',
  '("Ocupación anual y estadía media de Tierras Mágicas (valen también para Milenka)", "Demanda", "Panel de TM: Finanzas / Estadísticas"),\n    ("Condiciones del acuerdo con Milenka: comisión o paquete", "Acuerdo", "Titular"),'),
 ('("Ocupación y estadía media real de Tierras Mágicas", "Demanda", "Panel de Finanzas/Estadísticas del sistema de TM"),\n', ''),
 ('("1–2", "Cargar ocupación y estadía media de Tierras Mágicas (panel) y de Milenka; acordar condiciones con Milenka", "Titular", "Tabla de complejos completa"),',
  '("1–2", "Cargar ocupación y estadía media de Tierras Mágicas en el modelo (Milenka las toma automáticamente); acordar condiciones con Milenka", "Titular", "Tabla de complejos completa"),'),
 ('B("Acuerdo marco con Tierras Mágicas y Milenka, los primeros asociados (CONF): comisión o precio neto, materiales, reservas, cancelaciones; salidas compartidas entre huéspedes de ambos.',
  'B("Acuerdo marco con Tierras Mágicas y Milenka, los primeros asociados (CONF): comisión o precio neto, materiales, reservas y cancelaciones. Las salidas se comparten entre huéspedes de ambos complejos (CONF): un mismo calendario de salidas, cupos por vehículo y una regla clara de mínimo de personas para confirmar la salida.'),
 ('("Margen por salida", "ingreso (precio × personas) − costo variable"),',
  '("Margen por salida", "ingreso (precio × personas) − costo variable"),\n    ("Salidas compartidas", "salidas operadas = personas en travesía ÷ personas por salida (mix de productos); el modelo muestra cuántas salidas se ahorran frente a salir grupo por grupo"),'),
 ('"Plan_de_Negocios_Paso_del_Arco_v3_2.docx"', '"Plan_de_Negocios_Paso_del_Arco_v3_3.docx"'),
 ('("Punto de equilibrio", "costos fijos anuales ÷ margen medio por salida = salidas/año; ÷ salidas por complejo = complejos necesarios"),',
  '("Punto de equilibrio", "costos fijos anuales ÷ margen medio por salida = salidas/año; ÷ salidas compartidas que aporta cada complejo = complejos necesarios"),'),
])
# Modelo operativo: regla de salidas compartidas
ed(P, [('B("Todo recorrido que una el sector oeste con Vaquero cruza la RP12:',
        'B("Calendario único de salidas para Tierras Mágicas y Milenka; cada salida tiene cupo por vehículo y un mínimo de personas para confirmarse (a definir con costos reales). Si no se llega al mínimo: se reprograma o se ofrece como salida privada con otra tarifa. Se confirma o se cancela con anticipación fija (p. ej. la tarde anterior) y por clima.", "Salidas compartidas (CONF):")\nB("Todo recorrido que una el sector oeste con Vaquero cruza la RP12:')])
print("ok")
