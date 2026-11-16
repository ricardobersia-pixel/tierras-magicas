# -*- coding: utf-8 -*-
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
sys.path.insert(0, sys.argv[1])
from data_v24 import *
IDX_POI = {p[0]: p for p in HR['poi']}

OUT = sys.argv[2]
wb = Workbook()
HDR = PatternFill("solid", fgColor="1F3A2E")
INP = PatternFill("solid", fgColor="FFF4CC")
SUB = PatternFill("solid", fgColor="DCE8DF")
thin = Side(style="thin", color="B7B7B7")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")
BLUE = Font(color="0000FF")
NUM = '#,##0;[Red]-#,##0;"-"'
PCT = '0.0%;[Red]-0.0%;"-"'

def sheet(title, headers, rows, widths, note=None):
    ws = wb.create_sheet(title)
    r0 = 1
    if note:
        ws.cell(1, 1, note).font = Font(italic=True, color="555555")
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
        ws.row_dimensions[1].height = 30
        ws.cell(1, 1).alignment = WRAP
        r0 = 2
    for j, h in enumerate(headers, 1):
        c = ws.cell(r0, j, h); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF"); c.alignment = WRAP; c.border = BOX
    for i, row in enumerate(rows, r0 + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v); c.alignment = WRAP; c.border = BOX
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(r0 + 1, 3 if len(headers) > 4 else 2)
    ws.auto_filter.ref = f"A{r0}:{get_column_letter(len(headers))}{r0 + len(rows)}"
    return ws

# 0 LEEME
ws = wb.active; ws.title = "00_Leeme"
lines = [
 ("PASO DEL ARCO ADVENTURE — Matrices y Modelo Económico-Financiero v2.4", True),
 ("Documento de trabajo. Complementa al 'Plan de Negocios Paso del Arco v2'. No habilita la operación ni constituye estudio de factibilidad.", False),
 ("", False),
 ("Etiquetas de evidencia usadas en todo el libro:", True),
 ("CONF = confirmado por el titular · EXT = extraído de archivos (dossier v1, anexo v1) · EXTW = investigación externa con fuente (ver hoja 15_Fuentes) · INF = inferencia analítica · HIP = hipótesis · REC = recomendación · PEND = pendiente", False),
 ("", False),
 ("Convenciones del modelo financiero:", True),
 ("Celdas amarillas con texto azul = datos de entrada (vacías a propósito: no se inventan importes). Celdas blancas = fórmulas. Moneda: definir en 08_Supuestos (REC: moneda constante + revisión mensual por inflación).", False),
 ("Los resultados mostrarán '-' o vacío hasta cargar cotizaciones y mediciones reales. La hoja 14_Datos_faltantes indica de dónde sale cada dato.", False),
 ("", False),
 ("Hojas:", True),
 ("01_Bases · 02_Circuitos_24 · 02b_Auditoria_GPX · 02c_Waypoints_53 · 19_Relevamiento_POI · 20_Codificacion · 21_Hoja_de_ruta · 03_Priorizacion · 04_Portafolio · 05_Modelos_negocio · 06_Etapas_GoNoGo · 07_Riesgos · 08_Supuestos · 09_Costo_salida · 10_Fijos_PE · 11_Escenarios · 12_Flujo_12m · 13_CAPEX_Rentab · 14_Datos_faltantes · 15_Discrepancias · 16_Implementacion · 17_Competencia · 18_Fuentes", False),
 ("", False),
 ("v2.1: auditoría de los 24 GPX (hojas 02b y 02c), reclasificaciones. v2.2: acceso RP13/RP12 con la coordenada del titular (-38.902440, -71.064667), distancias por trazas desde el acceso (01_Bases) y corrección de la estimación de v2.1. v2.3: RP12 pública que divide el campo (sectores O/E), Tranquera 1, km de cada traza sobre la RP12 (02b) y relevamiento de puntos de interés (hoja 19). v2.4: codificación ZONA-TIPO-NN (hoja 20) y hoja de ruta por jornadas (hoja 21).", True),
 ("Ningún dato original del Anexo v1 fue modificado: las columnas 'v1' reproducen el original y las columnas 'v2' contienen la propuesta.", False),
]
for i, (t, b) in enumerate(lines, 1):
    c = ws.cell(i, 1, t); c.font = Font(bold=b, size=13 if i == 1 else 11); c.alignment = WRAP
ws.column_dimensions["A"].width = 140

# 01 Bases
rows = [(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]) for b in BASES]
ws = sheet("01_Bases", ["Código", "Base / puesto", "Lat (EXT/CONF)", "Lon (EXT/CONF)", "Dato aportado (CONF)", "Función propuesta (HIP)", "Lectura analítica (INF/EXTW)", "Validaciones pendientes (PEND)"],
           rows, [14, 22, 12, 12, 38, 42, 60, 55])
r = len(rows) + 4
ws.cell(r, 1, "Distancias en línea recta (cálculo propio, haversine, R=6371 km). NO equivalen a distancia por camino ni prueban conexión física.").font = Font(bold=True)
for j, h in enumerate(["Desde", "Hasta", "km línea recta", "Rumbo (°) / distancia por trazas"], 1):
    c = ws.cell(r + 1, j, h); c.fill = SUB; c.font = Font(bold=True)
for i, d in enumerate(DIST_BASES, r + 2):
    for j, v in enumerate(d, 1): ws.cell(i, j, v)
r2 = r + 2 + len(DIST_BASES) + 1
ra = r2 + 2
ws.cell(ra, 1, "ACCESO: " + ACCESO["nombre"]).font = Font(bold=True)
for k_, (lab, val) in enumerate([("Dato del titular", ACCESO["dato_titular"]), ("Coordenada (CONF titular)", f'{ACCESO["lat"]:.6f}, {ACCESO["lon"]:.6f}'), ("Método", ACCESO["metodo"]), ("Altitud", ACCESO["elev"])], ra + 1):
    ws.cell(k_, 1, lab).font = Font(bold=True); c_ = ws.cell(k_, 2, val); c_.alignment = WRAP
    ws.merge_cells(start_row=k_, start_column=2, end_row=k_, end_column=8); ws.row_dimensions[k_].height = 30
