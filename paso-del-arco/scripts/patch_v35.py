# -*- coding: utf-8 -*-
"""v3.5: referencia USD 1.000 por persona y por día; la sociedad abarca solo las travesías; cada socio administra su complejo."""
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

run(D + "/build_modelo_v3.py", [
 ("r", '"Alojamiento incluido por persona (costo interno; solo T4+)"]', '"Alojamiento: pago al complejo que hospeda, por persona y noche (solo T4+; cada complejo factura su alojamiento)"]'),
 ("r", 'ws.cell(rb + 1, 3, "Unidad PEND: ¿por persona y día? ¿por programa?")', 'ws.cell(rb + 1, 3, "CONF titular: por persona y por día")'),
 ("r", '"Prestadores similares: USD 1.000 con guía de travesía, alojamiento, desayuno, almuerzo y cena"', '"Prestadores similares: USD 1.000 por persona y por día (guía de travesía, alojamiento, desayuno, almuerzo y cena)"'),
 ("r", '"Precio del T4+ frente a la referencia (si la unidad coincide)"', '"Precio del T4+ (por persona y día) frente a la referencia"'),
 ("l", 'ws.cell(1, 1, "Sociedad Tierras Mágicas – Milenka: comparten gastos y ganancias',
  'ws.cell(1, 1, "Sociedad Tierras Mágicas – Milenka: comparten gastos y ganancias DE LAS TRAVESÍAS; cada uno administra su complejo y factura su alojamiento (CONF titular). Porcentajes a definir y formalizar por escrito.").font = Font(bold=True)'),
 ("r", 'ws.cell(12, 1, "Asociados que se sumen después:', 'ws.cell(13, 1, "El alojamiento del programa todo incluido (T4+) NO entra en el reparto: la sociedad lo paga al complejo que hospeda (hoja 02, fila Alojamiento).").font = Font(italic=True)\nws.cell(12, 1, "Asociados que se sumen después:'),
 ("r", '"PASO DEL ARCO ADVENTURE — Modelo económico v3.4', '"PASO DEL ARCO ADVENTURE — Modelo económico v3.5'),
])
run(D + "/build_plan_v3.py", [
 ("r", '"Plan de Negocios v3.4 — Reformulado desde cero"', '"Plan de Negocios v3.5 — Reformulado desde cero"'),
 ("l", 'P("Versión 3.4 · 16/11/2026', 'P("Versión 3.5 · 16/11/2026 · Incorpora: ocupación de temporada Alta 80% en Tierras Mágicas y Milenka; grupos de 1 a 4 personas; referencia de mercado de USD 1.000 por persona y por día con guía, alojamiento y pensión completa; Tierras Mágicas y Milenka comparten gastos y ganancias de las travesías y cada uno administra su complejo. Corrige el techo de demanda de v3.1–3.3 (se calculaba por plazas y no por cabañas). Documento de trabajo para decisión del titular; reemplaza a las versiones 1 a 2.5.", i=True)'),
 ("l", 'B("Tierras Mágicas y Milenka comparten gastos y ganancias (CONF): la operación es un emprendimiento conjunto',
  'B("Tierras Mágicas y Milenka comparten gastos y ganancias DE LAS TRAVESÍAS (CONF): la operación de travesías es un emprendimiento conjunto de los dos complejos. Cada uno administra su complejo y su alojamiento por separado (CONF). En el programa todo incluido, la sociedad paga el alojamiento al complejo que hospeda y reparte solo el resultado de las travesías (hoja 07 del modelo). Los complejos que se sumen después participan por comisión, salvo nuevo acuerdo.", "Sociedad y cobro:")'),
 ("r", 'H("3.3 Sociedad Tierras Mágicas – Milenka (CONF: comparten gastos y ganancias)", 2)', 'H("3.3 Sociedad de travesías Tierras Mágicas – Milenka (CONF)", 2)'),
 ("l", 'B("Acordar por escrito: porcentajes de participación,',
  'B("Alcance: solo las travesías (CONF). Cada socio sigue administrando su complejo, sus reservas, su facturación y su alojamiento. Acordar por escrito: porcentajes de participación, aportes (gestión, vehículos, personal, uso del campo), cómo se reparten gastos e inversiones de las travesías, quién factura la travesía, cómo se decide y cómo se sale. Definir el precio que la sociedad paga a cada complejo por el alojamiento incluido en el programa todo incluido, y cómo se asigna el huésped de un programa a uno u otro complejo.", "Qué definir (REC):")'),
 ("l", '    ("T4", "Programa Todo Incluido', '    ("T4", "Programa Todo Incluido — travesía + alojamiento en Tierras Mágicas o Milenka + desayuno, almuerzo en el campo y cena; precio por persona y por día (1 a 3 días)", "Campo + zona", "1–3 días", "Grupos de 1–4, parejas y familias", "1–2"),'),
 ("l", 'P("Clave comercial (REC): T4 replica', 'P("Clave comercial (REC): T4 replica lo que ofrecen prestadores similares — guía de travesía, alojamiento, desayuno, almuerzo y cena — por una referencia de USD 1.000 por persona y por día (CONF titular). Como referencia de escala, un grupo de 2 personas durante 2 días equivale a 4 personas-día (≈USD 4.000 a precio de referencia). El alojamiento ya existe en los complejos: la sociedad lo paga al complejo que hospeda y suma guía, vehículo y comidas. Es el producto con más potencial de margen para la sociedad y, a la vez, aporta noches a cada complejo (HIP: confirmar con costos reales y con la tarifa interna de alojamiento).", b=True)'),
 ("r", '("Referencia de mercado", "USD 1.000 con guía, alojamiento y pensión completa (CONF titular; unidad PEND), convertida a pesos para comparar con el precio del programa todo incluido"),',
  '("Referencia de mercado", "USD 1.000 por persona y por día con guía, alojamiento y pensión completa (CONF titular), convertida a pesos para comparar con el precio del programa todo incluido"),'),
 ("l", 'B("Prestadores similares cobran ≈USD 1.000 con guía, alojamiento y pensión completa (CONF titular; unidad PEND).',
  'B("Prestadores similares cobran ≈USD 1.000 por persona y por día con guía, alojamiento y pensión completa (CONF titular). El modelo la convierte a pesos con el tipo de cambio que usa la configuración de TM (supuesto, actualizar) y compara el precio por persona y día del T4+ contra esa referencia. El alojamiento entra como costo: lo que la sociedad paga al complejo que hospeda.", "Referencia de precio:")'),
 ("r", '("Desacuerdos entre socios (TM–Milenka)", "Alto", "Acuerdo escrito con porcentajes, aportes, decisiones y salida"),',
  '("Desacuerdos entre socios (TM–Milenka) o conflicto entre la sociedad y el negocio de alojamiento de cada uno", "Alto", "Acuerdo escrito: alcance (solo travesías), porcentajes, tarifa interna de alojamiento, asignación de huéspedes, decisiones y salida"),'),
 ("l", '    ("Unidad de la referencia USD 1.000', '    ("Tarifa interna de alojamiento que la sociedad paga a cada complejo en el programa todo incluido", "Costo del T4", "Acuerdo entre socios (sobre el tarifario común)"),'),
 ("r", '"Plan_de_Negocios_Paso_del_Arco_v3_4.docx"', '"Plan_de_Negocios_Paso_del_Arco_v3_5.docx"'),
])
print("ok")
