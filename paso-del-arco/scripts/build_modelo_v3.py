# -*- coding: utf-8 -*-
"""Modelo económico v3 (demanda desde complejos). Uso: build_modelo_v3.py <out.xlsx>"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

wb = Workbook()
HDR = PatternFill("solid", fgColor="1F3A2E"); INP = PatternFill("solid", fgColor="FFF4CC"); CNF = PatternFill("solid", fgColor="DCE8DF")
BLUE = Font(color="0000FF"); NUM = '#,##0;[Red]-#,##0;"-"'; PCT = '0%;[Red]-0%;"-"'; DEC = '#,##0.0;[Red]-#,##0.0;"-"'
def hdr(ws, r, cols):
    for j, h in enumerate(cols, 1):
        c = ws.cell(r, j, h); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF"); c.alignment = Alignment(wrap_text=True, vertical="top")
def inp(c, fmt=None, val=None, conf=False):
    c.value = val; c.fill = CNF if conf else INP; c.font = BLUE
    if fmt: c.number_format = fmt

ws = wb.active; ws.title = "00_Leeme"
for i, (t, b) in enumerate([
    ("PASO DEL ARCO ADVENTURE — Modelo económico v3.6 (demanda por cabañas y temporadas, salidas compartidas, sociedad TM–Milenka)", True),
    ("Acompaña al Plan de Negocios v3. Celdas amarillas con texto azul = datos de entrada (vacías: no se inventan importes). Celdas verdes = dato confirmado (sistema de reservas de TM o titular). Celda celeste = inferencia editable (2,5 personas por reserva = punto medio del rango 1–4 informado). Blancas = fórmulas.", False),
    ("Flujo: 01_Complejos (demanda) → 02_Productos (margen por salida y referencia de mercado) → 03_Equilibrio → 04_Escenarios → 05_Flujo_12m → 06_CAPEX → 07_Reparto (sociedad TM–Milenka).", False),
    ("Recomendación: completar primero con datos del panel de Tierras Mágicas (ocupación, estadía media) y de Milenka, cotizaciones del prestador aliado y del seguro, y la tasa de compra medida en la preventa.", False),
], 1):
    c = ws.cell(i, 1, t); c.font = Font(bold=b, size=13 if i == 1 else 11); c.alignment = Alignment(wrap_text=True)
ws.column_dimensions["A"].width = 130

# 01 Complejos (v3.4: por cabañas y temporadas)
INFF = PatternFill("solid", fgColor="DDEBF7")
ws = wb.create_sheet("01_Complejos")
ws.cell(1, 1, "Demanda desde los complejos, por cabañas ocupadas y temporadas (un grupo de 1–4 personas ocupa una cabaña)").font = Font(bold=True)
hdr(ws, 3, ["Temporada", "Días 2026 (calendario TM)", "Ocupación de cabañas (%)", "Estadía mínima (noches)", "Noches ocupadas por cabaña"])
temps = [("Alta", 86, 0.8, 3), ("Alta Premium", 54, None, 3), ("Media", 100, None, 2), ("Baja", 125, None, 2)]
for i, (t, d, o, m) in enumerate(temps, 4):
    ws.cell(i, 1, t); inp(ws.cell(i, 2), NUM, d, conf=True); inp(ws.cell(i, 3), PCT, o, conf=o is not None); inp(ws.cell(i, 4), NUM, m, conf=True)
    ws.cell(i, 5, f"=IFERROR(B{i}*C{i},0)").number_format = NUM
ws.cell(8, 1, "AÑO").font = Font(bold=True); ws.cell(8, 2, "=SUM(B4:B7)").number_format = NUM
ws.cell(8, 5, "=SUM(E4:E7)").number_format = NUM; ws.cell(8, 3, '=IF(COUNT(C4:C7)<4,"Faltan temporadas",E8/B8)').number_format = PCT
ws.cell(9, 1, "Alta 80% = CONF titular (Tierras Mágicas y Milenka). Días y estadías mínimas = calendario y políticas de TM (CONF; Fin de año exige 5 noches). Premium, Media y Baja: PEND. La ocupación anual de la fila AÑO solo es válida con las cuatro cargadas.").font = Font(italic=True)
hdr(ws, 11, ["Complejo", "Código", "Cabañas", "Plazas (ref.)", "Personas por reserva", "Estadía media (noches)", "Tasa de compra (%)", "Travesías por estadía",
             "Reservas/año (temporadas cargadas)", "Personas/año", "Personas en travesía/año", "Grupos en travesía/año", "Fuente / nota"])
rows = [("Tierras Mágicas", "AMO-ALO-01", 3, 16, "CONF: 3 cabañas (6+6+4) + dormi de 4 (amplía una reserva, no suma reservas). Grupo 1–4 personas (CONF): 2,5 = punto medio (INF, editable)."),
        ("Milenka", "AMO-ALO-02", 3, 18, "CONF: 3 cabañas de 6; ≈40 m de TM; mismas tarifas, políticas, ocupación y estadía que TM (toma sus valores)."),
        ("Complejo asociado 3", "", None, None, "Asociados futuros: por comisión (no comparten gastos y ganancias)"), ("Complejo asociado 4", "", None, None, ""),
        ("Complejo asociado 5", "", None, None, ""), ("Complejo asociado 6", "", None, None, ""), ("Complejo asociado 7", "", None, None, ""), ("Complejo asociado 8", "", None, None, "")]
for i, (n, cod, cab, pl, note) in enumerate(rows, 12):
    ws.cell(i, 1, n); ws.cell(i, 2, cod)
    inp(ws.cell(i, 3), NUM, cab, conf=cab is not None); inp(ws.cell(i, 4), NUM, pl, conf=pl is not None)
    for j, f in ((5, DEC), (6, DEC), (7, PCT), (8, DEC)): inp(ws.cell(i, j), f)
    if cod == "AMO-ALO-01":
        c_ = ws.cell(i, 5); c_.value = 2.5; c_.fill = INFF
    if cod == "AMO-ALO-02":
        for j, f in ((5, DEC), (6, DEC)):
            c_ = ws.cell(i, j, f"={L(j)}12"); c_.number_format = f; c_.fill = CNF
    ws.cell(i, 9, f"=IFERROR(C{i}*$E$8/F{i},0)").number_format = NUM
    ws.cell(i, 10, f"=IFERROR(I{i}*E{i},0)").number_format = NUM
    ws.cell(i, 11, f"=IFERROR(J{i}*G{i}*H{i},0)").number_format = NUM
    ws.cell(i, 12, f"=IFERROR(I{i}*G{i}*H{i},0)").number_format = DEC
    ws.cell(i, 13, note)
e = 11 + len(rows)
ws.cell(e + 1, 1, "TOTAL").font = Font(bold=True)
for j in (3, 4, 9, 10, 11, 12): ws.cell(e + 1, j, f"=SUM({L(j)}12:{L(j)}{e})").number_format = NUM
ws.cell(e + 3, 1, "COTA DE TEMPORADA ALTA (dato CONF: 80% de ocupación)").font = Font(bold=True)
ws.cell(e + 4, 1, "Reservas máximas en Alta, TM + Milenka (estadía mínima 3 noches)"); ws.cell(e + 4, 3, "=(C12+C13)*B4*C4/D4").number_format = DEC
ws.cell(e + 5, 1, "Personas en Alta si todas las reservas fueran de 1 persona"); ws.cell(e + 5, 3, f"=C{e+4}*1").number_format = NUM
ws.cell(e + 6, 1, "Personas en Alta si todas fueran de 4 personas"); ws.cell(e + 6, 3, f"=C{e+4}*4").number_format = NUM
ws.cell(e + 7, 1, "Personas en Alta con 2,5 por reserva (INF)"); ws.cell(e + 7, 3, f"=C{e+4}*E12").number_format = NUM
ws.cell(e + 8, 1, "Techo del año con 100% de ocupación y estadía de 2 noches (reservas)"); ws.cell(e + 8, 3, "=(C12+C13)*365/2").number_format = NUM
ws.cell(e + 9, 1, "Son cotas: estadías más largas que la mínima reducen las reservas; la tasa de compra reduce las personas en travesía.").font = Font(italic=True)
for j, w in enumerate([26, 13, 9, 9, 10, 11, 10, 10, 10, 10, 12, 12, 60], 1): ws.column_dimensions[L(j)].width = w
s0 = e + 11
ws.cell(s0, 1, "SALIDAS COMPARTIDAS (CONF: se comparten entre huéspedes de Tierras Mágicas y Milenka)").font = Font(bold=True)
ws.cell(s0 + 1, 1, "Personas en travesía por año (todos los complejos)"); ws.cell(s0 + 1, 3, f"=K{e+1}").number_format = NUM
ws.cell(s0 + 2, 1, "Personas por salida compartida (promedio según mix de productos, hoja 02)")
ws.cell(s0 + 3, 1, "SALIDAS OPERADAS por año (compartidas)").font = Font(bold=True); ws.cell(s0 + 3, 3, f'=IFERROR(C{s0+1}/C{s0+2},0)').number_format = DEC
ws.cell(s0 + 4, 1, "Referencia: salidas si cada grupo saliera solo (privadas)"); ws.cell(s0 + 4, 3, f"=L{e+1}").number_format = DEC
ws.cell(s0 + 5, 1, "Ahorro de salidas por compartir"); ws.cell(s0 + 5, 3, f'=IFERROR(1-C{s0+3}/C{s0+4},"")').number_format = PCT
sv = s0 + 7
ws.cell(sv, 1, "NO TODOS HACEN TRAVESÍA (CONF): sensibilidad a la tasa de compra, solo temporada Alta (cota CONF + 2,5 personas por reserva INF)").font = Font(bold=True)
hdr(ws, sv + 1, ["Tasa de compra", "", "Personas en travesía en Alta", "Grupos en travesía en Alta", "Personas-día (1 travesía de 1 día)"])
for k_, t in enumerate((0.1, 0.2, 0.3, 0.5), sv + 2):
    c_ = ws.cell(k_, 1, t); c_.number_format = PCT
    ws.cell(k_, 3, f"=C{e+7}*A{k_}").number_format = NUM
    ws.cell(k_, 4, f"=C{e+4}*A{k_}").number_format = NUM
    ws.cell(k_, 5, f"=C{k_}").number_format = NUM
ws.cell(sv + 6, 1, "Tasas ilustrativas, no estimaciones: la tasa real se mide con la preventa y el piloto. Fuera de la temporada Alta la demanda se suma cuando se carguen las otras ocupaciones.").font = Font(italic=True)
WS01 = ws; PERS_CELL = (s0 + 2, 3)
TOT_SAL = f"'01_Complejos'!C{s0+3}"; TOT_PERS = f"'01_Complejos'!C{s0+1}"

# 02 Productos
ws = wb.create_sheet("02_Productos")
ws.cell(1, 1, "Margen por salida — productos T1 a T5 (Plan v3). Traslado complejo↔campo separado del recorrido.").font = Font(bold=True)
G = [("Precio combustible por litro", ""), ("Consumo en ruta (l/100 km)", ""), ("Consumo en huella (l/100 km)", ""), ("Desgaste por km", ""),
     ("Hora de guía/conductor", ""), ("Hora de apoyo/cierre", ""), ("Hora de cocina/base", ""), ("Impuestos sobre ventas (%)", "")]
hdr(ws, 3, ["Parámetro global", "Valor", "Fuente"])
GR = {}
for i, (a, _) in enumerate(G, 4):
    ws.cell(i, 1, a); inp(ws.cell(i, 2), PCT if "%" in a else NUM); inp(ws.cell(i, 3)); GR[a] = f"$B${i}"
prods = ["T1 Medio día campo", "T2 Día campo + Vaquero", "T3 Campo + zona", "T4 Paquete (por travesía)", "T5 Convoy con tu 4x4", "T4+ Todo incluido (por persona y día)"]
V = ["Precio por persona (T5: por vehículo)", "Personas (T5: vehículos) por salida", "Km de traslado ida y vuelta (≈70 desde TM; 0 si encuentro en tranquera)",
     "Km del recorrido (huella)", "Vehículos del operador por salida", "Horas de guía", "Horas de apoyo", "Horas de cocina/base", "Comida por persona",
     "Seguro por persona", "Consumibles por salida", "Comisión del complejo (%) — TM y Milenka: 0 (socios); asociados futuros: %", "Pago al prestador aliado por salida", "Mix de salidas (%)",
     "Alojamiento: pago al complejo que hospeda, por persona y noche (solo T4+; cada complejo factura su alojamiento)"]
r0 = 14
hdr(ws, r0, ["Variable"] + prods)
VR = {}
for i, v in enumerate(V, r0 + 1):
    ws.cell(i, 1, v); VR[v] = i
    for j in range(len(prods)):
        inp(ws.cell(i, 2 + j), PCT if "%" in v else NUM)
b = r0 + len(V) + 2
lines = [
 ("Ingreso por salida", lambda c: f"=IFERROR({c}{VR[V[0]]}*{c}{VR[V[1]]},0)"),
 ("Impuestos", lambda c: f"=IFERROR({c}{b}*{GR['Impuestos sobre ventas (%)']},0)"),
 ("Comisión del complejo", lambda c: f"=IFERROR({c}{b}*{c}{VR[V[11]]},0)"),
 ("Traslado (combustible + desgaste)", lambda c: f"=IFERROR({c}{VR[V[2]]}*{c}{VR[V[4]]}*({GR['Consumo en ruta (l/100 km)']}/100*{GR['Precio combustible por litro']}+{GR['Desgaste por km']}),0)"),
 ("Recorrido (combustible + desgaste)", lambda c: f"=IFERROR({c}{VR[V[3]]}*{c}{VR[V[4]]}*({GR['Consumo en huella (l/100 km)']}/100*{GR['Precio combustible por litro']}+{GR['Desgaste por km']}),0)"),
 ("Personal", lambda c: f"=IFERROR({c}{VR[V[5]]}*{GR['Hora de guía/conductor']}+{c}{VR[V[6]]}*{GR['Hora de apoyo/cierre']}+{c}{VR[V[7]]}*{GR['Hora de cocina/base']},0)"),
 ("Comida", lambda c: f"=IFERROR({c}{VR[V[8]]}*{c}{VR[V[1]]},0)"),
 ("Seguro", lambda c: f"=IFERROR({c}{VR[V[9]]}*{c}{VR[V[1]]},0)"),
 ("Consumibles", lambda c: f"=N({c}{VR[V[10]]})"),
 ("Prestador aliado", lambda c: f"=N({c}{VR[V[12]]})"),
 ("Alojamiento (costo interno)", lambda c: f"=IFERROR({c}{VR[V[14]]}*{c}{VR[V[1]]},0)"),
]
for k_, (lab, fn) in enumerate(lines):
    r = b + k_; ws.cell(r, 1, lab)
    for j in range(len(prods)): ws.cell(r, 2 + j, fn(L(2 + j))).number_format = NUM
cv = b + len(lines); mc = cv + 1
ws.cell(cv, 1, "COSTO VARIABLE").font = Font(bold=True); ws.cell(mc, 1, "MARGEN POR SALIDA").font = Font(bold=True)
ws.cell(mc + 1, 1, "Margen %"); ws.cell(mc + 2, 1, "Peso del traslado en el costo variable")
for j in range(len(prods)):
    c = L(2 + j)
    ws.cell(cv, 2 + j, f"=SUM({c}{b+1}:{c}{cv-1})").number_format = NUM
    ws.cell(mc, 2 + j, f"={c}{b}-{c}{cv}").number_format = NUM
    ws.cell(mc + 1, 2 + j, f'=IF({c}{b}=0,"",{c}{mc}/{c}{b})').number_format = PCT
    ws.cell(mc + 2, 2 + j, f'=IF({c}{cv}=0,"",{c}{b+3}/{c}{cv})').number_format = PCT
rb = mc + 4
ws.cell(rb, 1, "REFERENCIA DE MERCADO (CONF titular)").font = Font(bold=True)
ws.cell(rb + 1, 1, "Prestadores similares: USD 1.000 por persona y por día (guía de travesía, alojamiento, desayuno, almuerzo y cena)"); inp(ws.cell(rb + 1, 2), NUM, 1000, conf=True)
ws.cell(rb + 1, 3, "CONF titular: por persona y por día; referencia de una travesía de 5 noches (USD 5.000); los programas más cortos, proporcionales")
ws.cell(rb + 2, 1, "Tipo de cambio de referencia (ARS por USD)"); c_ = ws.cell(rb + 2, 2, 1525); c_.fill = INFF; c_.font = BLUE; c_.number_format = NUM
ws.cell(rb + 2, 3, "INF: el que usa la configuración de TM (supuesto; actualizar)")
ws.cell(rb + 3, 1, "Referencia en pesos"); ws.cell(rb + 3, 2, f"=B{rb+1}*B{rb+2}").number_format = NUM
ws.cell(rb + 4, 1, "Precio del T4+ (por persona y día) frente a la referencia"); ws.cell(rb + 4, 2, f'=IFERROR(G{VR[V[0]]}/B{rb+3},"")').number_format = PCT

# Cuadro tarifario común TM = Milenka (CONF: configuración del sistema de reservas de TM; mismos cuadros en ambos complejos)
rt = rb + 7
ws.cell(rt, 1, "CUADRO TARIFARIO COMÚN (CONF) — ARS por cabaña y noche, Booking/Airbnb (dom–jue mínimo, vie–sáb máximo); venta directa con descuento").font = Font(bold=True)
hdr(ws, rt + 1, ["Temporada", "Cabaña 6: mín", "Cabaña 6: máx", "Cabaña 4: mín", "Cabaña 4: máx", "Cabaña 6 promedio con descuento directo", "Por persona y noche (÷ personas por reserva)"])
tar = [("Alta Premium", 280000, 340000, 210000, 250000), ("Alta", 210000, 260000, 160000, 190000), ("Media", 150000, 190000, 110000, 140000), ("Baja", 110000, 135000, 80000, 100000)]
for k_, (t, a1, a2, b1, b2) in enumerate(tar, rt + 2):
    ws.cell(k_, 1, t)
    for j, v in enumerate((a1, a2, b1, b2), 2): inp(ws.cell(k_, j), NUM, v, conf=True)
    ws.cell(k_, 6, f"=AVERAGE(B{k_}:C{k_})*(1-$B${rt+7})").number_format = NUM
    ws.cell(k_, 7, f"=IFERROR(F{k_}/'01_Complejos'!$E$12,0)").number_format = NUM
ws.cell(rt + 7, 1, "Descuento de venta directa (CONF: 10%)"); inp(ws.cell(rt + 7, 2), PCT, 0.10, conf=True)
ws.cell(rt + 8, 1, "Temporada del programa todo incluido (escribir: Alta Premium, Alta, Media o Baja)"); inp(ws.cell(rt + 8, 2), None, "Alta")
ws.cell(rt + 9, 1, "ALOJAMIENTO APLICADO al T4+ (por persona y noche)").font = Font(bold=True)
ws.cell(rt + 9, 2, f'=IFERROR(INDEX(G{rt+2}:G{rt+5},MATCH(B{rt+8},A{rt+2}:A{rt+5},0)),0)').number_format = NUM
ws.cell(rt + 10, 1, "Peso del alojamiento sobre la referencia de mercado por persona y día"); ws.cell(rt + 10, 2, f'=IFERROR(B{rt+9}/B{rb+3},"")').number_format = PCT
ws.cell(rt + 11, 1, "INF: precio interno = promedio de la cabaña de 6 con descuento directo ÷ personas por reserva (2,5). Milenka tiene cabañas de 6; editar si se acuerda otra regla.").font = Font(italic=True)
c_ = ws.cell(VR[V[14]], 7, f"=B{rt+9}"); c_.fill = INFF; c_.font = BLUE; c_.number_format = NUM
ws.column_dimensions["A"].width = 62; ws.column_dimensions["C"].width = 26
for j in range(2, 3 + len(prods)): ws.column_dimensions[L(j)].width = max(ws.column_dimensions[L(j)].width or 0, 16)
MIX = VR[V[13]]; LAST = L(1 + len(prods))
c_ = WS01.cell(*PERS_CELL, f"=IFERROR(SUMPRODUCT('02_Productos'!B{VR[V[1]]}:{LAST}{VR[V[1]]},'02_Productos'!B{MIX}:{LAST}{MIX}),0)"); c_.number_format = DEC
MC_POND = f"SUMPRODUCT('02_Productos'!B{mc}:{LAST}{mc},'02_Productos'!B{MIX}:{LAST}{MIX})"
ING_POND = f"SUMPRODUCT('02_Productos'!B{b}:{LAST}{b},'02_Productos'!B{MIX}:{LAST}{MIX})"

# 03 Equilibrio
ws = wb.create_sheet("03_Equilibrio")
ws.cell(1, 1, "Costos fijos, punto de equilibrio y complejos necesarios").font = Font(bold=True)
hdr(ws, 3, ["Costo fijo mensual", "Importe", "Fuente"])
F = ["Coordinación / administración", "Seguros anuales prorrateados", "Mantenimiento de huellas y bases", "Comunicaciones",
     "Marketing y material para complejos", "Honorarios (contable, legal)", "Habilitaciones y tasas prorrateadas", "Otros"]
for i, f in enumerate(F, 4):
    ws.cell(i, 1, f); inp(ws.cell(i, 2), NUM); inp(ws.cell(i, 3))
fe = 3 + len(F)
rows = [("Costos fijos mensuales", f"=SUM(B4:B{fe})", NUM), ("Costos fijos anuales", f"=B{fe+1}*12", NUM),
        ("Margen medio por salida (según mix)", f"=IFERROR({MC_POND},0)", NUM), ("Ingreso medio por salida", f"=IFERROR({ING_POND},0)", NUM),
        ("SALIDAS DE EQUILIBRIO por año", f'=IF(B{fe+3}>0,B{fe+2}/B{fe+3},"Margen no positivo o sin datos")', DEC),
        ("Salidas operadas (compartidas) con los complejos cargados", f"={TOT_SAL}", DEC),
        ("Cobertura del equilibrio con la demanda actual", f'=IFERROR(B{fe+6}/B{fe+5},"")', PCT),
        ("Salidas compartidas que aporta en promedio cada complejo cargado", f"=IFERROR({TOT_SAL}/COUNTIF('01_Complejos'!K12:K19,\">0\"),0)", DEC),
        ("COMPLEJOS NECESARIOS para el equilibrio", f'=IFERROR(ROUNDUP(B{fe+5}/B{fe+8},0),"Faltan datos")', NUM)]
for k_, (a, f, fmt) in enumerate(rows, fe + 1):
    ws.cell(k_, 1, a).font = Font(bold=a.isupper() or a.startswith("SALIDAS") or a.startswith("COMPLEJOS")); ws.cell(k_, 2, f).number_format = fmt
ws.column_dimensions["A"].width = 50; ws.column_dimensions["B"].width = 18; ws.column_dimensions["C"].width = 30
FIJO_ANUAL = f"'03_Equilibrio'!B{fe+2}"; FIJO_MES = f"'03_Equilibrio'!B{fe+1}"; MCP = f"'03_Equilibrio'!B{fe+3}"; INGP = f"'03_Equilibrio'!B{fe+4}"

# 04 Escenarios
ws = wb.create_sheet("04_Escenarios")
ws.cell(1, 1, "Escenarios: factores sobre la demanda calculada, el precio y el costo variable (derivarlos del piloto)").font = Font(bold=True)
hdr(ws, 3, ["Variable", "Conservador", "Base", "Favorable"])
for i, v in enumerate(["Factor salidas", "Factor precio", "Factor costo variable"], 4):
    ws.cell(i, 1, v)
    for j in range(3): inp(ws.cell(i, 2 + j), "0.00")
out = [("Salidas/año", "={TOT}*{c}4"), ("Ventas", "={TOT}*{c}4*{ING}*{c}5"), ("Costo variable", "={TOT}*{c}4*({ING}-{MC})*{c}6"),
       ("Margen", "={c}9-{c}10"), ("Costos fijos", "={FA}"), ("Resultado operativo", "={c}11-{c}12")]
for i, (a, f) in enumerate(out, 8):
    ws.cell(i, 1, a).font = Font(bold=a.startswith("Resultado"))
    for j, c in enumerate("BCD"):
        ws.cell(i, 2 + j, f.format(c=c, TOT=TOT_SAL, ING=INGP, MC=MCP, FA=FIJO_ANUAL)).number_format = NUM
ws.column_dimensions["A"].width = 30
for c in "BCD": ws.column_dimensions[c].width = 18

# 05 Flujo 12 meses
ws = wb.create_sheet("05_Flujo_12m")
ws.cell(1, 1, "Flujo mensual del año piloto (escenario base). Estacionalidad: % de las salidas anuales en cada mes; tomarla de la ocupación de los complejos.").font = Font(bold=True)
meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
hdr(ws, 3, ["Concepto"] + meses + ["Total"])
ws.cell(4, 1, "Estacionalidad (%)")
for j in range(2, 14): inp(ws.cell(4, j), PCT)
ws.cell(4, 14, "=SUM(B4:M4)").number_format = PCT
fl = [("Salidas", "={TOT}*'04_Escenarios'!$C$4*{c}4", DEC), ("Ingresos", "={c}5*{ING}*'04_Escenarios'!$C$5", NUM),
      ("Costo variable", "=-{c}5*({ING}-{MC})*'04_Escenarios'!$C$6", NUM), ("Costos fijos", "=-{FM}", NUM)]
for i, (a, f, fmt) in enumerate(fl, 5):
    ws.cell(i, 1, a)
    for j in range(2, 14): ws.cell(i, j, f.format(c=L(j), TOT=TOT_SAL, ING=INGP, MC=MCP, FM=FIJO_MES)).number_format = fmt
    ws.cell(i, 14, f"=SUM(B{i}:M{i})").number_format = fmt
ws.cell(9, 1, "Inversión del mes")
for j in range(2, 14): inp(ws.cell(9, j), NUM)
ws.cell(9, 14, "=SUM(B9:M9)").number_format = NUM
ws.cell(10, 1, "FLUJO NETO").font = Font(bold=True); ws.cell(11, 1, "ACUMULADO").font = Font(bold=True)
for j in range(2, 14):
    c = L(j); ws.cell(10, j, f"={c}6+{c}7+{c}8-{c}9").number_format = NUM
    ws.cell(11, j, f"={c}10" if j == 2 else f"={L(j-1)}11+{c}10").number_format = NUM
ws.cell(13, 1, "Necesidad máxima de caja").font = Font(bold=True); ws.cell(13, 2, "=MIN(0,MIN(B11:M11))").number_format = NUM
ws.column_dimensions["A"].width = 26

# 06 CAPEX
ws = wb.create_sheet("06_CAPEX")
ws.cell(1, 1, "Inversiones por etapa: solo con cotización y condición de liberación").font = Font(bold=True)
hdr(ws, 3, ["Etapa", "Ítem", "Cantidad", "Costo unitario", "Total", "Cotización / proveedor", "Se libera si…"])
items = [("0", "Estudio de títulos y mensura", "Siempre (gate)"), ("0", "Asesoría legal, regulatoria y de seguros", "Siempre"),
         ("0", "Radios / comunicador satelital y botiquín", "Siempre"), ("0", "Combustible y jornadas de relevamiento", "Siempre"),
         ("1", "Material comercial para complejos (fotos, video, fichas, mapa ilustrado)", "GO Etapa 0"),
         ("1", "Mejoras mínimas en Base 1 Inicio y señalización", "GO Etapa 0"), ("1", "Kit de recuperación 4x4 y extintores", "GO Etapa 0"),
         ("2", "Adecuación de Vaquero y Chivero (cocina, sanitarios, espacios)", "GO Etapa 1 + habilitación"),
         ("3", "Vehículo propio (si conviene frente al aliado)", "GO Etapa 2 + análisis"), ("3", "Equipamiento invernal", "Prefactibilidad invernal"),
         ("4", "Alojamiento en el campo o base en Chile", "Estudio específico")]
for i, (e_, it, cond) in enumerate(items, 4):
    ws.cell(i, 1, e_); ws.cell(i, 2, it)
    for j in (3, 4, 6): inp(ws.cell(i, j), NUM if j == 4 else None)
    ws.cell(i, 5, f"=IFERROR(C{i}*D{i},0)").number_format = NUM; ws.cell(i, 7, cond)
end = 3 + len(items)
for k_, e_ in enumerate("01234"):
    ws.cell(end + 2 + k_, 2, f"Total Etapa {e_}"); ws.cell(end + 2 + k_, 5, f'=SUMIF(A4:A{end},"{e_}",E4:E{end})').number_format = NUM
ws.column_dimensions["B"].width = 62; ws.column_dimensions["F"].width = 24; ws.column_dimensions["G"].width = 28

# 07 Reparto (sociedad TM–Milenka)
ws = wb.create_sheet("07_Reparto")
ws.cell(1, 1, "Sociedad Tierras Mágicas – Milenka: comparten gastos y ganancias DE LAS TRAVESÍAS; cada uno administra su complejo y factura su alojamiento (CONF titular). Participación 50% / 50% y sin canon por el campo (CONF). Formalizar por escrito.").font = Font(bold=True)
hdr(ws, 3, ["Socio", "Participación (%)", "Aportes (texto)", "Resultado operativo asignado (escenario base)", "Inversión Etapas 0–1 asignada"])
for i, n in enumerate(["Tierras Mágicas", "Milenka"], 4):
    ws.cell(i, 1, n); inp(ws.cell(i, 2), PCT, 0.5, conf=True); inp(ws.cell(i, 3))
    ws.cell(i, 4, f"=IFERROR(($B$9)*B{i},0)").number_format = NUM
    ws.cell(i, 5, f"=IFERROR(($B$10)*B{i},0)").number_format = NUM
ws.cell(6, 1, "Control: suma de participaciones").font = Font(bold=True); ws.cell(6, 2, "=SUM(B4:B5)").number_format = PCT
ws.cell(8, 1, "Canon o compensación por uso del campo (CONF: no hay canon)"); inp(ws.cell(8, 2), NUM, 0, conf=True)
ws.cell(9, 1, "Resultado a repartir (base − canon)").font = Font(bold=True); ws.cell(9, 2, "='04_Escenarios'!C13-N(B8)").number_format = NUM
ws.cell(10, 1, "Inversión Etapas 0 y 1 a aportar").font = Font(bold=True); ws.cell(10, 2, "=SUMIF('06_CAPEX'!A4:A14,\"0\",'06_CAPEX'!E4:E14)+SUMIF('06_CAPEX'!A4:A14,\"1\",'06_CAPEX'!E4:E14)").number_format = NUM
ws.cell(13, 1, "El alojamiento del programa todo incluido (T4+) NO entra en el reparto: la sociedad lo paga al complejo que hospeda (hoja 02, fila Alojamiento).").font = Font(italic=True)
ws.cell(12, 1, "Asociados que se sumen después: por comisión sobre ventas (hoja 02), sin participar de gastos ni ganancias, salvo nuevo acuerdo.").font = Font(italic=True)
ws.column_dimensions["A"].width = 56; ws.column_dimensions["C"].width = 40; ws.column_dimensions["D"].width = 22; ws.column_dimensions["E"].width = 22
wb.save(sys.argv[1]); print("ok")
