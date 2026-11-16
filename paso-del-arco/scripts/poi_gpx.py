# -*- coding: utf-8 -*-
"""Escribe el GPX base de puntos de interés (solo puntos con coordenada). Uso: poi_gpx.py <scripts_dir> <out.gpx>"""
import sys
from xml.sax.saxutils import escape
sys.path.insert(0, sys.argv[1])
import os
from data_v23 import POI
L = ['<?xml version="1.0" encoding="UTF-8"?>', '<gpx version="1.1" creator="Paso del Arco - relevamiento POI v1" xmlns="http://www.topografix.com/GPX/1/1">',
     '<metadata><name>PDA POI base v1</name><desc>Puntos conocidos para verificar en el relevamiento con fotos. No representa límites ni accesos autorizados.</desc></metadata>']
for c, n, t, la, lo, o, e, q in POI:
    if la is None: continue
    L.append(f'<wpt lat="{la:.6f}" lon="{lo:.6f}"><name>{escape(c + " " + n)}</name><desc>{escape(f"Tipo: {t}. Origen: {o}. Estado: {e}. Relevar: {q}")}</desc><type>{escape(t)}</type></wpt>')
L.append("</gpx>")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(L)); print(sum(1 for p in POI if p[3] is not None), "waypoints")