ws.cell(r2, 1, "Lectura: las tres bases forman un triángulo de ≈1,55 km² (≈155 ha). El resto del campo (~1.845 ha si se confirma la superficie) queda sin nodos: oportunidad de un nodo de retorno/evacuación en el extremo opuesto (¿puesto del Arroyo del Arco?).").alignment = WRAP
ws.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=8); ws.row_dimensions[r2].height = 32

# 02 Circuitos
rows = []
for c in CIRCUITOS:
    nwp = 0 if not c[5] else len(c[5].split(";"))
    rows.append((c[0], c[1], c[2], "Catálogo Preliminar (EXT) = reproducido exacto en recálculo v2.1 (haversine). Ver 02b: km netos sin saltos", nwp, c[5] or "—",
                 c[3], c[4], c[7], CATS[c[8]], CATS[c[9]] if c[9] else "", c[10], c[11], c[12], c[13], c[14], c[15], c[16], c[17],
                 "No comercializable hasta validación (EXT)"))
ws = sheet("02_Circuitos_24",
           ["Código", "Nombre GPX (original)", "km catálogo (EXT)", "Fuente / calidad del km", "N° waypoints", "Waypoints (EXT)",
            "Familia v1 (EXT)", "Base sugerida v1 (HIP v1)", "Relación con bases (dato disponible)", "Clasificación v2.1–2.2 (propuesta)", "Clasif. alternativa",
            "Justificación (INF)", "Potencial paisajístico (INF)", "Usos posibles (HIP)", "Estacionalidad a investigar", "Requisitos de inspección (REC)",
            "Riesgos / restricciones", "Información faltante (PEND)", "Ola de inspección (REC v2.1)", "Estado"],
           rows, [12, 34, 10, 22, 9, 40, 22, 22, 26, 24, 20, 55, 35, 38, 32, 45, 35, 35, 18, 20],
           note="Categorías v2 son PROPUESTAS DE ANÁLISIS, no clasificaciones aprobadas. Proximidad = distancia del punto GPS más cercano a la base (Dossier v1): no prueba acceso.")
for i in range(3, 3 + len(rows)):
    ws.cell(i, 3).number_format = "0.00"
r = 3 + len(rows) + 1
ws.cell(r, 2, "Total km catálogo").font = Font(bold=True)
ws.cell(r, 3, f"=SUM(C3:C{2+len(rows)})").number_format = "0.00"
ws.cell(r + 1, 2, "Total waypoints listados").font = Font(bold=True)
ws.cell(r + 1, 5, f"=SUM(E3:E{2+len(rows)})")
ws.cell(r + 1, 6, "Dossier v1 declara 53 → ver 15_Discrepancias X02")
ws.cell(r + 3, 2, "Resumen por categoría v2").font = Font(bold=True)
for k, (n, name) in enumerate(CATS.items()):
    ws.cell(r + 4 + k, 2, name)
    ws.cell(r + 4 + k, 3, f'=COUNTIF(J3:J{2+len(rows)},B{r+4+k})')


# 02b Auditoría GPX
rows = []
for c in CIRCUITOS:
    g = GPX[c[1]]
    rows.append((c[0], c[1], g["file"], g["sha256"][:16], g["n_points"], g["km"], g["km_sin_saltos_1km"], g["n_jumps"],
                 ", ".join(f"{j:.2f}" for j in g["jumps_km"]) or "—", g["t_start"][:10], g["t_start"][11:16] + "–" + g["t_end"][11:16] + " UTC",
                 g["elapsed_h"], g["moving_h"], round(g["km_sin_saltos_1km"] / g["moving_h"], 1) if g["moving_h"] else None,
                 g["ele_min"], g["ele_max"], g["gain_m"], g["start_end_km"], RP12_TRACK[c[1]]["km_sobre_RP12"], RP12_TRACK[c[1]]["pct_sobre_RP12"], g["near"]["Inicio"]["km"], g["near"]["Vaquero"]["km"],
                 g["near"]["Chivero"]["km"], g["near"]["Litrán"]["km"], g["pct_nucleo_proxy"], g["pct_celdas_nuevas"],
                 "; ".join(f"{n} {p}%" for n, p in g["overlaps"][:3]) or "—"))
ws = sheet("02b_Auditoria_GPX", ["Código", "Nombre", "Archivo", "SHA-256 (16)", "Puntos", "km (haversine)", "km sin saltos >1 km", "N° saltos >200 m", "Saltos (km)",
     "Fecha registro (UTC)", "Hora inicio–fin", "Horas transcurridas", "Horas en movimiento (≥2 km/h)", "Vel. media en mov. (km/h)", "Alt. mín (m)*", "Alt. máx (m)*", "Desnivel + (m)*",
     "Inicio–fin (km)", "km sobre RP12 (acceso–Cruce N)", "% sobre RP12", "Mín. a Inicio (km)", "Mín. a Vaquero (km)", "Mín. a Chivero (km)", "Mín. a Litrán (km)", "% km en radio proxy 3 km", "% traza única", "Principales superposiciones"],
     rows, [11, 30, 30, 18, 8, 9, 9, 8, 16, 11, 14, 9, 10, 9, 8, 8, 8, 8, 9, 8, 8, 8, 8, 8, 9, 8, 50],
     note="Recálculo reproducible (scripts/gpx_analyze.py): " + GPX_PARAMS["metodo"] + ". *Altitudes GPX con sesgos entre archivos (X11): no usar para dificultad. Radio proxy = 3 km alrededor de alguna base; NO es el límite del campo. Tiempos = registro de Wikiloc, no duración comercial.")
