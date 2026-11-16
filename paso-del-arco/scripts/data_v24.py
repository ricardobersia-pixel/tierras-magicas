# -*- coding: utf-8 -*-
"""v2.4: nueva codificación de puntos (ZONA-TIPO-NN) y hoja de ruta del relevamiento."""
import json, os
from data_v23 import *

HR = json.load(open(os.environ["HOJA_RUTA_JSON"]))
TIPO_TXT = dict(HR["tipos"])
JORNADA_DE = {}
for j in HR["jornadas"]:
    for c in j["secuencia"] + j["buscar"]:
        JORNADA_DE.setdefault(c, j["codigo"])
# Misma forma que POI v2.3: (código, punto, tipo, lat, lon, origen, estado, qué relevar)
POI = [(c, f"{n} [alias {al}]", TIPO_TXT[c.split("-")[1]], la, lo, o, ("Coordenada a relevar" if la is None else "Verificar") + f" · {JORNADA_DE.get(c, '—')}", q)
       for c, n, la, lo, al, o, q in HR["poi"]]
PROTOCOLO = [(a, b.replace("'PDA_POI_base_v1.gpx'", "'PDA_puntos_codificados_v1.gpx' o el GPX de la jornada (REL-D1 … REL-D5)")
              .replace("Nombrar con el código y el nombre de la planilla (ej. 'PDA-POI-013 Laguna Pilhue'). Para puntos nuevos, seguir la numeración desde PDA-POI-031.",
                       "Nombrar con el código ZONA-TIPO-NN y el nombre (ej. 'L-LAG-01 Laguna Pilhue'). Para puntos nuevos, usar el próximo número libre de esa zona y tipo (ver la hoja 20).")
              .replace("Nombre: 'PDA-REL-AAAAMMDD'.", "Nombre: 'REL-D1-AAAAMMDD' (jornada y fecha).")) for a, b in PROTOCOLO]
PROTOCOLO.append(("Fotos (nombre)", "Renombrar al descargar: CÓDIGO_AAAAMMDD_N.jpg (ej. O-BAS-01_20261120_1.jpg)."))
