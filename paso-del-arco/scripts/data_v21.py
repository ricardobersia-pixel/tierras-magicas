# -*- coding: utf-8 -*-
"""v2.1: incorpora la auditoría de los 24 GPX (RutasWKLC.zip) y el acceso RP13/RP12 informado por el titular.
No altera data.py (v2): aplica correcciones trazables."""
import json, os
from data import *
import data as _v2

M = json.load(open(os.environ["GPX_METRICS"]))
GPX = {t["name"]: t for t in M["tracks"]}
GPX_PARAMS = M["params"]
RED_UNICA_KM = 457  # aprox., método de grilla ~50 m (ver gpx_analyze.py)

NET = json.load(open(os.environ["ACCESO_RED"]))
_D = NET["destinos"]
ACCESO = {
    "nombre": "Intersección RP13 / RP12 — Paso del Arco",
    "dato_titular": "CONF: punto de acceso hacia la base = intersección RP13/RP12 (Paso del Arco): -38.902440, -71.064667 (coordenada aportada por el titular).",
    "lat": -38.902440, "lon": -71.064667,
    "metodo": "EXT/INF: 12 de los 24 GPX pasan por el punto. Salen tres ramas: NO y SE (camino pasante usado por las trazas 015 y 001 → RP13, INF) y NE (hacia las bases → RP12 por descarte, INF a confirmar). Distancias por red = camino más corto sobre el grafo de las 24 trazas (celdas de ~20 m; puede sobreestimar ~1–3%).",
    "dist": [(n, _D[n]["linea_recta_km"], (f"≈{_D[n]['por_red_km']:.1f}".replace('.', ',') + " km por trazas")) for n in
             ["Vista del Aluminé (wpt)", "Tranquera (013)", "Inicio", "Cruce N (traza 015 / eje N–S)", "Vaquero", "Chivero", "Litrán RP13/RP23", "Aduana Vieja (wpt)", "Laguna Pilhue (wpt)", "Punto límite campo (wpt)"]],
    "elev": f"≈{NET['ele_acceso']} m (mediana de los GPX, excluido 024). Inicio ≈{_D['Inicio']['alt_mediana_m']} m (+{_D['Inicio']['alt_mediana_m']-NET['ele_acceso']} m); Vaquero ≈{_D['Vaquero']['alt_mediana_m']} m.",
}