# 02c Waypoints
rows = []
for c in CIRCUITOS:
    for w in GPX[c[1]]["wpts"]:
        rows.append((c[0], c[1], w["name"], w["lat"], w["lon"], round(w["ele"]) if w["ele"] is not None else None, w["base_mas_cercana"], w["km_a_base"], w["km_al_track"]))
ws = sheet("02c_Waypoints_53", ["Código", "Track", "Waypoint", "Lat", "Lon", "Alt GPX (m)*", "Base más cercana", "km a la base", "km al track"], rows,
           [11, 34, 26, 11, 11, 9, 12, 9, 9], note="53 waypoints extraídos de los GPX (EXT). Proximidad en línea recta. *Altitud con sesgo según archivo.")

# 03 Priorización
ws = wb.create_sheet("03_Priorizacion")
ws.cell(1, 1, "Priorización para INSPECCIÓN (no para comercialización). Puntajes 1–5 = juicio analítico (INF) sobre datos extraídos; pesos = REC editables (amarillo). Ajustar tras gabinete GPX.").font = Font(italic=True)
ws.merge_cells("A1:L1")
ws.cell(3, 1, "Criterio").font = Font(bold=True); ws.cell(3, 2, "Descripción").font = Font(bold=True); ws.cell(3, 3, "Peso").font = Font(bold=True)
for i, (k, d, w) in enumerate(CRITERIOS, 4):
    ws.cell(i, 1, k); ws.cell(i, 2, d); c = ws.cell(i, 3, w); c.fill = INP; c.font = BLUE; c.number_format = "0%"
ws.cell(9, 2, "Suma de pesos (debe ser 100%)"); ws.cell(9, 3, "=SUM(C4:C8)").number_format = "0%"
hdr = ["Código", "Nombre", "km", "Clasificación v2", "C1", "C2", "C3", "C4", "C5", "Puntaje ponderado", "Ranking", "Ola (REC)"]
for j, h in enumerate(hdr, 1):
    c = ws.cell(11, j, h); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF"); c.alignment = WRAP
for i, c in enumerate(CIRCUITOS, 12):
    ws.cell(i, 1, c[0]); ws.cell(i, 2, c[1]); ws.cell(i, 3, c[2]); ws.cell(i, 4, CATS[c[8]])
    for j, s in enumerate(c[18]):
        x = ws.cell(i, 5 + j, s); x.fill = INP; x.font = BLUE
    ws.cell(i, 10, f"=SUMPRODUCT(E{i}:I{i},TRANSPOSE($C$4:$C$8))")
    ws.cell(i, 10).value = f"=E{i}*$C$4+F{i}*$C$5+G{i}*$C$6+H{i}*$C$7+I{i}*$C$8"
    ws.cell(i, 10).number_format = "0.00"
    ws.cell(i, 11, f"=RANK(J{i},$J$12:$J$35)")
    ws.cell(i, 12, c[17])
last = 11 + len(CIRCUITOS)
ws.conditional_formatting.add(f"J12:J{last}", CellIsRule(operator="greaterThanOrEqual", formula=["3.5"], fill=PatternFill("solid", fgColor="C6EFCE")))
ws.conditional_formatting.add(f"J12:J{last}", CellIsRule(operator="lessThan", formula=["2"], fill=PatternFill("solid", fgColor="F4CCCC")))
for col, w in zip("ABCDEFGHIJKL", [12, 40, 8, 26, 5, 5, 5, 5, 5, 11, 8, 26]):
    ws.column_dimensions[col].width = w
ws.column_dimensions["B"].width = 60

# 04 Portafolio
ws = sheet("04_Portafolio", ["Cód.", "Producto", "Familia", "Concepto", "Cliente objetivo", "Experiencia", "Recursos", "Base", "Estructura de costos",
                             "Variables de precio", "Canales", "Riesgos", "Validaciones", "Etapa (REC)", "Circuitos candidatos"],
           [p for p in PORTAFOLIO], [6, 30, 20, 40, 32, 38, 34, 14, 32, 30, 26, 30, 32, 16, 22],
           note="Sin tarifas ni capacidades: se completan en 08_Supuestos tras medir y cotizar. Productos = HIP de diseño.")

# 05 Modelos
ws = sheet("05_Modelos_negocio", ["Alt.", "Modelo", "Ventajas", "Desventajas", "Inversión", "Costos", "Riesgos", "Escalabilidad"],
           MODELOS, [5, 30, 45, 45, 28, 30, 35, 22],
           note="REC: iniciar con D (C + B), sin flota propia hasta superar el gate de Etapa 1. Comparación económica en 09_Costo_salida (bloque modelos).")

# 06 Etapas
ws = sheet("06_Etapas_GoNoGo", ["Etapa", "Horizonte", "Alcance", "Inversión admisible", "Criterios GO / NO-GO (REC)", "Entregable de decisión"],
           ETAPAS, [26, 18, 50, 40, 70, 20])

# 07 Riesgos
ws = sheet("07_Riesgos", ["ID", "Categoría", "Riesgo", "Probabilidad", "Impacto", "Mitigación", "Responsable", "Momento"],
           RIESGOS, [6, 18, 60, 14, 10, 55, 22, 18])

# 08 Supuestos
ws = wb.create_sheet("08_Supuestos")
ws.cell(1, 1, "DATOS DE ENTRADA — todas las celdas amarillas están vacías a propósito. Completar con cotizaciones/mediciones y anotar fuente.").font = Font(bold=True)
glob = [("Moneda del modelo", "", "texto"), ("Precio combustible por litro", "", "cotización estación de servicio local"),
        ("Consumo vehículo (l/100 km) en terreno", "", "medición en pilotos"), ("Desgaste/mantenimiento por km", "", "taller + historial"),
        ("Costo hora guía/chofer", "", "convenio/cotización"), ("Costo hora apoyo/cierre", "", "convenio/cotización"),
        ("Costo hora cocina/base", "", "convenio/cotización"), ("Impuestos sobre ventas (%)", "", "contador"),
        ("Tasa de descuento anual (%)", "", "titular/CFO"), ("Crecimiento anual de salidas (%)", "", "REC tras piloto"),
        ("Meses de cobertura de capital de trabajo", "", "CFO")]
