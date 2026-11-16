# -*- coding: utf-8 -*-
"""v3.6: alojamiento interno según cuadro tarifario común; reparto 50/50 sin canon; no todos hacen travesía (sensibilidad)."""
import sys
D = sys.argv[1]
def run(path, ops):
    s = open(path).read()
    for kind, a, b in ops:
        if kind == "r":
            if a not in s: raise SystemExit(f"MISSING {path}: {a[:80]}")
            s = s.replace(a, b)
        else:
            L = s.split("\n"); idx = [i for i, l in enumerate(L) if a in l]
            if len(idx) != 1: raise SystemExit(f"line {len(idx)} {path}: {a[:60]}")
            L[idx[0]] = b; s = "\n".join(L)
    open(path, "w").write(s)

TARIFARIO = '''
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
'''
run(D + "/build_modelo_v3.py", [
 ("r", 'ws.column_dimensions["A"].width = 62; ws.column_dimensions["C"].width = 26', TARIFARIO + 'ws.column_dimensions["A"].width = 62; ws.column_dimensions["C"].width = 26'),
 ("r", '    ws.cell(i, 1, n); inp(ws.cell(i, 2), PCT); inp(ws.cell(i, 3))', '    ws.cell(i, 1, n); inp(ws.cell(i, 2), PCT, 0.5, conf=True); inp(ws.cell(i, 3))'),
 ("r", 'ws.cell(8, 1, "Canon o compensación por uso del campo (anual, si se acuerda)"); inp(ws.cell(8, 2), NUM)',
  'ws.cell(8, 1, "Canon o compensación por uso del campo (CONF: no hay canon)"); inp(ws.cell(8, 2), NUM, 0, conf=True)'),
 ("r", 'Porcentajes a definir y formalizar por escrito.").font = Font(bold=True)', 'Participación 50% / 50% y sin canon por el campo (CONF). Formalizar por escrito.").font = Font(bold=True)'),
 ("r", '"PASO DEL ARCO ADVENTURE — Modelo económico v3.5', '"PASO DEL ARCO ADVENTURE — Modelo económico v3.6'),
 ("r", 'WS01 = ws; PERS_CELL = (s0 + 2, 3)', '''sv = s0 + 7
ws.cell(sv, 1, "NO TODOS HACEN TRAVESÍA (CONF): sensibilidad a la tasa de compra, solo temporada Alta (cota CONF + 2,5 personas por reserva INF)").font = Font(bold=True)
hdr(ws, sv + 1, ["Tasa de compra", "", "Personas en travesía en Alta", "Grupos en travesía en Alta", "Personas-día (1 travesía de 1 día)"])
for k_, t in enumerate((0.1, 0.2, 0.3, 0.5), sv + 2):
    c_ = ws.cell(k_, 1, t); c_.number_format = PCT
    ws.cell(k_, 3, f"=C{e+7}*A{k_}").number_format = NUM
    ws.cell(k_, 4, f"=C{e+4}*A{k_}").number_format = NUM
    ws.cell(k_, 5, f"=C{k_}").number_format = NUM
ws.cell(sv + 6, 1, "Tasas ilustrativas, no estimaciones: la tasa real se mide con la preventa y el piloto. Fuera de la temporada Alta la demanda se suma cuando se carguen las otras ocupaciones.").font = Font(italic=True)
WS01 = ws; PERS_CELL = (s0 + 2, 3)'''),
])