# ---------- Correcciones por circuito (cat, cat_alt, justificación, usos, inspección, riesgos, faltante, ola, scores) ----------
OV = {
 "PDA-EX-001": (5, None, "GPX: 23,99 km registrados el 24/03/2026 en 0,52 h en movimiento (~46 km/h: ritmo de ruta). 92,5% superpuesto con la traza tipo ruta 015; 1,6% dentro del radio proxy de 3 km de las bases. Es un tramo de ruta hacia Villa Pehuenia.",
                "Traslado de clientes; no producto.", "Solo gabinete.", "Vía pública.", "Jurisdicción del camino.", "Ola 4", (1, 4, 1, 1, 2)),
 "PDA-EX-002": (5, None, "GPX: comienza ≈9 km al NO (-38.731, -71.138) y termina sobre el eje N–S cerca de la Tranquera de Inicio. 93% superpuesto con 016 y 018; ~33 km/h en movimiento. La 'proximidad a Chivero' (425 m) corresponde al camino, no a la base. Es una traza de aproximación desde el norte, NO un circuito corto (corrige v1/v2).",
                "Ruta de llegada desde el norte.", "Gabinete: ¿camino público?", "Vía pública/terceros.", "Titularidad del tramo.", "Ola 4", (2, 3, 2, 1, 3)),
 "PDA-EX-003": (4, 1, "GPX (registro 05/02/2024, el más antiguo): 72,50 km con 4 saltos (8,5 y 2,3 km en línea recta) → ≈61,7 km netos. 47% dentro del radio proxy. Waypoints decisivos: 'Quincho' = Base Inicio (6 m); 'Cima' a 0,75 km y 'CP' a 0,19 km de Chivero; 'Aduana Vieja' 1,8 km al N de Chivero; 'Castillo' coincide con 'Grupo el Arco' (024); 'Punto límite campo' 3,55 km al O de Inicio. Contiene el ramal oeste Chivero→Punto límite campo: mejor candidato a circuito interno 'alto'.",
                "Derivar 2 circuitos internos: (a) ramal oeste hacia Punto límite campo; (b) bucle norte Cima–Aduana Vieja–Castillo.", "Campo Ola 1 en los segmentos internos; gabinete para el resto.", "Exposición en altura; zona límite; tramos externos.", "Recálculo por segmento; qué es 'CP'.", "Ola 1 (segmentos internos)", (4, 3, 5, 5, 4)),
 "PDA-EX-004": (4, None, "GPX (31/10–01/11/2026, el más reciente, primavera): 9,25 h transcurridas y 2,44 h en movimiento (muchas paradas); bucle regional desde el oeste (-38.889, -71.278) que pasa por Inicio (1 m) y Vaquero (1 m); 30% dentro del radio proxy; 84% superpuesto con 021. Waypoint 'Río' = cruce de río sobre la traza 015, 1,7 km al E de Vaquero (mismo punto que Puente/Vado de 013).",
                "Travesía regional que integra las bases; fuente de tiempos de parada reales.", "Gabinete: separar tramos; campo Ola 2.", "Cruce de río (deshielo).", "Identificar el río (¿Arroyo del Arco?).", "Ola 2", (3, 1, 3, 3, 3)),
 "PDA-EX-005": (4, 5, "GPX (19/04/2026): de Villa Pehuenia (-38.879, -71.175) al sur del campo; pasa por Inicio (0 m) y Vaquero (14 m); 87% superpuesto con 021 y 71% con 012. Redundante.",
                "Sin uso propio (redundante).", "Ninguna adicional.", "—", "—", "Ola 4", (2, 1, 1, 2, 2)),
 "PDA-EX-006": (5, 3, "GPX (14/06/2026): registra un tránsito en junio (inicio del invierno). No prueba operabilidad con nieve. Salto de 4,9 km → ≈26,8 km netos. Transecta N–S que pasa por el Cruce N (34 m) y continúa al sur; 87% superpuesta con 005. 29% dentro del radio proxy.",
                "Dato de estacionalidad; no producto propio.", "Comparar con registros de julio–septiembre (no hay en el set).", "Nieve/barro.", "Condición del camino en junio.", "Ola 2 (dato invernal)", (3, 3, 3, 2, 3)),
 "PDA-EX-007": (6, 5, "GPX: comienza a 9,6 km de Inicio; 0% dentro del radio proxy; 94% superpuesto con 008 y 70% con 023 (Comunidad Colluqueo); ~33 km/h. NO es circuito local: corrige la recomendación v2 que lo ponía en Ola 1.",
                "Tramo externo.", "Gabinete de titularidad.", "Terceros/comunidad.", "Titularidad.", "Ola 4", (1, 4, 1, 2, 1)),
 "PDA-EX-008": (6, None, "GPX (21/05/2026): bucle de 14,65 km (inicio–fin 0,6 km) a 9,1 km de Chivero; 0% dentro del radio proxy; 65% superpuesto con 023. 'Llaima' es un waypoint a 1.722 m: posible mirador. Probablemente en territorio de terceros/comunidad.",
                "Mirador como producto de terceros/alianza.", "Gabinete.", "Terceros/comunidad.", "Titularidad.", "Ola 3", (1, 4, 1, 4, 1)),
 "PDA-EX-009": (6, None, "GPX: el waypoint 'Inicio' está a 15,6 km de la Base Inicio: es el inicio del track, no la base (X04 resuelta). 'Hito' a -38.811, -71.244.",
                "Producto especial con autorización.", "Gabinete legal.", "Terceros.", "Autorización escrita.", "Ola 3", (1, 5, 1, 2, 1)),
 "PDA-EX-010": (4, 5, "GPX: pasa por Inicio (9 m) y Vaquero (7 m); 48% dentro del radio proxy; 90% superpuesto con 012. 'Entrada Pilhue' a 2,6 km y Laguna Pilhue a ≈2,7 km al O de Inicio, AL ESTE del 'Punto límite campo' (3,55 km al O): HIP a verificar con el titular, la laguna podría estar dentro o lindante con el campo.",
                "Inicio → Laguna Pilhue como posible producto corto si es interno.", "Gabinete: ¿Pilhue dentro del campo? Campo Ola 2.", "Terceros; ambiente lacustre.", "Límite oeste del campo.", "Ola 2", (2, 3, 3, 4, 2)),
 "PDA-EX-011": (5, None, "GPX: a 8–9 km de las bases; 0% dentro del radio proxy.", "Enlace regional.", "Gabinete.", "Zona fronteriza.", "Jurisdicción.", "Ola 4", (1, 5, 1, 3, 1)),
 "PDA-EX-012": (4, 6, "GPX (07/05/2026): bucle desde Villa Pehuenia (inicio–fin 0,66 km), 2,32 h en movimiento; pasa a 22 m de Vaquero; 22% dentro del radio proxy. Atractivos cercanos al campo: Aduana Vieja (1,9 km de Chivero) y Laguna Pilhue (2,7 km de Inicio). Lejanos: Laguna del Arco (9,4 km), Vista del Aluminé (7,2 km al S).",
                "Travesía regional; sus segmentos cercanos alimentan productos propios.", "Gabinete legal/ambiental; campo Ola 3.", "Terceros, vados, competencia.", "Titularidad por tramo.", "Ola 3", (2, 2, 4, 5, 2)),
 "PDA-EX-013": (5, 2, "GPX (27/03/2026): sale a 137 m de Inicio, sube por el eje N–S hasta el Cruce N (3 m) y sigue por la traza tipo ruta 015 (71% superpuesto) hacia el E: Puente y Vado sobre el río (1,6–1,7 km de Vaquero) y Vertiente; termina a 0,5 km de Litrán. Es mayormente camino de acceso, posiblemente público: NO es circuito interno (corrige v1/v2).",
                "Conocer el cruce del río y el acceso desde Litrán.", "Campo Ola 2: puente (carga), vado (crecidas).", "Vía pública; puente; vado.", "Carácter público del camino.", "Ola 2", (3, 4, 3, 2, 2)),
 "PDA-EX-014": (5, None, "GPX: a 6,2 km de Chivero; 97% superpuesto con 016.", "—", "—", "—", "—", "Ola 4", (1, 5, 1, 1, 2)),
 "PDA-EX-015": (5, None, "GPX (19–20/06/2026): traza tipo ruta (259,9 km en 4,5 h en movimiento) que pasa a 3 m de Litrán y por el acceso RP13/RP12 (CONF) y por el Cruce N: su tramo NO–SE en el acceso sería la RP13 (INF). Acceso→Litrán ≈6,9 km por trazas. Corte Litrán del titular pendiente de generar.",
                "Definir el tramo de acceso Litrán→Paso del Arco.", "Gabinete: generar derivado acceso–Litrán y conservar original.", "Vía pública.", "Confirmar qué ruta es cada rama.", "Ola 1 (gabinete)", (1, 1, 4, 1, 3)),
 "PDA-EX-016": (6, None, "GPX: pasa a 5 m de Inicio; 15,4 h transcurridas (archivo de jornada larga).", "Travesía internacional (Etapa 3+).", "Gabinete.", "Binacional.", "Normativa.", "Ola 4", (1, 2, 1, 3, 1)),
 "PDA-EX-017": (5, None, "GPX: >90% superpuesto con 010, 012, 023 y 024: redundante.", "—", "—", "Terceros.", "—", "Ola 4", (1, 4, 1, 3, 1)),
 "PDA-EX-018": (5, None, "GPX: archivo de 78,6 h (varios días) con 6 saltos (uno de 12,4 km) → ≈59,5 km netos; 19% dentro del radio proxy.", "Traslado.", "Gabinete.", "Vía pública.", "—", "Ola 4", (2, 2, 1, 2, 2)),
 "PDA-EX-019": (3, 5, "GPX (09/06/2026, junio): 29,15 km; 70,5% dentro del radio proxy; ida y vuelta por el eje N–S desde el sur (-38.879, -71.066) hasta Vaquero (20 m), partiendo del acceso RP13/RP12 (CONF); ~35 km/h → corre mayormente sobre el camino principal. Si ese eje es ruta pública (¿RP12?), gran parte del recorrido no es interno.",
                "Recorrido panorámico del eje; conexión sur.", "Campo Ola 1: % sobre camino público vs. huella privada.", "Tránsito público.", "Carácter público del eje N–S.", "Ola 1", (4, 4, 3, 2, 3)),
 "PDA-EX-020": (6, None, "GPX (31/05/2026): a 10,4 km de Inicio; altura máxima 1.955 m.", "Alianza con la comunidad.", "Gabinete institucional.", "Licencia social.", "Reglas de acceso.", "Ola 4", (1, 5, 1, 5, 1)),
 "PDA-EX-021": (4, None, "GPX (15/02/2026): 2 saltos (uno de 13,5 km) → ≈136 km netos; pasa por Inicio (1 m) y Vaquero (20 m); 26% dentro del radio proxy. Waypoint 'Foto' = Vado Aduana Vieja.", "Travesía larga (Etapa 3).", "Gabinete; campo Ola 3.", "Fatiga, terceros.", "Segmentación.", "Ola 3", (2, 1, 2, 3, 2)),
 "PDA-EX-022": (1, None, "GPX (22/05/2026): 23,36 km, 100% dentro del radio proxy; 1,36 h en movimiento (~17 km/h, el ritmo más lento del set: típico de huella 4x4); +694 m de desnivel acumulado (1.314–1.641 m). Pasa a 57 m de Vaquero, 140 m de Inicio, 149 m de Chivero y 36 m del Cruce N. Incluye el bucle norte (Aduana Vieja/Castillo) y el ramal oeste (63% superpuesto con 003). Una parte usa el eje N–S (50% superpuesto con 019).",
                "Producto insignia de medio día; base para el Bautismo (bucle norte corto) y la escuela de manejo.", "Campo Ola 1, PRIMERO; separar tramos sobre el eje N–S.", "Pendientes (+694 m); tramo sobre camino principal.", "Duración comercial, dificultad, tramos públicos.", "Ola 1", (5, 4, 3, 4, 4)),
 "PDA-EX-023": (6, None, "GPX (27/05/2026): a 2,3 km de Inicio en su punto más cercano; 4,7% dentro del radio proxy; comparte zona con 007 y 008.", "Co-diseño comunitario.", "Gabinete institucional.", "Conflicto territorial.", "Posición de la comunidad.", "Ola 3", (1, 2, 1, 4, 1)),
 "PDA-EX-024": (4, 5, "GPX (26/02/2026): 'Puesto Vaquero' = Base Vaquero (31 m); 'Entrada campo mecánico' a 0,49 km de Chivero cerca del 'Cruce N'; 'Grupo el Arco' = 'Castillo' (003). ALERTA: las altitudes de este archivo son ≈350–400 m menores que las de los demás en los mismos puntos (sesgo del equipo): no usarlas. Salto de 3,7 km → ≈91,5 km netos.",
                "Travesía Vaquero–lagunas (Etapa 3); fuente de datos de conexión.", "Gabinete resuelto en v2.1; campo Ola 3.", "Vados, Tramo Piedra, terceros.", "Titularidad por tramo.", "Ola 3", (3, 1, 5, 5, 2)),
}
_NEW = []
for c in CIRCUITOS:
    o = OV[c[0]]; g = GPX[c[1]]
    rel = (f"Mín. a Inicio {g['near']['Inicio']['km']:.2f} km · Vaquero {g['near']['Vaquero']['km']:.2f} km · Chivero {g['near']['Chivero']['km']:.2f} km "
           f"(GPX v2.1; distancia al punto más cercano, no prueba acceso)")
    c2 = list(c)
    c2[7] = rel; c2[8] = o[0]; c2[9] = o[1]; c2[10] = o[2]; c2[12] = o[3]; c2[14] = o[4]; c2[15] = o[5]; c2[16] = o[6]; c2[17] = o[7]; c2[18] = o[8]
    _NEW.append(tuple(c2))