ws.cell(3, 1, "Parámetro global").font = Font(bold=True); ws.cell(3, 2, "Valor").font = Font(bold=True); ws.cell(3, 3, "Fuente esperada").font = Font(bold=True)
for i, (a, b, s) in enumerate(glob, 4):
    ws.cell(i, 1, a); c = ws.cell(i, 2); c.fill = INP; c.font = BLUE; ws.cell(i, 3, s)
G = {k: f"'08_Supuestos'!$B${i}" for i, k in enumerate(["mon", "comb", "cons", "desg", "hg", "ha", "hc", "imp", "tasa", "crec", "ct"], 4)}
PRODS = ["P01 Bautismo 4x4", "P02 Campo + Vaquero", "P03 Jornada completa", "P04 Mesa Vaquero", "P05 Chivero", "P07 Tag-along", "P08 Escuela 4x4"]
pvars = [("Precio por pax (o por vehículo en P07)", "relevamiento + test DAP"), ("Pax (o vehículos) por salida", "capacidad evaluada"),
         ("Km por salida (recalculados)", "GPX + piloto"), ("Vehículos del operador por salida", "diseño de producto"),
         ("Horas guía por salida", "piloto"), ("Horas apoyo por salida", "piloto"), ("Horas cocina/base por salida", "piloto"),
         ("Alimentos por pax", "cotización + receta"), ("Seguro por pax", "póliza"), ("Consumibles por salida", "cotización"),
         ("Comisión de canal (%)", "acuerdo con aliados"), ("Pago a prestador aliado por salida (modelo C)", "acuerdo"),
         ("Mix de salidas (% del total)", "piloto"), ("Salidas por año — escenario base", "test de demanda")]
r0 = 17
ws.cell(r0 - 1, 1, "Supuestos por producto").font = Font(bold=True)
ws.cell(r0, 1, "Variable").font = Font(bold=True)
for j, p in enumerate(PRODS, 2):
    c = ws.cell(r0, j, p); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF"); c.alignment = WRAP
ws.cell(r0, 2 + len(PRODS), "Fuente esperada").font = Font(bold=True)
PV = {}
for i, (v, s) in enumerate(pvars, r0 + 1):
    ws.cell(i, 1, v)
    for j in range(len(PRODS)):
        c = ws.cell(i, 2 + j); c.fill = INP; c.font = BLUE
        if "%" in v: c.number_format = "0.0%"
    ws.cell(i, 2 + len(PRODS), s)
    PV[v] = i
ws.cell(r0 + len(pvars) + 1, 1, "Control: suma del mix").font = Font(bold=True)
ws.cell(r0 + len(pvars) + 1, 2, f"=SUM(B{PV['Mix de salidas (% del total)']}:{get_column_letter(1+len(PRODS))}{PV['Mix de salidas (% del total)']})").number_format = "0%"
ws.column_dimensions["A"].width = 46
for j in range(2, 3 + len(PRODS)): ws.column_dimensions[get_column_letter(j)].width = 16
ws.column_dimensions[get_column_letter(2 + len(PRODS))].width = 26

def S(var, j):  # reference to supuesto
    return f"'08_Supuestos'!{get_column_letter(2+j)}${PV[var]}"

# 09 Costo por salida
ws = wb.create_sheet("09_Costo_salida")
ws.cell(1, 1, "Costo y margen de contribución por salida (fórmulas; se completan solas al cargar 08_Supuestos)").font = Font(bold=True)
for j, p in enumerate(PRODS, 2):
    c = ws.cell(3, j, p); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF"); c.alignment = WRAP
L = {}
def line(r, label, fn, fmt=NUM, bold=False):
    ws.cell(r, 1, label).font = Font(bold=bold)
    for j in range(len(PRODS)):
        c = ws.cell(r, 2 + j, fn(j)); c.number_format = fmt
        if bold: c.font = Font(bold=True)
    L[label] = r