run(D + "/build_plan_v3.py", [
 ("r", '"Plan de Negocios v3.5 — Reformulado desde cero"', '"Plan de Negocios v3.6 — Reformulado desde cero"'),
 ("l", 'P("Versión 3.5 · 16/11/2026', 'P("Versión 3.6 · 16/11/2026 · Incorpora: ocupación Alta 80%; grupos de 1 a 4; referencia USD 1.000 por persona y por día con pensión completa; sociedad de travesías Tierras Mágicas – Milenka al 50/50, sin canon por el campo, cada uno administra su complejo; alojamiento interno según el cuadro tarifario común; no todos los huéspedes hacen travesía. Corrige el techo de demanda de v3.1–3.3. Documento de trabajo para decisión del titular; reemplaza a las versiones 1 a 2.5.", i=True)'),
 ("r", 'H("3.3 Sociedad de travesías Tierras Mágicas – Milenka (CONF)", 2)', 'H("3.3 Sociedad de travesías Tierras Mágicas – Milenka: 50% / 50%, sin canon por el campo (CONF)", 2)'),
 ("l", 'B("Alcance: solo las travesías (CONF).',
  'B("Alcance: solo las travesías (CONF). Participación 50% / 50% y sin canon por el uso del campo (CONF). El alojamiento del programa todo incluido se paga a cada complejo según el cuadro tarifario común (CONF). Cada socio sigue administrando su complejo, sus reservas y su facturación. Falta acordar por escrito: aportes (gestión, vehículos, personal), quién factura la travesía, cómo se asigna el huésped de un programa a uno u otro complejo, cómo se decide y cómo se sale.", "Qué está definido y qué falta:")'),
 ("l", 'B("Si el campo no pertenece a la sociedad, fijar si su uso se compensa',
  'B("Su uso no se compensa con canon (CONF). Conviene dejar por escrito las condiciones de uso, el mantenimiento de huellas y bases, y la responsabilidad ante incidentes dentro del campo.", "El campo:")'),
 ("l", 'P("Lectura (INF): la temporada Alta, por sí sola,',
  'P("Lectura (INF): la temporada Alta da como máximo ≈138 grupos (≈340 personas). No todos hacen travesía (CONF): con una tasa de compra del 10% serían ≈34 personas en la temporada Alta; con 30%, ≈100; con 50%, ≈170 (tasas ilustrativas: la real se mide en la preventa). Con grupos chicos, una salida rentable necesita juntar varios grupos: por eso las salidas compartidas entre los dos complejos (CONF) son centrales, y la tasa de compra es el dato que decide el negocio.", i=True)'),
 ("l", 'B("Prestadores similares cobran ≈USD 1.000 por persona y por día',
  'B("Prestadores similares cobran ≈USD 1.000 por persona y por día con guía, alojamiento y pensión completa (CONF titular). El alojamiento interno sale del cuadro tarifario común (CONF): en Alta, la cabaña de 6 cuesta 210–260 mil pesos por noche; con descuento directo y 2,5 personas por reserva son ≈85 mil pesos por persona y noche (INF), alrededor del 5–6% de la referencia convertida al tipo de cambio que usa TM (supuesto). Lectura: casi todo el precio de referencia corresponde a guía, vehículo, comidas, gestión y margen. Validar que los huéspedes acepten ese nivel de precio (HIP).", "Referencia de precio y alojamiento:")'),
 ("l", 'B("La hoja 07 asigna el resultado', 'B("50% / 50% del resultado de las travesías y de la inversión de las Etapas 0–1; sin canon por el campo (CONF). La hoja 07 lo calcula.", "Reparto entre socios:")'),
 ("l", '    ("Tarifa interna de alojamiento que la sociedad paga', '    ("Tasa de compra: qué proporción de huéspedes hace travesía (no todos la hacen)", "Demanda — dato decisivo", "Preventa y encuesta en los dos complejos"),'),
 ("l", '    ("Porcentajes de participación y aportes de cada socio; forma jurídica"', '    ("Aportes de cada socio y forma jurídica (porcentajes 50/50 ya CONF)", "Sociedad", "Socios + contador + abogado"),'),
 ("r", '"Acordar con Milenka los porcentajes de participación, los aportes y la forma jurídica de la sociedad.",', '"Formalizar con Milenka la sociedad de travesías (50/50, sin canon): aportes, facturación, asignación de huéspedes, decisiones y salida.",'),
 ("r", '"Plan_de_Negocios_Paso_del_Arco_v3_5.docx"', '"Plan_de_Negocios_Paso_del_Arco_v3_6.docx"'),
])
print("ok")