CIRCUITOS = _NEW

# ---------- Bases ----------
BASES = [
 (BASES[0][0], BASES[0][1], BASES[0][2], BASES[0][3], BASES[0][4], BASES[0][5],
  "GPX v2.1: el waypoint 'Quincho' (003) está a 6 m: coincidencia geométrica con el quincho informado. 6 trazas pasan a ≤10 m: Inicio es un nodo de la red regional hacia el oeste (Laguna Pilhue y lagunas). A 7,8 km en línea recta y ≈10,1 km por trazas del acceso RP13/RP12; ≈1.490 m. Es la PRIMERA base desde el acceso RP13/RP12 (CONF): ≈10,1 km por la rama NE y +≈330 m de ascenso (v2.2; corrige la estimación de v2.1).",
  BASES[0][7]),
 (BASES[1][0], BASES[1][1], BASES[1][2], BASES[1][3], BASES[1][4], BASES[1][5],
  "GPX v2.1: el waypoint 'Puesto Vaquero' (024) está a 31 m: correspondencia geométrica fuerte. 7 trazas pasan a ≤25 m. A ≈12,1 km por trazas del acceso RP13/RP12 (≈2 km después de Inicio); ≈1.360 m. Asado a la estaca sujeto al régimen de fuego (EXTW).",
  BASES[1][7]),
 (BASES[2][0], BASES[2][1], BASES[2][2], BASES[2][3], BASES[2][4], BASES[2][5],
  "GPX v2.1: ninguna traza pasa a menos de 140 m: el camino de acceso a Chivero NO está documentado en los GPX. A ≈13,1 km por trazas del acceso (los últimos ~140 m sin traza). Waypoints cercanos: 'CP' (186 m, significado a aclarar) y 'Cima' (0,75 km). Con Vaquero a 1,3 km, forman el polo norte del campo, junto al 'Cruce N' donde llega un segundo camino desde el este (traza 015).",
  BASES[2][7]),
 (BASES[3][0], BASES[3][1], None, None, BASES[3][4], BASES[3][5],
  "Sin coordenadas. Referencias candidatas en los GPX (HIP, no asignar sin confirmar): 'Grupo el Arco'/'Castillo' (-38.7921, -71.0708), 1,9 km al N de Chivero; cruce de río 'Río/Puente/Vado' (-38.812/-38.814, -71.031/-71.033), 1,6–1,7 km al E de Vaquero.",
  BASES[3][7]),
]