col = lambda j: get_column_letter(2 + j)
line(4, "Ingreso bruto por salida", lambda j: f'=IFERROR({S("Precio por pax (o por vehículo en P07)",j)}*{S("Pax (o vehículos) por salida",j)},0)', bold=True)
line(5, "Impuestos sobre ventas", lambda j: f"=IFERROR({col(j)}4*{G['imp']},0)")
line(6, "Comisión de canal", lambda j: f'=IFERROR({col(j)}4*{S("Comisión de canal (%)",j)},0)')
line(7, "Combustible", lambda j: f'=IFERROR({S("Km por salida (recalculados)",j)}*{G["cons"]}/100*{G["comb"]}*{S("Vehículos del operador por salida",j)},0)')
line(8, "Desgaste / mantenimiento", lambda j: f'=IFERROR({S("Km por salida (recalculados)",j)}*{G["desg"]}*{S("Vehículos del operador por salida",j)},0)')
line(9, "Personal guía", lambda j: f'=IFERROR({S("Horas guía por salida",j)}*{G["hg"]},0)')
line(10, "Personal apoyo", lambda j: f'=IFERROR({S("Horas apoyo por salida",j)}*{G["ha"]},0)')
line(11, "Personal cocina/base", lambda j: f'=IFERROR({S("Horas cocina/base por salida",j)}*{G["hc"]},0)')
line(12, "Alimentos", lambda j: f'=IFERROR({S("Alimentos por pax",j)}*{S("Pax (o vehículos) por salida",j)},0)')
line(13, "Seguro por pax", lambda j: f'=IFERROR({S("Seguro por pax",j)}*{S("Pax (o vehículos) por salida",j)},0)')
line(14, "Consumibles", lambda j: f'=IFERROR({S("Consumibles por salida",j)}*1,0)')
line(15, "Pago a prestador aliado (modelo C)", lambda j: f'=IFERROR({S("Pago a prestador aliado por salida (modelo C)",j)}*1,0)')
line(16, "COSTO VARIABLE TOTAL", lambda j: f"=SUM({col(j)}5:{col(j)}15)", bold=True)
line(17, "MARGEN DE CONTRIBUCIÓN por salida", lambda j: f"={col(j)}4-{col(j)}16", bold=True)
line(18, "MC %", lambda j: f'=IF({col(j)}4=0,"",{col(j)}17/{col(j)}4)', fmt=PCT)
line(19, "MC por pax", lambda j: f'=IFERROR({col(j)}17/{S("Pax (o vehículos) por salida",j)},"")')
line(20, "Precio mínimo por pax para MC = 0", lambda j: f'=IFERROR(({col(j)}16-{col(j)}5-{col(j)}6)/{S("Pax (o vehículos) por salida",j)}/(1-{G["imp"]}-{S("Comisión de canal (%)",j)}),"")')
ws.cell(22, 1, "Comparación de modelos de vehículo (por salida, producto P02 de referencia)").font = Font(bold=True)
cmp_inputs = [("Valor de compra del vehículo (A)", ""), ("Valor residual (A)", ""), ("Km de vida útil (A)", ""),
              ("Seguro anual de flota por vehículo (A)", ""), ("Salidas anuales por vehículo (A)", "")]
for i, (a, _) in enumerate(cmp_inputs, 23):
    ws.cell(i, 1, a); c = ws.cell(i, 2); c.fill = INP; c.font = BLUE
ws.cell(29, 1, "A — Depreciación por salida (propio)"); ws.cell(29, 2, f'=IFERROR((B23-B24)/B25*{S("Km por salida (recalculados)",1)},0)').number_format = NUM
ws.cell(30, 1, "A — Seguro de flota por salida"); ws.cell(30, 2, "=IFERROR(B26/B27,0)").number_format = NUM
ws.cell(31, 1, "A — Costo vehicular total por salida (combustible+desgaste+depr.+seguro)"); ws.cell(31, 2, "=C7+C8+B29+B30").number_format = NUM
ws.cell(32, 1, "C — Pago a prestador aliado por salida"); ws.cell(32, 2, "=C15").number_format = NUM
ws.cell(33, 1, "B — Vehículo del cliente: costo vehicular del operador"); ws.cell(33, 2, 0)
ws.cell(34, 1, "Diferencia A − C (si >0, conviene aliado a este volumen)"); ws.cell(34, 2, "=B31-B32").number_format = NUM
ws.column_dimensions["A"].width = 58
for j in range(2, 3 + len(PRODS)): ws.column_dimensions[get_column_letter(j)].width = 16

# 10 Fijos y PE
ws = wb.create_sheet("10_Fijos_PE")
ws.cell(1, 1, "Costos fijos mensuales (OPEX) y punto de equilibrio").font = Font(bold=True)
fijos = ["Personal permanente (dirección/operaciones/administración)", "Seguros anuales prorrateados", "Mantenimiento de bases y huellas",
         "Servicios (energía, agua, comunicaciones, internet satelital)", "Marketing digital y material", "Software de reservas / contabilidad",
         "Honorarios profesionales (contable, legal)", "Habilitaciones, tasas y registros prorrateados", "Capacitación prorrateada", "Otros"]
ws.cell(3, 1, "Concepto").font = Font(bold=True); ws.cell(3, 2, "Mensual").font = Font(bold=True); ws.cell(3, 3, "Fuente").font = Font(bold=True)
for i, f in enumerate(fijos, 4):
    ws.cell(i, 1, f); c = ws.cell(i, 2); c.fill = INP; c.font = BLUE; c.number_format = NUM
    c = ws.cell(i, 3); c.fill = INP; c.font = BLUE
ws.cell(14, 1, "TOTAL COSTOS FIJOS MENSUALES").font = Font(bold=True); ws.cell(14, 2, "=SUM(B4:B13)").number_format = NUM
ws.cell(15, 1, "TOTAL COSTOS FIJOS ANUALES").font = Font(bold=True); ws.cell(15, 2, "=B14*12").number_format = NUM
mix_r = PV["Mix de salidas (% del total)"]
ws.cell(17, 1, "MC ponderado por salida (según mix)").font = Font(bold=True)
ws.cell(17, 2, f"=SUMPRODUCT('09_Costo_salida'!B17:{get_column_letter(1+len(PRODS))}17,'08_Supuestos'!B{mix_r}:{get_column_letter(1+len(PRODS))}{mix_r})").number_format = NUM
ws.cell(18, 1, "Ingreso ponderado por salida").font = Font(bold=True)
ws.cell(18, 2, f"=SUMPRODUCT('09_Costo_salida'!B4:{get_column_letter(1+len(PRODS))}4,'08_Supuestos'!B{mix_r}:{get_column_letter(1+len(PRODS))}{mix_r})").number_format = NUM
ws.cell(19, 1, "PUNTO DE EQUILIBRIO — salidas por año").font = Font(bold=True)
ws.cell(19, 2, '=IF(B17>0,B15/B17,"MC no positivo o sin datos")').number_format = "#,##0.0"
ws.cell(20, 1, "PUNTO DE EQUILIBRIO — salidas por mes promedio")
ws.cell(20, 2, '=IFERROR(B19/12,"")').number_format = "#,##0.0"
ws.cell(21, 1, "PUNTO DE EQUILIBRIO — ventas anuales")
ws.cell(21, 2, '=IFERROR(B19*B18,"")').number_format = NUM
ws.cell(23, 1, "Capital de trabajo (cobertura de fijos en temporada baja)").font = Font(bold=True)
ws.cell(23, 2, f"=IFERROR(B14*{G['ct']},0)").number_format = NUM
ws.cell(25, 1, "Lectura: con estacionalidad marcada, el equilibrio anual puede ocultar meses deficitarios: ver 12_Flujo_12m.").font = Font(italic=True)
ws.column_dimensions["A"].width = 60; ws.column_dimensions["B"].width = 20; ws.column_dimensions["C"].width = 30

