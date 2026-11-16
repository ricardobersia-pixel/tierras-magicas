# -*- coding: utf-8 -*-
"""v3.4: ocupación Alta 80%, grupos 1–4, referencia de mercado USD 1.000 todo incluido, sociedad TM–Milenka."""
import sys
D = sys.argv[1]; P = D + "/build_plan_v3.py"
s = open(P).read()
def rep(a, b):
    global s
    if a not in s: raise SystemExit("MISSING: " + a[:90])
    s = s.replace(a, b)
def rep_line(contains, new):
    global s
    L = s.split("\n"); idx = [i for i, l in enumerate(L) if contains in l]
    if len(idx) != 1: raise SystemExit(f"line match {len(idx)}: {contains[:60]}")
    L[idx[0]] = new; s = "\n".join(L)

rep('"Plan de Negocios v3.3 — Reformulado desde cero"', '"Plan de Negocios v3.4 — Reformulado desde cero"')
rep_line('P("Versión 3.3 · 16/11/2026', 'P("Versión 3.4 · 16/11/2026 · Incorpora: ocupación de temporada Alta 80% en Tierras Mágicas y Milenka; grupos de 1 a 4 personas; referencia de mercado de USD 1.000 con guía, alojamiento y pensión completa; Tierras Mágicas y Milenka comparten gastos y ganancias. Corrige el techo de demanda de v3.1–3.3 (se calculaba por plazas y no por cabañas). Documento de trabajo para decisión del titular; reemplaza a las versiones 1 a 2.5.", i=True)')
rep_line('B("Los dos primeros asociados están juntos en Moquehue:',
 'B("Tierras Mágicas (3 cabañas + dormi) y Milenka (3 cabañas), contiguos en Moquehue, suman 6 cabañas (CONF). Cada reserva es un grupo de 1 a 4 personas (CONF), así que la demanda se cuenta por cabañas ocupadas, no por plazas. En temporada Alta la ocupación llega al 80% en ambos (CONF). Con los 86 días de Alta del calendario 2026 de TM y la estadía mínima de 3 noches, son como máximo ≈138 reservas en Alta, es decir entre ≈140 y ≈550 personas (≈340 con 2,5 por grupo, INF). En todo el año, aun con 100% de ocupación y estadías de 2 noches, el techo es de ≈1.100 reservas. CORRECCIÓN: el techo de ≈6.200 huéspedes de la v3.1–3.3 suponía todas las plazas llenas y estaba sobrestimado.", "Escala de la demanda cautiva (CONF + INF):")')
rep_line('B("El huésped paga la travesía (directo o a través del complejo);',
 'B("Tierras Mágicas y Milenka comparten gastos y ganancias (CONF): la operación es un emprendimiento conjunto de los dos complejos, no un proveedor que les paga comisión. Ingresos y costos son comunes y el resultado se reparte según porcentajes a acordar (hoja 07 del modelo). Los complejos que se sumen después participan por comisión, salvo nuevo acuerdo.", "Sociedad y cobro:")')
rep('H("3.3 Fuentes de ingreso", 2)', '''H("3.3 Sociedad Tierras Mágicas – Milenka (CONF: comparten gastos y ganancias)", 2)
B("Acordar por escrito: porcentajes de participación, aportes de cada socio (gestión, vehículos, personal, uso del campo), cómo se reparten gastos e inversiones, quién factura, cómo se decide y cómo se sale de la sociedad.", "Qué definir (REC):")
B("Elegir con un contador y un abogado la figura adecuada en Argentina (un contrato asociativo o una sociedad), considerando facturación, seguros y responsabilidad frente a los pasajeros. La habilitación como prestador y el seguro deben estar a nombre de quien opere.", "Forma jurídica (PEND):")
B("Si el campo no pertenece a la sociedad, fijar si su uso se compensa con un canon o como aporte (hoja 07).", "El campo:")
H("3.4 Fuentes de ingreso", 2)''')
rep('H("3.4 Alternativas de operación", 2)', 'H("3.5 Alternativas de operación", 2)')
rep('P("Personas en travesía por año = Σ complejos (plazas × 365 × ocupación ÷ estadía media × tasa de compra × travesías por estadía)", b=True)',
    'P("Reservas por año = cabañas × Σ temporadas (días × ocupación) ÷ estadía media · Personas = reservas × personas por reserva · Personas en travesía = personas × tasa de compra × travesías por estadía", b=True)')
