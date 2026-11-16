# -*- coding: utf-8 -*-
"""Grafo de la red GPX (celdas ~20 m) y distancias por traza desde el acceso. Uso: gpx_network.py <dir_gpx> <lat> <lon>"""
import sys, os, math, heapq, json
import xml.etree.ElementTree as ET
NS = {"g": "http://www.topografix.com/GPX/1/1"}
def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(h))
C = 0.0002
key = lambda p: (round(p[0]/C), round(p[1]/C))
G = {}; P = {}; ELE = {}; NAMES = {}
for f in sorted(os.listdir(sys.argv[1])):
    r = ET.parse(os.path.join(sys.argv[1], f)).getroot(); n = r.find("g:trk/g:name", NS).text
    pts = [(float(p.get("lat")), float(p.get("lon")), float(p.find("g:ele", NS).text)) for p in r.iterfind(".//g:trkpt", NS)]
    for i, p in enumerate(pts):
        k = key(p); P.setdefault(k, p[:2]); NAMES.setdefault(k, set()).add(n)
        if "XXMoquehue" not in n: ELE.setdefault(k, []).append(p[2])
        if i:
            d = hav(pts[i-1], p)
            if d > 0.2: continue
            k0 = key(pts[i-1])
            if k0 == k: continue
            G.setdefault(k0, {}); G.setdefault(k, {})
            w = hav(P[k0], P[k]); G[k0][k] = w; G[k][k0] = w
# unir celdas vecinas (tolerancia entre trazas paralelas)
ks = list(G)
for k in ks:
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            k2 = (k[0]+dx, k[1]+dy)
            if k2 != k and k2 in G:
                d = hav(P[k], P[k2]); G[k][k2] = min(G[k].get(k2, 9e9), d)
def nearest(pt):
    return min(G, key=lambda k: hav(P[k], pt))
def dijkstra(src):
    dist = {src: 0}; prev = {}; h = [(0, src)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]: continue
        for v, w in G[u].items():
            nd = d + w
            if nd < dist.get(v, 9e9): dist[v] = nd; prev[v] = u; heapq.heappush(h, (nd, v))
    return dist, prev
A = (float(sys.argv[2]), float(sys.argv[3]))
T = {"Acceso RP13/RP12": (-38.902440, -71.064667), "Tranquera 1 (CONF)": (-38.832922, -71.058162), "Inicio": (-38.832050, -71.066724), "Vaquero": (-38.814204, -71.050709), "Chivero": (-38.807993, -71.063218),
     "Cruce N (traza 015 / eje N–S)": (-38.810607, -71.057450), "Litrán RP13/RP23": (-38.867250, -71.027544),
     "Tranquera (013)": (-38.832388, -71.057847), "Laguna Pilhue (wpt)": (-38.836408, -71.097463), "Aduana Vieja (wpt)": (-38.791826, -71.058897),
     "Punto límite campo (wpt)": (-38.818238, -71.103710), "Vista del Aluminé (wpt)": (-38.896102, -71.056230)}
ka = nearest(A); dist, prev = dijkstra(ka)
out = {"acceso": A, "snap_m": round(hav(P[ka], A)*1000), "trazas_en_acceso": sorted(NAMES[ka] | set().union(*[NAMES.get((ka[0]+i, ka[1]+j), set()) for i in (-2,-1,0,1,2) for j in (-2,-1,0,1,2)])),
       "ele_acceso": round(sorted(ELE.get(ka, [0]))[len(ELE.get(ka, [0]))//2]), "destinos": {}}
for n, t in T.items():
    kt = nearest(t); d = dist.get(kt)
    # perfil: altitud mediana en destino
    e = ELE.get(kt); em = round(sorted(e)[len(e)//2]) if e else None
    path = [];
    if d is not None:
        u = kt
        while u != ka: path.append(P[u]); u = prev[u]
    out["destinos"][n] = {"linea_recta_km": round(hav(A, t), 3), "por_red_km": round(d, 2) if d is not None else None,
                          "snap_m": round(hav(P[kt], t)*1000), "alt_mediana_m": em, "path": path[::-1][::5]}
    print(f"{n:32s} recta={hav(A,t):6.2f} km  red={d if d is None else round(d,2)} km  snap={hav(P[kt],t)*1000:.0f} m  alt≈{em}")
print("snap acceso", out["snap_m"], "m; alt acceso ≈", out["ele_acceso"]); print("trazas en acceso:", out["trazas_en_acceso"])
json.dump(out, open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
