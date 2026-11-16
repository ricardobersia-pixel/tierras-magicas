# -*- coding: utf-8 -*-
"""v3.8 / propuesta v1.2: la referencia es USD 1.000 por persona por TODA la travesía de 5 noches (≈USD 200 por persona y día)."""
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

REF = "USD 1.000 por persona por una travesía de 5 noches (≈USD 200 por persona y por día; los programas más cortos, proporcionales)"
run(D + "/build_plan_v3.py", [
 ("r", '"Plan de Negocios v3.7 — Reformulado desde cero"', '"Plan de Negocios v3.8 — Reformulado desde cero"'),
 ("l", 'P("Versión 3.7 · 16/11/2026', 'P("Versión 3.8 · 16/11/2026 · CORRIGE la referencia de mercado: USD 1.000 por persona por TODA una travesía de 5 noches (≈USD 200 por persona y por día; los programas más cortos, proporcionales). Incorpora además: ocupación Alta 80%; grupos de 1 a 4; sociedad de travesías Tierras Mágicas – Milenka al 50/50, sin canon por el campo, cada uno administra su complejo; alojamiento interno según el cuadro tarifario común; no todos los huéspedes hacen travesía. Corrige el techo de demanda de v3.1–3.3. Documento de trabajo para decisión del titular; reemplaza a las versiones 1 a 2.5.", i=True)'),
 ("l", 'P("Clave comercial (REC): T4 replica',
  'P("Clave comercial (REC): T4 replica lo que ofrecen prestadores similares — guía de travesía, alojamiento, desayuno, almuerzo y cena — por una referencia de ' + REF + ' (CONF titular). El alojamiento ya existe en los complejos: la sociedad lo paga al complejo que hospeda según el tarifario. Con ese nivel de precio el margen depende de compartir vehículo y guía entre varios grupos (ver §12). A la vez, el programa aporta noches a cada complejo (HIP: confirmar con costos reales).", b=True)'),
 ("r", '("Referencia de mercado", "USD 1.000 por persona y por día (referencia de una travesía de 5 noches; los programas más cortos, proporcionales) con guía, alojamiento y pensión completa (CONF titular),',
  '("Referencia de mercado", "' + REF + ', con guía, alojamiento y pensión completa (CONF titular),'),
 ("l", 'B("Prestadores similares cobran ≈USD 1.000 por persona y por día',
  'B("Prestadores similares: ' + REF + ', con guía, alojamiento y pensión completa (CONF titular). Al tipo de cambio que usa TM (1.525, supuesto), ≈305 mil pesos por persona y por día. El alojamiento interno sale del cuadro tarifario común (CONF): en Alta, ≈85 mil pesos por persona y noche (cabaña de 6 con descuento directo ÷ 2,5 personas, INF), ≈28% de la referencia. Por grupo de 2,5 personas y por día: ≈USD 500 de referencia, ≈USD 139 de alojamiento y ≈USD 361 para guía, vehículo (≈90 km), 7–8 comidas, seguro, gestión y margen (INF). Lectura: si cada grupo sale solo, el margen es estrecho; con 2–3 grupos por vehículo y guía (salidas compartidas, CONF) el costo de guía y vehículo se reparte. Validar con costos reales (HIP).", "Referencia de precio y alojamiento:")'),
 ("r", '"Plan_de_Negocios_Paso_del_Arco_v3_7.docx"', '"Plan_de_Negocios_Paso_del_Arco_v3_8.docx"'),
])
run(D + "/build_modelo_v3.py", [
 ("r", 'ws.cell(rb + 1, 1, "Prestadores similares: USD 1.000 por persona y por día (guía de travesía, alojamiento, desayuno, almuerzo y cena)"); inp(ws.cell(rb + 1, 2), NUM, 1000, conf=True)',
  'ws.cell(rb + 1, 1, "Prestadores similares: USD por persona por TODA una travesía de 5 noches (guía, alojamiento, desayuno, almuerzo y cena)"); inp(ws.cell(rb + 1, 2), NUM, 1000, conf=True)'),
 ("r", 'ws.cell(rb + 1, 3, "CONF titular: por persona y por día; referencia de una travesía de 5 noches (USD 5.000); los programas más cortos, proporcionales")',
  'ws.cell(rb + 1, 3, "CONF titular: USD 1.000 por persona por la travesía de 5 noches (≈USD 200 por persona y día); los programas más cortos, proporcionales")'),
 ("r", 'ws.cell(rb + 3, 1, "Referencia en pesos"); ws.cell(rb + 3, 2, f"=B{rb+1}*B{rb+2}").number_format = NUM',
  'ws.cell(rb + 3, 1, "Referencia por persona y por día en pesos (USD ÷ 5 días × tipo de cambio)"); ws.cell(rb + 3, 2, f"=B{rb+1}/5*B{rb+2}").number_format = NUM'),
 ("r", '"PASO DEL ARCO ADVENTURE — Modelo económico v3.6', '"PASO DEL ARCO ADVENTURE — Modelo económico v3.8'),
])
run(D + "/propuesta_travesias.py", [
 ("r", '("Referencia de mercado", "Prestadores similares: travesía de 5 noches a USD 1.000 por persona y por día (USD 5.000), con guía, alojamiento, desayuno, almuerzo y cena (CONF titular). Los planes más cortos, proporcionales."),',
  '("Referencia de mercado", "Prestadores similares: USD 1.000 por persona por una travesía de 5 noches (≈USD 200 por persona y por día), con guía, alojamiento, desayuno, almuerzo y cena (CONF titular). Los planes más cortos, proporcionales."),'),
 ("r", 'f"USD {1000*nd:,}".replace(",", ".") + (" (referencia: 5 noches = USD 5.000)" if nd == 5 else " (proporcional al de 5 noches)")',
  'f"USD {200*nd:,}".replace(",", ".") + (" (referencia de 5 noches)" if nd == 5 else " (proporcional al de 5 noches)")'),
 ("l", 'Pp("La referencia (CONF titular) es la de prestadores similares para una travesía de 5 noches:',
  'Pp("La referencia (CONF titular) es la de prestadores similares: USD 1.000 por persona por una travesía de 5 noches, ≈USD 200 por persona y por día; los planes de 1 y 3 días se calculan en proporción (USD 200 y USD 600). NO es un precio propio: incluye alojamiento y pensión completa. El alojamiento según el cuadro tarifario común es ≈85 mil pesos por persona y noche en temporada Alta (INF), ≈28% de la referencia diaria al tipo de cambio que usa TM (supuesto). El resto debe cubrir guía, vehículo, comidas, seguro, gestión y margen: compartir vehículo y guía entre varios grupos es decisivo.", i=True)'),
 ("r", '"PEND (con costos; referencia USD 1.000 por persona y día)"', '"PEND (con costos; referencia USD 1.000 por persona por 5 noches ≈ USD 200 por día)"'),
 ("r", 'Pp("Versión 1.1 · 16/11/2026', 'Pp("Versión 1.2 · 16/11/2026'),
 ("r", '"Propuesta_Travesias_Paso_del_Arco_v1_1.docx"', '"Propuesta_Travesias_Paso_del_Arco_v1_2.docx"'),
])
print("ok")