i = s.index('T(["Variable", "Tierras Mágicas", "Milenka", "Fuente"], ['); j = s.index('], [3.5, 5.2, 2.6, 5.7])', i) + len('], [3.5, 5.2, 2.6, 5.7])')
s = s[:i] + '''T(["Variable", "Tierras Mágicas", "Milenka", "Fuente"], [
    ("Cabañas", "3 (+ dormi que amplía una reserva)", "3", "CONF"),
    ("Personas por reserva", "1 a 4 (CONF); 2,5 en el modelo (INF, punto medio)", "Igual", "Titular"),
    ("Ocupación temporada Alta (86 días en 2026)", "80% (CONF)", "80% (CONF)", "Titular · calendario de TM"),
    ("Ocupación Alta Premium (54 d), Media (100 d), Baja (125 d)", "PEND", "Igual a TM", "Panel de TM"),
    ("Estadía mínima", "3 noches en Alta y Premium, 2 en Media y Baja, 5 en Fin de año (CONF)", "Igual (mismas políticas)", "Políticas de TM"),
    ("Estadía media real", "PEND", "Igual a TM", "Panel de TM"),
    ("Tasa de compra y travesías por estadía", "HIP — se miden en la preventa y el piloto", "HIP", "Preventa"),
], [4.6, 5.6, 2.8, 4])''' + s[j:]
rep_line('P("Techo conjunto de Tierras Mágicas + Milenka (INF)',
 'P("Lectura (INF): la temporada Alta, por sí sola, da como máximo ≈138 grupos de 1 a 4 personas. Con grupos chicos, una salida rentable necesita juntar varios grupos: por eso las salidas compartidas entre los dos complejos (CONF) son centrales. Están a ≈40 m, comparten punto de salida, tarifas y políticas; el paquete puede tener un solo precio y una sola política para los dos.", i=True)')
rep_line('("T4", "Paquete Estadía + Travesías',
 '    ("T4", "Programa Todo Incluido — travesía + alojamiento en Tierras Mágicas o Milenka + desayuno, almuerzo en el campo y cena (1 a 3 días)", "Campo + zona", "1–3 días", "Grupos de 1–4, parejas y familias", "1–2"),')
rep_line('P("Clave comercial (REC): el producto que mejor encaja',
 'P("Clave comercial (REC): T4 replica lo que ofrecen prestadores similares — guía de travesía, alojamiento, desayuno, almuerzo y cena — por una referencia de USD 1.000 (CONF titular; falta saber si es por persona, por día o por programa). La sociedad ya tiene el alojamiento: el costo adicional de T4 es guía, vehículo y comidas, y el ingreso suma estadía y travesía. Es el producto con más potencial de margen (HIP: confirmar con costos reales y con la unidad de la referencia).", b=True)')
rep_line('B("Con un traslado de ≈70 km por salida y grupos chicos,',
 'B("Con un traslado de ≈70 km por salida y grupos de 1 a 4 personas, el traslado y las horas de guía dominan el costo variable (INF). Palancas: salidas compartidas entre los dos complejos, encuentro en la Tranquera 1 fuera del invierno y el programa todo incluido T4.", "Lectura:")\nB("Prestadores similares cobran ≈USD 1.000 con guía, alojamiento y pensión completa (CONF titular; unidad PEND). El modelo la convierte a pesos con el tipo de cambio que usa la configuración de TM (supuesto, actualizar) y compara el precio del T4+ contra esa referencia.", "Referencia de precio:")\nB("La hoja 07 asigna el resultado y la inversión de las Etapas 0–1 a cada socio según los porcentajes que acuerden; descuenta un canon por el uso del campo si se pacta.", "Reparto entre socios:")')
rep('("Demanda cautiva insuficiente (TM + Milenka = 34 plazas)", "Crítico",', '("Demanda cautiva acotada (6 cabañas; ≈138 grupos en temporada Alta)", "Crítico",')
rep('    ("Binacional (futuro)", "Alto", "Solo con requisitos escritos y socio chileno"),',
    '    ("Desacuerdos entre socios (TM–Milenka)", "Alto", "Acuerdo escrito con porcentajes, aportes, decisiones y salida"),\n    ("Binacional (futuro)", "Alto", "Solo con requisitos escritos y socio chileno"),')
rep('("Condiciones del acuerdo con Milenka: comisión o paquete", "Acuerdo", "Titular"),',
    '("Porcentajes de participación y aportes de cada socio; forma jurídica", "Sociedad", "Socios + contador + abogado"),\n    ("Unidad de la referencia USD 1.000 (¿por persona y día? ¿por programa?) y qué días/noches incluye", "Precio", "Titular"),\n    ("Ocupación de Alta Premium, Media y Baja", "Demanda anual", "Panel de TM"),')
rep('"Acordar con Milenka las condiciones (comisión o paquete) y definir la lista de complejos a invitar después.",',
    '"Acordar con Milenka los porcentajes de participación, los aportes y la forma jurídica de la sociedad.",\n    "Definir la lista de complejos a invitar después (por comisión).",')
rep('("Ocupación anual y estadía media de Tierras Mágicas (valen también para Milenka)", "Demanda", "Panel de TM: Finanzas / Estadísticas"),',
    '("Estadía media real de Tierras Mágicas (vale también para Milenka)", "Demanda", "Panel de TM: Estadísticas"),')
rep('"Plan_de_Negocios_Paso_del_Arco_v3_3.docx"', '"Plan_de_Negocios_Paso_del_Arco_v3_4.docx"')
open(P, "w").write(s); print("ok")