DIST_BASES = DIST_BASES + [("Acceso RP13/RP12 (CONF)", n, km, txt) for n, km, txt in ACCESO["dist"]]

# ---------- Portafolio: circuitos candidatos ----------
_pc = {"P01": "PDA-EX-022 (bucle norte: Cima–Aduana Vieja–Castillo, cerca de Chivero)", "P02": "PDA-EX-022, segmentos internos de PDA-EX-003",
       "P03": "PDA-EX-003 (ramal oeste a Punto límite campo), PDA-EX-022, PDA-EX-004", "P06": "PDA-EX-022 (bucle norte)",
       "P07": "PDA-EX-022, ramal oeste de PDA-EX-003", "P08": "Tramos internos de PDA-EX-022/003 (definir pista)", "P11": "PDA-EX-022 (a evaluar en invierno); dato de junio: PDA-EX-006/019"}
PORTAFOLIO = [tuple(list(p[:14]) + [_pc.get(p[0], p[14])]) for p in PORTAFOLIO]

# ---------- Discrepancias ----------
_st = {"X01": ("Las cifras del catálogo se reproducen EXACTAMENTE con haversine sobre los GPX (v2.1). Diferencias pendientes solo frente a la hoja 'Geometría GPX' (no adjunta). Además, el catálogo incluye saltos en línea recta: ver X16. REC: adoptar la hoja 02b como inventario maestro.", "Parcialmente resuelta"),
       "X02": ("Los GPX contienen 53 waypoints (coincide con el dossier). El anexo omitió 6 nombres repetidos (Pilhue y Entrada Pilhue ×2 en 010; Árbol ×4 en 021; Laguna Pilhue ×2 en 024).", "Resuelta"),
       "X04": ("El waypoint 'Inicio' está a 15,6 km de la Base Inicio: es el inicio del track.", "Resuelta"),
       "X05": ("'Quincho' a 6 m de Base Inicio: coincidencia geométrica. Confirmar identidad en campo.", "Resuelta (geométrica)"),
       "X06": ("'Puesto Vaquero' a 31 m de Base Vaquero: coincidencia geométrica. Confirmar en campo.", "Resuelta (geométrica)"),
       "X10": ("Superada: la v2.1 muestra que XF1 C está a 9–10 km de las bases (ver X12).", "Superada")}