# 11 Escenarios
ws = wb.create_sheet("11_Escenarios")
ws.cell(1, 1, "Escenarios — estructura de modelización (factores a definir; no son pronósticos)").font = Font(bold=True)
hd = ["Variable", "Conservador", "Base", "Favorable"]
for j, h in enumerate(hd, 1):
    c = ws.cell(3, j, h); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF")
vars_ = ["Factor salidas vs. base", "Factor precio vs. base", "Factor costo variable vs. base"]
for i, v in enumerate(vars_, 4):
    ws.cell(i, 1, v)
    for j in range(3):
        c = ws.cell(i, 2 + j); c.fill = INP; c.font = BLUE; c.number_format = "0.00"
ws.cell(7, 1, "Sugerencia (REC, editable): derivar factores de los resultados del piloto, no de supuestos de escritorio.").font = Font(italic=True)
sal_r = PV["Salidas por año — escenario base"]
ws.cell(9, 1, "Salidas base anuales (suma)"); ws.cell(9, 3, f"=SUM('08_Supuestos'!B{sal_r}:{get_column_letter(1+len(PRODS))}{sal_r})").number_format = NUM
ws.cell(10, 1, "Ingreso medio por salida (base)"); ws.cell(10, 3, "=IFERROR('10_Fijos_PE'!B18,0)").number_format = NUM
ws.cell(11, 1, "Costo variable medio por salida (base)"); ws.cell(11, 3, "=IFERROR('10_Fijos_PE'!B18-'10_Fijos_PE'!B17,0)").number_format = NUM
outs = [("Salidas anuales", "=$C$9*{c}4"), ("Ventas", "=$C$9*{c}4*$C$10*{c}5"), ("Costo variable", "=$C$9*{c}4*$C$11*{c}6"),
        ("Margen de contribución", "={c}14-{c}15"), ("Costos fijos anuales", "='10_Fijos_PE'!$B$15"), ("Resultado operativo (EBITDA aprox.)", "={c}16-{c}17")]
for i, (lab, f) in enumerate(outs, 13):
    ws.cell(i, 1, lab).font = Font(bold=lab.startswith("Resultado"))
    for j, c_ in enumerate("BCD"):
        ws.cell(i, 2 + j, f.format(c=c_)).number_format = NUM
ws.column_dimensions["A"].width = 42
for c_ in "BCD": ws.column_dimensions[c_].width = 18

# 12 Flujo 12 meses
ws = wb.create_sheet("12_Flujo_12m")
ws.cell(1, 1, "Flujo de caja mensual — año piloto (escenario base). Índice de estacionalidad = % de las salidas anuales en cada mes (debe sumar 100%).").font = Font(bold=True)
meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
ws.cell(3, 1, "Concepto").font = Font(bold=True)
for j, m in enumerate(meses, 2):
    c = ws.cell(3, j, m); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF")
ws.cell(3, 14, "Total").font = Font(bold=True)
ws.cell(4, 1, "Índice estacionalidad (%) — dato a relevar (Observatorio + piloto)")
for j in range(2, 14):
    c = ws.cell(4, j); c.fill = INP; c.font = BLUE; c.number_format = "0%"
ws.cell(4, 14, "=SUM(B4:M4)").number_format = "0%"
rows_f = [("Salidas", "='11_Escenarios'!$C$9*{c}4", "#,##0.0"), ("Ingresos", "={c}5*'11_Escenarios'!$C$10", NUM),
          ("Costo variable", "=-{c}5*'11_Escenarios'!$C$11", NUM), ("Costos fijos", "=-'10_Fijos_PE'!$B$14", NUM)]
for i, (lab, f, fmt) in enumerate(rows_f, 5):
    ws.cell(i, 1, lab)
    for j in range(2, 14):
        ws.cell(i, j, f.format(c=get_column_letter(j))).number_format = fmt
    ws.cell(i, 14, f"=SUM(B{i}:M{i})").number_format = fmt
ws.cell(9, 1, "CAPEX del mes (cargar)")
for j in range(2, 14):
    c = ws.cell(9, j); c.fill = INP; c.font = BLUE; c.number_format = NUM
ws.cell(9, 14, "=SUM(B9:M9)").number_format = NUM
ws.cell(10, 1, "FLUJO NETO").font = Font(bold=True)
ws.cell(11, 1, "FLUJO ACUMULADO").font = Font(bold=True)
for j in range(2, 14):
    c = get_column_letter(j)
    ws.cell(10, j, f"={c}6+{c}7+{c}8-{c}9").number_format = NUM
    ws.cell(11, j, f"={c}10" if j == 2 else f"={get_column_letter(j-1)}11+{c}10").number_format = NUM
ws.cell(10, 14, "=SUM(B10:M10)").number_format = NUM
ws.cell(13, 1, "Necesidad máxima de caja (mínimo acumulado)").font = Font(bold=True)
ws.cell(13, 2, "=MIN(0,MIN(B11:M11))").number_format = NUM
ws.column_dimensions["A"].width = 52

# 13 CAPEX y rentabilidad
ws = wb.create_sheet("13_CAPEX_Rentab")
ws.cell(1, 1, "CAPEX por etapa (solo ítems; importes a cotizar) y rentabilidad a 5 años").font = Font(bold=True)
hd = ["Etapa", "Ítem", "Cantidad", "Costo unitario", "Total", "Proveedor / cotización", "Condición de liberación"]
for j, h in enumerate(hd, 1):
    c = ws.cell(3, j, h); c.fill = HDR; c.font = Font(bold=True, color="FFFFFF"); c.alignment = WRAP
