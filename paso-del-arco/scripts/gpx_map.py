# -*- coding: utf-8 -*-
"""Mapas esquemáticos (sin cartografía de fondo) de los 24 GPX. Uso: gpx_map.py <dir_gpx> <metrics.json> <out_dir> [lat lon acceso]"""
import sys, os, json, math
import xml.etree.ElementTree as ET
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
NS = {"g": "http://www.topografix.com/GPX/1/1"}
d, mj, out = sys.argv[1], sys.argv[2], sys.argv[3]
acc = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else None
M = json.load(open(mj))
code = {}
CODES = ["XAgua Fría - Villa Pehuenia","XBLDMR","XCP","XCampo Paso del Arco","XDomingo","XDomingo Junio","XF1 C","XFelicinda",
 "XIcalma - Moquehue María Puel","XLa Angostura - Laguna Vallejos - Villa Unión","XLa Angostura - Paso de Icalma",
 "XLaguna El Arco y Laguna Vallejos desde Villa Pehuenia","XLeña","XMarimenuco - Reducción Marimenuco",
 "XReducción Marimenuco - Moquehue - Zapala","XVilla Pehuenia Chile","XVilla Unión - Laguna Vallejos - Reducción Marimenuco 27",
 "XVilla Unión - Villa Pehuenia","XVilla Unión Corto","XVolcán Batea Mahuida desde Paso de Icalma","XVuelta","XX Circuito campo",
 "XXComunidad Colluqueo - Laguna El Arco - Laguna Vallejos - Moquehue","XXMoquehue - Laguna Vallejos - Villa Unión"]
CN = {n: f"{i+1:03d}" for i, n in enumerate(CODES)}
tracks = {}
for f in sorted(os.listdir(d)):
    r = ET.parse(os.path.join(d, f)).getroot()
    n = r.find("g:trk/g:name", NS).text.strip()
    tracks[n] = [(float(p.get("lat")), float(p.get("lon"))) for p in r.iterfind(".//g:trkpt", NS)]
BASES = {"Inicio": (-38.832050, -71.066724), "Vaquero": (-38.814204, -71.050709), "Chivero": (-38.807993, -71.063218)}
LIT = (-38.867250, -71.027544)
k = math.cos(math.radians(38.83))
HL = {"XX Circuito campo": "#1b9e77", "XLeña": "#d95f02", "XVilla Unión Corto": "#7570b3", "XDomingo Junio": "#e7298a",
      "XBLDMR": "#66a61e", "XCP": "#a6761d", "XReducción Marimenuco - Moquehue - Zapala": "#c00000"}

def draw(ext, fname, title, labels_wpt=True, only=None):
    fig, ax = plt.subplots(figsize=(13, 13 * (ext[1]-ext[0]) / ((ext[3]-ext[2]) * k)), dpi=130)
    for n, pts in tracks.items():
        if only and n not in only: continue
        ys, xs = zip(*pts)
        c = HL.get(n, "#9a9a9a"); lw = 2.2 if n in HL else 0.8
        ax.plot(xs, ys, color=c, lw=lw, alpha=0.9 if n in HL else 0.6,
                label=(f"{CN[n]} {n}" + (" (traza tipo ruta, posible RP13)" if "Zapala" in n else "")) if n in HL else None, zorder=3 if n in HL else 2)
    for t in M["tracks"]:
        if only and t["name"] not in only: continue
        for w in t["wpts"]:
            if ext[0] <= w["lat"] <= ext[1] and ext[2] <= w["lon"] <= ext[3]:
                ax.plot(w["lon"], w["lat"], "o", ms=3.5, color="#333", zorder=5)
                if labels_wpt: ax.annotate(w["name"], (w["lon"], w["lat"]), fontsize=6.5, xytext=(3, 3), textcoords="offset points", color="#222")
    for n, (la, lo) in BASES.items():
        ax.plot(lo, la, "s", ms=11, color="#0b3d2e", zorder=6); ax.annotate("BASE " + n.upper(), (lo, la), fontsize=9, weight="bold", xytext=(6, -12), textcoords="offset points", color="#0b3d2e")
    ax.plot(LIT[1], LIT[0], "^", ms=10, color="#c00000", zorder=6); ax.annotate("Litrán RP13/RP23 (CONF titular)", (LIT[1], LIT[0]), fontsize=8, xytext=(6, -10), textcoords="offset points", color="#c00000")
    if acc:
        ax.plot(acc[1], acc[0], "*", ms=16, color="#ff9900", mec="k", zorder=7)
        ax.annotate("Acceso RP13/RP12 — ESTIMADO (INF), confirmar", (acc[1], acc[0]), fontsize=8.5, weight="bold", xytext=(8, 6), textcoords="offset points", color="#b35900")
    ax.set_xlim(ext[2], ext[3]); ax.set_ylim(ext[0], ext[1]); ax.set_aspect(1 / k)
    ax.grid(True, lw=0.3, alpha=0.5); ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
    ax.set_title(title, fontsize=11)
    # escala 1 km
    x0 = ext[2] + (ext[3]-ext[2]) * 0.05; y0 = ext[0] + (ext[1]-ext[0]) * 0.04
    dlon = 1 / (111.32 * k); ax.plot([x0, x0 + dlon], [y0, y0], "k-", lw=3); ax.annotate("1 km", (x0, y0), xytext=(0, 5), textcoords="offset points", fontsize=8)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.85)
    fig.text(0.01, 0.005, "Esquema sin cartografía de fondo. Trazas de los 24 GPX (Wikiloc, aportados por el titular). No representa límites legales ni prueba accesos.", fontsize=7, color="#555")
    fig.savefig(os.path.join(out, fname), bbox_inches="tight"); plt.close(fig)

draw((-38.93, -38.72, -71.31, -71.00), "mapa_regional.png", "Paso del Arco — red de 24 trazas (vista regional)", labels_wpt=False)
draw((-38.875, -38.775, -71.115, -71.010), "mapa_nucleo.png", "Paso del Arco — entorno de las bases (vista núcleo)")