DISCREPANCIAS = [(d[0], d[1], d[2], d[3], _st[d[0]][0], _st[d[0]][1]) if d[0] in _st else d for d in DISCREPANCIAS] + [
 ("X11", "Altitudes entre archivos", "En los mismos puntos, 024 registra ≈350–400 m menos que el resto y 018 ≈100 m menos.", "GPX v2.1", "No usar altitudes GPX para dificultad; usar un modelo digital de elevación (MDE) o una medición única.", "Abierta"),
 ("X12", "XF1 C y XFelicinda como 'candidato núcleo'", "v1 los clasificó núcleo y v2 propuso XF1 C para Ola 1; los GPX los ubican a 9–10 km de las bases, sin tramos en el radio proxy.", "Anexo v1; v2; GPX", "Reclasificados como externos (6). Error de v2 corregido.", "Resuelta en v2.1"),
 ("X13", "Punto de acceso", "v2 usó Litrán como referencia. v2.1 ESTIMÓ el acceso RP13/RP12 junto a Chivero/Vaquero: ERROR de ≈10 km (ese punto es otro cruce, el 'Cruce N'). El titular aportó la coordenada: -38.902440, -71.064667.", "v2; v2.1; titular", "v2.2 recalcula todo desde la coordenada del titular. Inicio vuelve a ser la primera base desde el acceso (≈10,1 km por trazas).", "Resuelta (v2.2)"),
 ("X14", "Redundancia del inventario", "1.318 km suman los 24 archivos, pero la red única es de ≈457 km (método de grilla): ~65% es superposición. Ejemplos: 017 (>90% con 4 trazas), 014 (97%), 002 (93%).", "GPX v2.1", "Gestionar la red como grafo de tramos únicos y no como 24 rutas.", "Abierta"),
 ("X15", "Origen de las trazas (Wikiloc)", "No consta si los 24 archivos son registros propios o descargados de terceros en Wikiloc.", "RutasWKLC.zip", "Confirmar autoría. Si son de terceros: no publicarlos y revisar las condiciones de uso.", "Abierta"),
 ("X16", "Saltos incluidos en el km del catálogo", "5 archivos tienen saltos >1 km en línea recta (003: 10,8 km; 021: 13,5; 018: 12,4; 006: 4,9; 024: 3,7).", "GPX v2.1", "Reportar km brutos y netos (columna 'km sin saltos >1 km').", "Abierta"),
 ("X17", "Rama NE / eje N–S: ¿RP12 pública?", "Desde el acceso RP13/RP12 la única rama hacia las bases es la NE, que sigue por Tranquera, Inicio, Cruce N y Vaquero. Por descarte sería la RP12 (INF). Si es pública, la llegada a las bases y parte de 019 y 022 son vía pública.", "GPX v2.1", "Confirmar con el titular y con la cartografía vial provincial.", "Abierta"),
]

