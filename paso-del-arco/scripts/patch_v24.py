# -*- coding: utf-8 -*-
import sys
D = sys.argv[1]
def ed(p, R):
    s = open(p).read()
    for a, b in R:
        if a not in s: raise SystemExit(f"MISSING {p}: {a[:70]}")
        s = s.replace(a, b)
    open(p, "w").write(s)
ed(D + "/build_xlsx.py", [
 ("from data_v23 import *", "from data_v24 import *"),
 ('Económico-Financiero v2.3", True)', 'Económico-Financiero v2.4", True)'),
 ('y relevamiento de puntos de interés (hoja 19).", True)', 'y relevamiento de puntos de interés (hoja 19). v2.4: codificación ZONA-TIPO-NN (hoja 20) y hoja de ruta por jornadas (hoja 21).", True)'),
 ('· 19_Relevamiento_POI ·', '· 19_Relevamiento_POI · 20_Codificacion · 21_Hoja_de_ruta ·'),
 ("Los puntos con coordenada están en PDA_POI_base_v1.gpx para navegar hasta ellos.", "Códigos ZONA-TIPO-NN (hoja 20). Los puntos con coordenada están en PDA_puntos_codificados_v1.gpx y en los GPX de cada jornada."),
])
# append sheets 20/21 after the POI sheet block (last lines of the 19 block)
s = open(D + "/build_xlsx.py").read()
anchor = "for k, (a, b) in enumerate(TITULAR_V23, r2 + 1):\n    ws.cell(k, 1, a).font = Font(bold=True); c_ = ws.cell(k, 2, b); c_.alignment = WRAP\n    ws.merge_cells(start_row=k, start_column=2, end_row=k, end_column=8)\n"
assert anchor in s
add = '''
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
'''
s = s.replace(anchor, anchor + add)
s = s.replace("from data_v24 import *", "from data_v24 import *\nIDX_POI = {p[0]: p for p in HR['poi']}")
open(D + "/build_xlsx.py", "w").write(s)
ed(D + "/build_docx.py", [
 ("from data_v23 import *", "from data_v24 import *"),
 ('"Plan de Negocios v2.3 —', '"Plan de Negocios v2.4 —'),
 ('P("Versión 2.3 · 16/11/2026', 'P("Versión 2.4 · 16/11/2026'),
 ("Paso_del_Arco_v2_3.xlsx", "Paso_del_Arco_v2_4.xlsx"),
 ('se entregan un GPX base (PDA_POI_base_v1.gpx, con los 24 puntos que ya tienen coordenada), la planilla 19 del libro (para completar en el campo) y este protocolo.")',
  'v2.4: los puntos usan la codificación ZONA-TIPO-NN (ej. O-BAS-01 Inicio, N-PAT-01 Aduana Vieja, L-LAG-01 Laguna Pilhue) y el relevamiento se organiza en 5 jornadas (REL-D1 a REL-D5). Ver el documento \'Hoja de Ruta del Relevamiento\', los GPX por jornada, la planilla 19 y las hojas 20–21 del libro.")'),
])
print("ok")
