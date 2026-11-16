# -*- coding: utf-8 -*-
import sys
D = sys.argv[1]
def ed(p, R, strict=True):
    s = open(p).read()
    for a, b in R:
        if a not in s:
            if strict: raise SystemExit(f"MISSING in {p}: {a[:70]}")
            print("skip", a[:60]); continue
        s = s.replace(a, b)
    open(p, "w").write(s)

ed(D + "/build_xlsx.py", [
 ("from data_v21 import *", "from data_v23 import *"),
 ('Económico-Financiero v2.2", True)', 'Económico-Financiero v2.3", True)'),
 ('y corrección de la estimación de v2.1.", True)', 'y corrección de la estimación de v2.1. v2.3: RP12 pública que divide el campo (sectores O/E), Tranquera 1, km de cada traza sobre la RP12 (02b) y relevamiento de puntos de interés (hoja 19).", True)'),
 ('"Inicio–fin (km)", "Mín. a Inicio (km)",', '"Inicio–fin (km)", "km sobre RP12 (acceso–Cruce N)", "% sobre RP12", "Mín. a Inicio (km)",'),
 ('g["gain_m"], g["start_end_km"], g["near"]["Inicio"]["km"]', 'g["gain_m"], g["start_end_km"], RP12_TRACK[c[1]]["km_sobre_RP12"], RP12_TRACK[c[1]]["pct_sobre_RP12"], g["near"]["Inicio"]["km"]'),
 ('[11, 30, 30, 18, 8, 9, 9, 8, 16, 11, 14, 9, 10, 9, 8, 8, 8, 8, 8, 8, 8, 8, 9, 8, 50]', '[11, 30, 30, 18, 8, 9, 9, 8, 16, 11, 14, 9, 10, 9, 8, 8, 8, 8, 9, 8, 8, 8, 8, 8, 9, 8, 50]'),
 ('"01_Bases · 02_Circuitos_24 · 02b_Auditoria_GPX · 02c_Waypoints_53 ·', '"01_Bases · 02_Circuitos_24 · 02b_Auditoria_GPX · 02c_Waypoints_53 · 19_Relevamiento_POI ·'),
 ('sheet("18_Fuentes", ["Tipo", "Fuente", "URL"], FUENTES, [10, 80, 90])', '''sheet("18_Fuentes", ["Tipo", "Fuente", "URL"], FUENTES, [10, 80, 90])
# 19 Relevamiento POI
ws = sheet("19_Relevamiento_POI", ["Código", "Punto", "Tipo", "Lat", "Lon", "Origen del dato", "Estado", "Qué relevar",
           "Lat relevada", "Lon relevada", "Fecha", "Fotos (archivos)", "¿Dentro del campo? (Sí/No/No sé)", "Sector (O/E de RP12)", "Acceso (4x4/4x2/a pie)", "Estado / riesgos", "Temporada observada", "Observaciones"],
           POI, [12, 36, 14, 11, 11, 30, 18, 40, 11, 11, 10, 18, 12, 10, 12, 26, 12, 30],
           note="Planilla para el relevamiento del titular. Columnas amarillas = completar en campo. Los puntos con coordenada están en PDA_POI_base_v1.gpx para navegar hasta ellos.")
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
    ws.merge_cells(start_row=k, start_column=2, end_row=k, end_column=8)'''),
])

ed(D + "/build_docx.py", [
 ("from data_v21 import *", "from data_v23 import *"),
 ('"Plan de Negocios v2.2 —', '"Plan de Negocios v2.3 —'),
 ('P("Versión 2.2 · 15/11/2026', 'P("Versión 2.3 · 16/11/2026'),
 ("Paso_del_Arco_v2_2.xlsx", "Paso_del_Arco_v2_3.xlsx"),
 ('B("Inicio es la primera base desde el acceso:', '''B("RP12 pública en todo su recorrido; el campo queda dividido por ella, entre el Cerro Piñihue y la costa del Arroyo del Arco (referencias, no límites catastrales). Sector OESTE: Inicio, Chivero, Tranquera 1 (-38.832922, -71.058162) y el ramal hacia el Punto límite campo. Sector ESTE: Vaquero y, probablemente, el cruce de río que podría ser el Arroyo del Arco (HIP). Hasta la Tranquera 1: solo 4x4 en invierno; vehículo de calle no bajo el resto del año.", "Respuestas del titular (CONF, 16/11):")
B("(1) Fuera del invierno, el cliente puede llegar por su cuenta hasta Inicio: los productos de base (P01, P02, P04–P06) no necesitan traslado. (2) En invierno, la llegada exige 4x4: traslado con prestador habilitado o producto solo para clientes con 4x4. (3) Todo circuito que una el sector oeste con Vaquero cruza la RP12: hacen falta puntos de cruce fijos, señalización y un protocolo para el convoy. (4) XVilla Unión Corto va un 69% por la RP12: deja de ser un circuito propio. XX Circuito campo va solo un 14% por la ruta (≈20 km por huellas propias) y se confirma como circuito insignia.", "Implicancias (INF/REC):")
B("Inicio es la primera base desde el acceso:'''),
 ('H("5. Priorización', '''H("4 ter. Relevamiento de puntos de interés con fotos (v2.3)")
P("El titular grabó las 24 trazas y planea una traza con todos los puntos de interés y fotografías. Para que sirva al plan, se entregan un GPX base (PDA_POI_base_v1.gpx, con los 24 puntos que ya tienen coordenada), la planilla 19 del libro (para completar en el campo) y este protocolo.")
T(["Paso", "Instrucción"], PROTOCOLO, [3, 14], size=7.5)
T(["Código", "Punto", "Tipo", "Coordenada", "Origen", "Qué relevar"],
  [(p[0], p[1], p[2], "PEND" if p[3] is None else f"{p[3]:.6f}, {p[4]:.6f}", p[5], p[7]) for p in POI], [2.2, 5, 2.2, 3.6, 4.5, 6], size=7)
P("Este relevamiento resuelve, sin costo, cinco datos faltantes: los límites de referencia (D29), las lagunas norte y el mirador de las antenas (D30), si Pilhue, la Aduana Vieja y el Castillo son internos (D26), los cruces de la RP12 (D31) y el camino a Chivero. Con él se arman las fichas de producto y el material visual propio.", b=True)

H("5. Priorización'''),
 ('B("Indicar dónde está la tranquera de ingreso al campo sobre la RP12 y si el camino es apto para 4x2 todo el año; confirmar si', 'B("Hacer el relevamiento de puntos de interés con el GPX base y la planilla 19; en él, determinar si'),
 ('014, 016, 017, 018, 020: traslados, trazas redundantes o destinos de terceros.", "Ola 4:")', '014, 016, 017, 018, 020: traslados, trazas redundantes o destinos de terceros. v2.3: 019 pasa a Ola 2 (69% sobre la RP12 pública).", "Ola 4:")'),
])

ed(D + "/gpx_map.py", [
 ('    ax.plot(-71.05745, -38.810607, "D"', '    ax.plot(-71.058162, -38.832922, "P", ms=10, color="#7a3e00", zorder=7); ax.annotate("Tranquera 1 (CONF)", (-71.058162, -38.832922), fontsize=7.5, xytext=(6, -10), textcoords="offset points", color="#7a3e00")\n    ax.plot(-71.05745, -38.810607, "D"'),
 ('" (traza tipo ruta, posible RP13)" if "Zapala" in n else ""', '" (traza tipo ruta; RP13 en el acceso)" if "Zapala" in n else (" (69% sobre RP12 pública)" if "Corto" in n else "")'),
])
print("patched")