capex = [
 ("0", "Estudio de títulos, mensura y catastro", "Siempre (gate)"), ("0", "Asesoría legal-regulatoria y de seguros", "Siempre"),
 ("0", "GPS/tablet + software SIG + recálculo GPX", "Siempre"), ("0", "Radios VHF/handies y botiquines", "Siempre"),
 ("0", "Combustible y jornadas de inspección Ola 1", "Siempre"), ("0", "Análisis de agua en bases", "Siempre"),
 ("1", "Mejoras indispensables Base Inicio (sanitarios, accesibilidad, señalética)", "GO Etapa 0"),
 ("1", "Comunicador satelital / repetidora (según medición de cobertura)", "GO Etapa 0"),
 ("1", "Kit de recuperación 4x4 (eslingas, grilletes, pala, compresor)", "GO Etapa 0"),
 ("1", "Extintores y equipamiento de prevención de incendios", "GO Etapa 0"),
 ("1", "Web, reservas, fotografía/video propios", "GO Etapa 0"),
 ("2", "Adecuación cocina/servicio Vaquero", "GO Etapa 1 + habilitación"),
 ("2", "Espacio familiar Chivero (vallados, sombra, juegos rurales)", "GO Etapa 1"),
 ("2", "Sanitarios en Vaquero/Chivero", "GO Etapa 1"),
 ("3", "Vehículos propios (si modelo A supera a C en 09_Costo_salida)", "GO Etapa 2 + análisis A vs C"),
 ("3", "Equipamiento invernal (cadenas, raquetas, rescate)", "Prefactibilidad invernal"),
 ("4", "Lodge / alojamiento", "Estudio de factibilidad independiente"),
]
for i, (e, it, cond) in enumerate(capex, 4):
    ws.cell(i, 1, e); ws.cell(i, 2, it)
    for j in (3, 4, 6):
        c = ws.cell(i, j); c.fill = INP; c.font = BLUE
    ws.cell(i, 4).number_format = NUM
    ws.cell(i, 5, f"=IFERROR(C{i}*D{i},0)").number_format = NUM
    ws.cell(i, 7, cond)
end = 3 + len(capex)
r = end + 2
ws.cell(r, 1, "Totales por etapa").font = Font(bold=True)
for k, e in enumerate(["0", "1", "2", "3", "4"]):
    ws.cell(r + 1 + k, 1, f"Etapa {e}"); ws.cell(r + 1 + k, 5, f'=SUMIF(A4:A{end},"{e}",E4:E{end})').number_format = NUM
ws.cell(r + 6, 1, "CAPEX Etapas 0–2").font = Font(bold=True); ws.cell(r + 6, 5, f"=SUM(E{r+1}:E{r+3})").number_format = NUM
rr = r + 9
ws.cell(rr, 1, "Rentabilidad 5 años (escenario base, Etapas 0–2)").font = Font(bold=True)
for j, h in enumerate(["", "Año 0", "Año 1", "Año 2", "Año 3", "Año 4", "Año 5"], 1):
    c = ws.cell(rr + 1, j, h); c.fill = SUB; c.font = Font(bold=True)
ws.cell(rr + 2, 1, "Inversión (CAPEX 0–2 + capital de trabajo)")
ws.cell(rr + 2, 2, f"=-(E{r+6}+'10_Fijos_PE'!B23)").number_format = NUM
ws.cell(rr + 3, 1, "Resultado operativo (año 1 = escenario base; crece según 08_Supuestos)")
ws.cell(rr + 3, 3, "='11_Escenarios'!C18").number_format = NUM
for j in range(4, 8):
    ws.cell(rr + 3, j, f"={get_column_letter(j-1)}{rr+3}*(1+{G['crec']})").number_format = NUM
ws.cell(rr + 4, 1, "Flujo neto").font = Font(bold=True)
for j in range(2, 8):
    ws.cell(rr + 4, j, f"=N({get_column_letter(j)}{rr+2})+N({get_column_letter(j)}{rr+3})").number_format = NUM
ws.cell(rr + 5, 1, "Flujo acumulado")
for j in range(2, 8):
    ws.cell(rr + 5, j, f"={get_column_letter(j)}{rr+4}" if j == 2 else f"={get_column_letter(j-1)}{rr+5}+{get_column_letter(j)}{rr+4}").number_format = NUM
ws.cell(rr + 7, 1, "VAN (tasa en 08_Supuestos)").font = Font(bold=True)
ws.cell(rr + 7, 2, f'=IF({G["tasa"]}="","Falta tasa",B{rr+4}+NPV({G["tasa"]},C{rr+4}:G{rr+4}))').number_format = NUM
ws.cell(rr + 8, 1, "TIR").font = Font(bold=True)
ws.cell(rr + 8, 2, f'=IFERROR(IRR(B{rr+4}:G{rr+4}),"No calculable")').number_format = PCT
ws.cell(rr + 9, 1, "Año de recupero (primer año con acumulado ≥ 0)").font = Font(bold=True)
ws.cell(rr + 9, 2, f'=IF(B{rr+2}=0,"Sin inversión cargada",IFERROR(INDEX(C{rr+1}:G{rr+1},MATCH(TRUE,INDEX(C{rr+5}:G{rr+5}>=0,0),0)),"> 5 años"))')
ws.column_dimensions["A"].width = 50; ws.column_dimensions["B"].width = 58
for c_ in "CDEFG": ws.column_dimensions[c_].width = 16

