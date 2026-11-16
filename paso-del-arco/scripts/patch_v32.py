# -*- coding: utf-8 -*-
"""v3.2: coordenada de Milenka y tarifario/políticas comunes con Tierras Mágicas."""
import sys
D = sys.argv[1]
def ed(p, R):
    s = open(p).read()
    for a, b in R:
        if a not in s: raise SystemExit(f"MISSING {p}: {a[:80]}")
        s = s.replace(a, b)
    open(p, "w").write(s)
ed(D + "/hoja_ruta.py", [
 ('("AMO-ALO-02", "Milenka (complejo contiguo a Tierras Mágicas)", None, None, "—", "CONF titular (sin coordenada)", "Marcar su entrada; punto de encuentro común con TM")',
  '("AMO-ALO-02", "Milenka (complejo contiguo a Tierras Mágicas)", -38.900986, -71.291336, "—", "CONF titular", "Entrada; punto de encuentro común con TM (≈40 m)")'),
 ('  ["AMO-ALO-01", "R-ACC-01", "R-MIR-01", "O-TRQ-01", "O-BAS-01", "AMO-ALO-01"],\n  ["AMO-ALO-02"],',
  '  ["AMO-ALO-01", "AMO-ALO-02", "R-ACC-01", "R-MIR-01", "O-TRQ-01", "O-BAS-01", "AMO-ALO-01"],\n  [],'),
])
ed(D + "/build_modelo_v3.py", [
 ('"CONF titular: contiguo a Tierras Mágicas, 3 cabañas de 6 plazas. Primer asociado junto con TM."',
  '"CONF titular: -38.900986, -71.291336 (≈40 m de TM); 3 cabañas de 6 plazas; mismos cuadros tarifarios y políticas que TM (estadía mínima 2–3 noches). Primer asociado junto con TM."'),
 ('("PASO DEL ARCO ADVENTURE — Modelo económico v3.1 (demanda desde complejos)", True),', '("PASO DEL ARCO ADVENTURE — Modelo económico v3.2 (demanda desde complejos)", True),'),
])
ed(D + "/build_plan_v3.py", [
 ('"Plan de Negocios v3.1 — Reformulado desde cero"', '"Plan de Negocios v3.2 — Reformulado desde cero"'),
 ('P("Versión 3.1 · 16/11/2026 (incorpora a Milenka: contiguo a Tierras Mágicas, 3 cabañas de 6 plazas; ambos son los primeros asociados)',
  'P("Versión 3.2 · 16/11/2026 (Milenka: -38.900986, -71.291336, a ≈40 m de Tierras Mágicas, 3 cabañas de 6 plazas, mismos cuadros tarifarios y políticas; ambos son los primeros asociados)'),
 ('"PEND (política de estadía mínima también)"', '"≥ 2–3 noches: mismas políticas que TM (CONF); media real PEND"'),
 ('("Milenka: ocupación, estadía media, condiciones del acuerdo y coordenada (plazas y ubicación ya CONF)"',
  '("Milenka: ocupación y estadía media reales, condiciones del acuerdo (plazas, coordenada, tarifas y políticas ya CONF)"'),
 ('Ventaja operativa: al estar contiguos, comparten un único punto de salida y se pueden juntar huéspedes de ambos en la misma salida.',
  'Ventajas: están a ≈40 m (Milenka -38.900986, -71.291336, CONF), comparten un único punto de salida y se pueden juntar huéspedes de ambos en la misma salida; y como tienen los mismos cuadros tarifarios y políticas (CONF), el paquete “estadía + travesías” puede tener un solo precio y una sola política para los dos.'),
 ('B("Paquete \'Estadía + Travesías\' (T4) para estadías de 3+ noches; incentivo para temporada media y baja.", "3. Paquete:")',
  'B("Paquete \'Estadía + Travesías\' (T4) para estadías de 3+ noches; incentivo para temporada media y baja. Tierras Mágicas y Milenka comparten cuadros tarifarios y políticas (CONF): el paquete se arma sobre ese tarifario común (mismas temporadas, estadías mínimas, seña y cancelación) y la travesía se suma con su propia política de clima.", "3. Paquete:")'),
 ('"Plan_de_Negocios_Paso_del_Arco_v3_1.docx"', '"Plan_de_Negocios_Paso_del_Arco_v3_2.docx"'),
 ('ax.annotate("+ MILENKA (contiguo)", (TM[1], TM[0])', 'ax.plot(-71.291336, -38.900986, "*", ms=12, color="#d4a017", mec="k", zorder=6); ax.annotate("+ MILENKA (≈40 m)", (TM[1], TM[0])'),
])
print("ok")
