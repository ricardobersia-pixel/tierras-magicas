# -*- coding: utf-8 -*-
"""Recálculo reproducible de los 24 GPX (método único). Uso: python3 -I gpx_analyze.py <dir_gpx> <out_json>"""
import sys, os, json, math, hashlib, unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime

NS = {"g": "http://www.topografix.com/GPX/1/1"}
R = 6371.0088
BASES = {"Inicio": (-38.832050, -71.066724), "Vaquero": (-38.814204, -71.050709), "Chivero": (-38.807993, -71.063218)}
LITRAN = (-38.867250, -71.027544)
JUMP_M = 200.0          # salto entre puntos consecutivos considerado discontinuidad
STOP_KMH = 2.0          # velocidad por debajo = detenido
ELE_HYST = 5.0          # histéresis para desnivel
NUCLEO_KM = 3.0         # PROXY: radio alrededor de alguna base (no es límite catastral)
CELL = 0.0005           # ~55 m lat / ~43 m lon para superposición

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def code_for(name):
    return name

def parse(path):
    root = ET.parse(path).getroot()
    name = root.find("g:trk/g:name", NS).text.strip()
    pts = []
    for p in root.iterfind(".//g:trkpt", NS):
        e = p.find("g:ele", NS); t = p.find("g:time", NS)
        pts.append((float(p.get("lat")), float(p.get("lon")), float(e.text) if e is not None else None,
                    datetime.strptime(t.text, "%Y-%m-%dT%H:%M:%SZ") if t is not None else None))
    wpts = []
    for w in root.iterfind("g:wpt", NS):
        n = w.find("g:name", NS); e = w.find("g:ele", NS)
        wpts.append({"name": (n.text or "").strip(), "lat": float(w.get("lat")), "lon": float(w.get("lon")),
                     "ele": float(e.text) if e is not None else None})
    segs = len(root.findall(".//g:trkseg", NS))
    return name, pts, wpts, segs

def analyze(path):
    name, pts, wpts, segs = parse(path)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    L = 0.0; jumps = []; moving_s = 0; Lnuc = 0.0
    gain = loss = 0.0; ref = None
    for i in range(1, len(pts)):
        a, b = pts[i-1], pts[i]
        d = hav(a, b)
        if d*1000 > JUMP_M: jumps.append(round(d, 3))
        L += d
        mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
        if min(hav(mid, c) for c in BASES.values()) <= NUCLEO_KM: Lnuc += d
        if a[3] and b[3]:
            dt = (b[3]-a[3]).total_seconds()
            if dt > 0 and d/(dt/3600) >= STOP_KMH and dt < 600: moving_s += dt
    for p in pts:
        if p[2] is None: continue
        if ref is None: ref = p[2]; continue
        if p[2]-ref >= ELE_HYST: gain += p[2]-ref; ref = p[2]
        elif ref-p[2] >= ELE_HYST: loss += ref-p[2]; ref = p[2]
    eles = [p[2] for p in pts if p[2] is not None]
    t0, t1 = pts[0][3], pts[-1][3]
    near = {}
    for bn, bc in list(BASES.items()) + [("Litrán", LITRAN)]:
        dmin, idx = min((hav((p[0], p[1]), bc), i) for i, p in enumerate(pts))
        near[bn] = {"km": round(dmin, 3), "lat": pts[idx][0], "lon": pts[idx][1]}
    for w in wpts:
        bn, bd = min(((k, hav((w["lat"], w["lon"]), c)) for k, c in BASES.items()), key=lambda x: x[1])
        w["base_mas_cercana"] = bn; w["km_a_base"] = round(bd, 3)
        w["km_al_track"] = round(min(hav((w["lat"], w["lon"]), (p[0], p[1])) for p in pts[::3]), 3)
    cells = sorted({(round(p[0]/CELL), round(p[1]/CELL)) for p in pts})
    return {
        "file": os.path.basename(path), "sha256": sha, "name": name, "segments": segs, "n_points": len(pts),
        "km": round(L, 2), "km_sin_saltos_1km": round(L - sum(j for j in jumps if j > 1.0), 2), "jumps_km": jumps, "n_jumps": len(jumps),
        "start": [pts[0][0], pts[0][1]], "end": [pts[-1][0], pts[-1][1]], "start_end_km": round(hav(pts[0], pts[-1]), 3),
        "t_start": t0.isoformat() if t0 else None, "t_end": t1.isoformat() if t1 else None,
        "elapsed_h": round((t1-t0).total_seconds()/3600, 2) if t0 and t1 else None,
        "moving_h": round(moving_s/3600, 2), "ele_min": round(min(eles)), "ele_max": round(max(eles)),
        "gain_m": round(gain), "loss_m": round(loss),
        "bbox": [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)],
        "km_nucleo_proxy": round(Lnuc, 2), "pct_nucleo_proxy": round(100*Lnuc/L, 1) if L else 0,
        "near": near, "wpts": wpts, "cells": cells,
        "pts_sample": [[p[0], p[1]] for p in pts[::max(1, len(pts)//400)]],
    }

def main():
    d, out = sys.argv[1], sys.argv[2]
    res = [analyze(os.path.join(d, f)) for f in sorted(os.listdir(d)) if f.lower().endswith(".gpx")]
    # superposición: % de celdas del track A presentes en B
    sets = {r["name"]: set(map(tuple, r["cells"])) for r in res}
    ov = {}
    for a in res:
        for b in res:
            if a["name"] == b["name"]: continue
            s = len(sets[a["name"]] & sets[b["name"]]) / len(sets[a["name"]])
            if s >= 0.10: ov.setdefault(a["name"], []).append((b["name"], round(100*s, 1)))
    seen = set(); tot = 0.0
    for r in sorted(res, key=lambda x: -x["km"]):
        c = set(map(tuple, r["cells"])); new = len(c - seen) / len(c); seen |= c
        r["pct_celdas_nuevas"] = round(100 * new, 1)
    for r in res:
        r["overlaps"] = sorted(ov.get(r["name"], []), key=lambda x: -x[1]); del r["cells"]
    json.dump({"celdas_unicas": len(seen), "params": {"metodo": "haversine sobre trkpt consecutivos, R=6371.0088 km, sin suavizado 2D",
                          "salto_m": JUMP_M, "detenido_kmh": STOP_KMH, "histeresis_desnivel_m": ELE_HYST,
                          "radio_nucleo_proxy_km": NUCLEO_KM, "celda_superposicion_grados": CELL},
               "tracks": res}, open(out, "w"), ensure_ascii=False, indent=1)
    for r in res:
        print(f"{r['name'][:45]:45s} km={r['km']:7.2f} pts={r['n_points']:5d} jumps={r['n_jumps']} "
              f"{r['t_start'][:10]} mov={r['moving_h']}h el={r['elapsed_h']}h ele={r['ele_min']}-{r['ele_max']} +{r['gain_m']} "
              f"nuc={r['pct_nucleo_proxy']}% I={r['near']['Inicio']['km']} V={r['near']['Vaquero']['km']} C={r['near']['Chivero']['km']} "
              f"loop={r['start_end_km']} st={r['start'][0]:.4f},{r['start'][1]:.4f}")
        if r["jumps_km"]: print("    saltos:", r["jumps_km"][:8])
        if r["overlaps"]: print("    sup:", r["overlaps"][:5])

main()