# 14-18
sheet("14_Datos_faltantes", ["ID", "Tema", "Dato faltante", "Por qué importa", "Cómo obtenerlo", "Criticidad"], FALTANTES, [6, 14, 50, 30, 42, 10])
sheet("15_Discrepancias", ["ID", "Tema", "Problema", "Origen", "Propuesta de resolución (sin alterar originales)", "Estado"], DISCREPANCIAS, [6, 26, 60, 26, 60, 14])
sheet("16_Implementacion", ["ID", "Etapa", "Tarea", "Responsable", "Plazo (REC)", "Entregable"], IMPLEMENTACION, [6, 10, 70, 24, 16, 26])
sheet("17_Competencia", ["Actor", "Oferta (EXTW)", "Relación con el proyecto (INF)", "Fuente"], COMPETENCIA, [40, 60, 40, 60],
      note="Relevamiento inicial por web; tarifas no publicadas. Completar con mystery shopping (D14).")
sheet("18_Fuentes", ["Tipo", "Fuente", "URL"], FUENTES, [10, 80, 90])
# 19 Relevamiento POI
ws = sheet("19_Relevamiento_POI", ["Código", "Punto", "Tipo", "Lat", "Lon", "Origen del dato", "Estado", "Qué relevar",
           "Lat relevada", "Lon relevada", "Fecha", "Fotos (archivos)", "¿Dentro del campo? (Sí/No/No sé)", "Sector (O/E de RP12)", "Acceso (4x4/4x2/a pie)", "Estado / riesgos", "Temporada observada", "Observaciones"],
           POI, [12, 36, 14, 11, 11, 30, 18, 40, 11, 11, 10, 18, 12, 10, 12, 26, 12, 30],
           note="Planilla para el relevamiento del titular. Columnas amarillas = completar en campo. Códigos ZONA-TIPO-NN (hoja 20). Los puntos con coordenada están en PDA_puntos_codificados_v1.gpx y en los GPX de cada jornada.")
for i in range(3, 3 + len(POI)):
    for j in range(9, 19):
        ws.cell(i, j).fill = INP; ws.cell(i, j).font = BLUE
dv = DataValidation(type="list", formula1='"Sí,No,No sé"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"M3:M{2+len(POI)}")
dv2 = DataValidation(type="list", formula1='"Oeste,Este,Sobre RP12"', allow_blank=True); ws.add_data_validation(dv2); dv2.add(f"N3:N{2+len(POI)}")
r = 4 + len(POI)
ws.cell(r, 1, "PROTOCOLO DE RELEVAMIENTO").font = Font(bold=True)
for k, (a, b) in enumerate(PROTOCOLO, r + 1):
    ws.cell(k, 1, a).font = Font(bold=True); c_ = ws.cell(k, 2, b); c_.alignment = WRAP
    ws.merge_cells(start_row=k, start_column=2, end_row=k, end_column=8); ws.row_dimensions[k].height = 30
r2 = r + len(PROTOCOLO) + 2
ws.cell(r2, 1, "RESPUESTAS DEL TITULAR (16/11/2026)").font = Font(bold=True)
for k, (a, b) in enumerate(TITULAR_V23, r2 + 1):
    ws.cell(k, 1, a).font = Font(bold=True); c_ = ws.cell(k, 2, b); c_.alignment = WRAP
    ws.merge_cells(start_row=k, start_column=2, end_row=k, end_column=8)

# 20 Codificación
rows = [("Formato", "ZONA-TIPO-NN", "O-BAS-01 = sector Oeste · Base · 01 (Base 1, Inicio)")]
rows += [("Zona " + z, n, d) for z, n, d in HR["zonas"]]
rows += [("Tipo " + t, d, "") for t, d in HR["tipos"]]
rows += [("Tramo", "PUNTO>PUNTO", "O-BAS-01>O-MIR-01"), ("Ruta de producto", "RUT-ZONA-NN (M si combina zonas)", "RUT-O-01; RUT-M-01"),
         ("Jornada de relevamiento", "REL-Dn-AAAAMMDD", "REL-D1-20261120"), ("Foto", "PUNTO_AAAAMMDD_N.jpg", "O-BAS-01_20261120_1.jpg"),
         ("Reglas", "Un código no se reutiliza; si un punto cambia de zona o de nombre recibe código nuevo y el anterior queda como alias. Bases conservan su número. Puntos P se recodifican al relevarlos.", "")]
sheet("20_Codificacion", ["Elemento", "Valor / significado", "Ejemplo / criterio"], rows, [22, 50, 60])
rows = []
for j in HR["jornadas"]:
    acum = 0.0; seen = set()
    rows.append((j["codigo"], 0, j["secuencia"][0], IDX_POI[j["secuencia"][0]][1], 0, 0, "Salida", j["titulo"]))
    for l in j["tramos"]:
        acum += l["km"]; c = l["a"]; first = c not in seen and c != j["secuencia"][0]; seen.add(c)
        rows.append((j["codigo"], len(seen) if first else None, c, IDX_POI[c][1], l["km"], round(acum, 2), IDX_POI[c][6] if first else "Paso / regreso", ""))
    for c in j["buscar"]:
        rows.append((j["codigo"], None, c, IDX_POI[c][1], None, None, "BUSCAR: " + IDX_POI[c][6], ""))
    rows.append((j["codigo"], None, "TOTAL", f"≈{j['km_total']} km · ≈{j['h_total']} h (conducción {j['h_conduccion']} h + puntos {j['h_puntos']} h)", None, None, j["notas"], ""))
sheet("21_Hoja_de_ruta", ["Jornada", "Nº", "Código", "Punto", "km tramo", "km acumulado", "Qué relevar", "Recorrido"], rows, [9, 5, 11, 40, 9, 10, 60, 30],
      note="Distancias por la red de las 24 trazas del titular. Tiempos = planificación (20 km/h; 15 min por punto; 30 min por punto a buscar). GPX por jornada: REL-D1 … REL-D5.")

wb.save(OUT)
print("ok", OUT)
