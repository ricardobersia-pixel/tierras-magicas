# -*- coding: utf-8 -*-
"""Tramo RP12 (acceso→Cruce N, camino más corto en la red GPX) y km de cada traza sobre él; tranquera 1 y lados de la ruta.
Uso: rp12.py <dir_gpx> <out_json>"""
import sys, os, math, heapq, json
import xml.etree.ElementTree as ET
NS = {"g": "http://www.topografix.com/GPX/1/1"}
def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(h))
C = 0.0002; key = lambda p: (round(p[0]/C), round(p[1]/C))
G, P, TR = {}, {}, {}
for f in sorted(os.listdir(sys.argv[1])):
    r = ET.parse(os.path.join(sys.argv[1], f)).getroot(); n = r.find("g:trk/g:name", NS).text
    pts = [(float(p.get("lat")), float(p.get("lon"))) for p in r.iterfind(".//g:trkpt", NS)]; TR[n] = pts
    for i, p in enumerate(pts):
        k = key(p); P.setdefault(k, p)
        if i and hav(pts[i-1], p) <= 0.2:
            k0 = key(pts[i-1])
            if k0 != k: G.setdefault(k0, {})[k] = 1; G.setdefault(k, {})[k0] = 1
for k in list(G):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            k2 = (k[0]+dx, k[1]+dy)
            if k2 != k and k2 in G: G[k][k2] = 1; G[k2][k] = 1
W = lambda a, b: hav(P[a], P[b])
near = lambda pt: min(G, key=lambda k: hav(P[k], pt))
def sp(a, b):
    dist = {a: 0}; prev = {}; h = [(0, a)]
    while h:
        d, u = heapq.heappop(h)
        if u == b: break
        if d > dist[u]: continue
        for v in G[u]:
            nd = d + W(u, v)
            if nd < dist.get(v, 9e9): dist[v] = nd; prev[v] = u; heapq.heappush(h, (nd, v))
    path = [b]
    while path[-1] != a: path.append(prev[path[-1]])
    return dist[b], [P[k] for k in path[::-1]]
ACC = (-38.902440, -71.064667); TQ = (-38.832922, -71.058162); CN = (-38.810607, -71.057450)
B = {"Inicio": (-38.832050, -71.066724), "Vaquero": (-38.814204, -71.050709), "Chivero": (-38.807993, -71.063218)}
d_tq, path_acc_tq = sp(near(ACC), near(TQ))
d_cn, path = sp(near(ACC), near(CN))
out = {"tranquera1": TQ, "tranquera_snap_m": round(hav(P[near(TQ)], TQ)*1000), "acc_a_tranquera_km": round(d_tq, 2),
       "rp12_acc_cruceN_km": round(d_cn, 2), "rp12_path": path[::3], "tracks": {}, "bases": {}}
def lado(pt):  # lado respecto de la RP12 (O/E) usando el punto de la ruta más cercano
    j = min(range(len(path)), key=lambda i: hav(path[i], pt)); q = path[j]
    return ("O" if pt[1] < q[1] else "E"), round(hav(pt, q), 3)
for n, pt in list(B.items()) + [("Tranquera 1", TQ)]:
    s, dm = lado(pt); out["bases"][n] = {"lado_RP12": s, "dist_RP12_km": dm}
    print(n, s, dm)
for n, pts in TR.items():
    on = 0.0; tot = 0.0
    for i in range(1, len(pts)):
        d = hav(pts[i-1], pts[i])
        if d > 1: continue
        tot += d; m = ((pts[i-1][0]+pts[i][0])/2, (pts[i-1][1]+pts[i][1])/2)
        if min(hav(m, q) for q in path[::2]) < 0.04: on += d
    out["tracks"][n] = {"km_sobre_RP12": round(on, 2), "pct_sobre_RP12": round(100*on/tot, 1) if tot else 0}
print("acc→tranquera", round(d_tq, 2), "km; RP12 acc→cruceN", round(d_cn, 2), "km; snap tranquera", out["tranquera_snap_m"], "m")
for n, v in sorted(out["tracks"].items(), key=lambda x: -x[1]["pct_sobre_RP12"]): print(f"{n[:45]:45s} {v['km_sobre_RP12']:6.2f} km {v['pct_sobre_RP12']:5.1f}%")
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