# ---------- Datos faltantes ----------
_fd = {"D03": ("GPX", "24 GPX originales", "Base de datos auditable", "RECIBIDOS (RutasWKLC.zip, 24 archivos, hash SHA-256 en hoja 02b)", "Resuelta"),
       "D05": ("GPX", "Fechas de cada track", "Estacionalidad", "Extraídas: feb-2024 a nov-2026; sin registros de julio a septiembre", "Resuelta"),
       "D06": ("GPX", "6 waypoints faltantes", "Integridad", "Explicados: nombres repetidos omitidos en el anexo", "Resuelta")}
FALTANTES = [(f[0],) + _fd[f[0]] if f[0] in _fd else f for f in FALTANTES] + [
 ("D23", "Acceso", "Coordenada de la intersección RP13/RP12", "Recepción, logística", "RECIBIDA del titular: -38.902440, -71.064667. Falta confirmar que la rama NE es la RP12", "Resuelta parcial"),
 ("D24", "Acceso", "¿La rama NE (acceso→Inicio→Cruce N→Vaquero) es la RP12 pública en todo su recorrido? ¿Dónde empieza el campo sobre ella? ¿Camino hasta Chivero?", "Encuadre legal de los circuitos 019/022", "Titular + Vialidad + catastro", "Crítica"),
 ("D25", "GPX", "Autoría de las trazas de Wikiloc", "Uso comercial y publicación", "Titular", "Alta"),
 ("D26", "Territorio", "¿La Laguna Pilhue y la Aduana Vieja están dentro del campo?", "Atractivos propios de alto valor", "Titular + mensura", "Alta"),
 ("D27", "Territorio", "Significado de los waypoints 'CP' y 'Castillo/Grupo el Arco'", "Interpretación y producto", "Titular", "Media"),
 ("D28", "Terreno", "Modelo digital de elevación para pendientes y desniveles", "Dificultad", "MDE público (SRTM/ALOS) o relevamiento", "Media"),
]

