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
    ("PASO DEL ARCO ADVENTURE — Modelo económico v3 (demanda desde complejos)", True),
    ("Acompaña al Plan de Negocios v3. Celdas amarillas con texto azul = datos de entrada (vacías: no se inventan importes). Celdas verdes = dato confirmado (plazas de Tierras Mágicas, sistema de reservas). Blancas = fórmulas.", False),
    ("Flujo: 01_Complejos (demanda) → 02_Productos (margen por salida) → 03_Equilibrio (salidas y complejos necesarios) → 04_Escenarios → 05_Flujo_12m → 06_CAPEX.", False),
    ("Recomendación: completar primero con datos del panel de Tierras Mágicas (ocupación, estadía media) y de Milenka, cotizaciones del prestador aliado y del seguro, y la tasa de compra medida en la preventa.", False),
], 1):
    c = ws.cell(i, 1, t); c.font = Font(bold=b, size=13 if i == 1 else 11); c.alignment = Alignment(wrap_text=True)
ws.column_dimensions["A"].width = 130

# 01 Complejos
ws = wb.create_sheet("01_Complejos")
ws.cell(1, 1, "Demanda potencial por complejo: salidas/año = plazas × 365 × ocupación ÷ estadía ÷ grupo × tasa de compra × travesías por estadía").font = Font(bold=True)
cols = ["Complejo", "Código", "Plazas", "Ocupación anual (%)", "Estadía media (noches)", "Personas por grupo", "Tasa de compra (%)", "Travesías por estadía",
        "Huéspedes/año", "Grupos/año", "Salidas demandadas/año", "Personas en travesía/año", "Fuente / nota"]
hdr(ws, 3, cols)
rows = [("Tierras Mágicas", "AMO-ALO-01", 16, "CONF: 3 cabañas (6+6+4); dormi de 4 adicional no incluido. Estadía mínima 2–3 noches."),
        ("Milenka", "PEND", None, "PEND: plazas, ubicación, vínculo"),
        ("Complejo asociado 3", "", None, ""), ("Complejo asociado 4", "", None, ""), ("Complejo asociado 5", "", None, ""),
        ("Complejo asociado 6", "", None, ""), ("Complejo asociado 7", "", None, ""), ("Complejo asociado 8", "", None, "")]
for i, (n, cod, pl, note) in enumerate(rows, 4):
    ws.cell(i, 1, n); ws.cell(i, 2, cod)
    inp(ws.cell(i, 3), NUM, pl, conf=pl is not None)
    for j, f in ((4, PCT), (5, DEC), (6, DEC), (7, PCT), (8, DEC)): inp(ws.cell(i, j), f)
    ws.cell(i, 9, f"=IFERROR(C{i}*365*D{i}/E{i},0)").number_format = NUM
    ws.cell(i, 10, f"=IFERROR(I{i}/F{i},0)").number_format = NUM
    ws.cell(i, 11, f"=IFERROR(J{i}*G{i}*H{i},0)").number_format = DEC
    ws.cell(i, 12, f"=IFERROR(K{i}*F{i},0)").number_format = NUM
    ws.cell(i, 13, note)
e = 3 + len(rows)
ws.cell(e + 1, 1, "TOTAL").font = Font(bold=True)
for j in (3, 9, 10, 11, 12): ws.cell(e + 1, j, f"=SUM({L(j)}4:{L(j)}{e})").number_format = NUM
ws.cell(e + 3, 1, "Techo teórico de Tierras Mágicas (100% ocupación)").font = Font(bold=True)
ws.cell(e + 4, 1, "Huéspedes/año con estadía de 2 noches"); ws.cell(e + 4, 3, "=C4*365/2").number_format = NUM
ws.cell(e + 5, 1, "Huéspedes/año con estadía de 3 noches"); ws.cell(e + 5, 3, "=C4*365/3").number_format = NUM
ws.cell(e + 6, 1, "Es un máximo: la demanda real es una fracción (ocupación < 100% y tasa de compra < 100%).").font = Font(italic=True)
for j, w in enumerate([24, 13, 8, 11, 11, 10, 10, 10, 11, 10, 12, 12, 50], 1): ws.column_dimensions[L(j)].width = w
TOT_SAL = f"'01_Complejos'!K{e+1}"

# 02 Productos
ws = wb.create_sheet("02_Productos")
ws.cell(1, 1, "Margen por salida — productos T1 a T5 (Plan v3). Traslado complejo↔campo separado del recorrido.").font = Font(bold=True)
G = [("Precio combustible por litro", ""), ("Consumo en ruta (l/100 km)", ""), ("Consumo en huella (l/100 km)", ""), ("Desgaste por km", ""),
     ("Hora de guía/conductor", ""), ("Hora de apoyo/cierre", ""), ("Hora de cocina/base", ""), ("Impuestos sobre ventas (%)", "")]
hdr(ws, 3, ["Parámetro global", "Valor", "Fuente"])
GR = {}
for i, (a, _) in enumerate(G, 4):
    ws.cell(i, 1, a); inp(ws.cell(i, 2), PCT if "%" in a else NUM); inp(ws.cell(i, 3)); GR[a] = f"$B${i}"
prods = ["T1 Medio día campo", "T2 Día campo + Vaquero", "T3 Campo + zona", "T4 Paquete (por travesía)", "T5 Convoy con tu 4x4"]
V = ["Precio por persona (T5: por vehículo)", "Personas (T5: vehículos) por salida", "Km de traslado ida y vuelta (≈70 desde TM; 0 si encuentro en tranquera)",
     "Km del recorrido (huella)", "Vehículos del operador por salida", "Horas de guía", "Horas de apoyo", "Horas de cocina/base", "Comida por persona",
     "Seguro por persona", "Consumibles por salida", "Comisión del complejo (%)", "Pago al prestador aliado por salida", "Mix de salidas (%)"]
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
ws.column_dimensions["A"].width = 58; ws.column_dimensions["C"].width = 22
for j in range(2, 3 + len(prods)): ws.column_dimensions[L(j)].width = max(ws.column_dimensions[L(j)].width or 0, 16)
MIX = VR[V[13]]; LAST = L(1 + len(prods))
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
        ("Salidas demandadas por todos los complejos", f"={TOT_SAL}", DEC),
        ("Cobertura del equilibrio con la demanda actual", f'=IFERROR(B{fe+6}/B{fe+5},"")', PCT),
        ("Salidas medias por complejo cargado", f"=IFERROR({TOT_SAL}/COUNTIF('01_Complejos'!K4:K11,\">0\"),0)", DEC),
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
wb.save(sys.argv[1]); print("ok")