# ---------- Implementación ----------
_done = {"T01": "HECHO v2.1 (hash SHA-256)", "T02": "HECHO v2.1 (hoja 02b)", "T03": "HECHO v2.1 (hoja 02c y mapas)"}
IMPLEMENTACION = [(t[0], t[1], t[2], t[3], _done.get(t[0], t[4]), t[5]) for t in IMPLEMENTACION]
IMPLEMENTACION.insert(3, ("T03b", "Etapa 0", "Acceso RP13/RP12 recibido (v2.2). Confirmar si la rama NE es RP12 pública, dónde está la tranquera de ingreso al campo y ubicar el puesto del Arroyo del Arco", "Titular", "Sem 1", "Nota + puntos GPS"))
IMPLEMENTACION = [(t[0], t[1], "Inspección Ola 1: 022 (bucle norte y ramal oeste), segmentos internos de 003, 019 (con relevamiento de tramos públicos); verificar el camino a Chivero", t[3], t[4], "Fichas F01") if t[0] == "T07" else t for t in IMPLEMENTACION]

# ---------- Riesgos ----------
RIESGOS = [(r[0], r[1], "Trazas con km inflados por saltos, altitudes sesgadas entre archivos, ~65% de superposición y autoría Wikiloc no confirmada.", r[3], r[4], "Usar la hoja 02b como maestro; MDE para pendientes; confirmar autoría.", r[6], r[7]) if r[0] == "R07" else r for r in RIESGOS]
RIESGOS.append(("R15", "Vial/legal", "Llegada a las bases por ≈10–13 km de la rama NE, probablemente RP12 pública (INF): traslados de pasajeros en vía pública (habilitación de transporte), tránsito de terceros, estado del camino en invierno y deshielo; y circuitos 019/022 que la usan en parte.", "Media", "Alto", "Confirmar el carácter del camino; priorizar huellas privadas; señalización y velocidad máxima en convoy.", "Operaciones", "Etapa 0"))
