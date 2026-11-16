# -*- coding: utf-8 -*-
"""Importa un GPX exportado de Wikiloc (relevamiento Paso del Arco) y lo convierte a la planilla de puntos.
- Normaliza los nombres escritos en el celular al código canónico ZONA-TIPO-NN.
- Lee las etiquetas cortas de la descripción (C: A: E: R:).
- Compara cada punto con el catálogo (puntos conocidos a <60 m) y numera los puntos nuevos.
Uso: python3 -I wikiloc_import.py <catalogo hoja_ruta.json> <salida.xlsx> <gpx> [<gpx> ...]"""
import sys, re, json, math, unicodedata
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

ZONAS = set("RONELXP")
TIPOS = {"ACC", "BAS", "TRQ", "CRZ", "VAD", "PTE", "AGU", "LAG", "MIR", "CER", "LIM", "PAT", "FOR", "ARB", "PUE", "RSG", "SRV", "FOT",
         "GAS", "ALO", "FRO", "CMB", "SAL", "APR", "ALI", "RET", "COM", "OTR"}
TERRITORIOS = set()  # se carga del catálogo
MATCH_M = 60

def sin_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

PAT = re.compile(r"^(?:\d{1,2}[\s.)-]+)?([AC][A-Z]{2}|[RONELXP0])[\s\-_./]*([A-Z]{3})[\s\-_./]*(N?)[\s\-_./]*(\d{1,2})([A-Z]?)(?=$|[\s\-_.,:;])[\s\-_.,:;]*(.*)$")

def normalizar(nombre):
    """Devuelve (codigo, es_nuevo, sufijo, resto, alerta)."""
    s = sin_acentos((nombre or "").strip()).upper()
    m = PAT.match(s)
    if not m:
        return None, False, "", nombre, "Nombre sin código reconocible"
    z, t, nuevo, n, suf, resto = m.groups()
    alerta = ""
    if z == "0": z = "O"; alerta = "Zona escrita como cero: se tomó O (oeste)"
    if t not in TIPOS:
        return None, False, "", nombre, f"Tipo '{t}' no existe en la lista"
    if len(z) == 3 and z not in TERRITORIOS:
        alerta = (alerta + "; " if alerta else "") + f"Territorio '{z}' no está en la tabla: agregarlo (A=Argentina, C=Chile + 2 letras)"
    return f"{z}-{t}-{int(n):02d}", bool(nuevo), suf, resto.strip(), alerta

ETQ = re.compile(r"\b([CAERHcaerh]|COM|com)\s*:\s*")
def etiquetas(desc):
    d = {"C": "", "A": "", "E": "", "R": "", "H": "", "COM": "", "obs": ""}
    if not desc: return d
    partes = ETQ.split(desc)
    d["obs"] = partes[0].strip()
    for i in range(1, len(partes) - 1, 2):
        k = partes[i].upper(); v = partes[i + 1].strip().rstrip(";,")
        if k == "R": d["R"] = v
        elif k in ("H", "COM"): d[k] = v
        else:
            tok, _, resto = v.partition(" ")
            d[k] = tok; d["obs"] = (d["obs"] + " " + resto).strip()
    c = sin_acentos(d["C"]).upper()
    d["C"] = {"S": "Sí", "SI": "Sí", "N": "No", "NO": "No", "?": "No sé"}.get(c, d["C"])
    a = d["A"].lower().replace(" ", "")
    d["A"] = {"4x4": "4x4", "4x2": "4x2", "pie": "A pie", "apie": "A pie", "p": "A pie"}.get(a, d["A"])
    e = d["E"].upper()
    d["E"] = {"B": "Bueno", "R": "Regular", "M": "Malo"}.get(e, d["E"])
    return d

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371008.8*math.asin(math.sqrt(h))

def main():
    J = json.load(open(sys.argv[1])); cat = J["poi"]
    TERRITORIOS.update(t[0] for t in J.get("territorios", []))
    conocidos = {p[0]: p for p in cat}
    usados = {}
    for c in conocidos:
        z, t, n = c.split("-"); usados.setdefault((z, t), set()).add(int(n))
    filas = []
    for path in sys.argv[3:]:
        root = ET.parse(path).getroot()
        ns = {"g": root.tag.split("}")[0].strip("{")} if root.tag.startswith("{") else {"g": ""}
        f = (lambda e, tag: e.find(f"g:{tag}", ns)) if ns["g"] else (lambda e, tag: e.find(tag))
        trk = root.find("g:trk/g:name", ns) if ns["g"] else root.find("trk/name")
        traza = trk.text.strip() if trk is not None and trk.text else path
        mr = re.search(r"\b(RUT|TRV)[\s\-_]*([A-Z]{2,3})[\s\-_]*(\d{1,2})([A-Z]?)(?:[.\s]*D(\d))?", sin_acentos(traza).upper())
        ruta = (f"{mr.group(1)}-{mr.group(2)}-{int(mr.group(3)):02d}{mr.group(4)}" + (f".D{mr.group(5)}" if mr.group(5) else "")) if mr else ""
        for w in (root.iterfind("g:wpt", ns) if ns["g"] else root.iterfind("wpt")):
            nm = f(w, "name"); de = f(w, "desc"); cm = f(w, "cmt"); tm = f(w, "time"); el = f(w, "ele")
            nombre = nm.text if nm is not None and nm.text else ""
            desc = " ".join(x.text for x in (de, cm) if x is not None and x.text and x.text != nombre)
            la, lo = float(w.get("lat")), float(w.get("lon"))
            cod, nuevo, suf, resto, alerta = normalizar(nombre)
            et = etiquetas(desc)
            # punto conocido más cercano
            cerca = min(((hav((la, lo), (p[2], p[3])), c) for c, p in conocidos.items() if p[2] is not None and c != normalizar(nombre)[0]), default=(None, None))
            final = cod
            if cod and not nuevo and cod not in conocidos:
                z, t, n_ = cod.split("-")
                if int(n_) not in usados.get((z, t), set()):
                    usados.setdefault((z, t), set()).add(int(n_))
                    conocidos[cod] = (cod, "(alta en este relevamiento)", la, lo)
                    alerta = (alerta + "; " if alerta else "") + "Alta nueva con el número escrito (se agrega al catálogo)"
                    filas.append([cod, nombre, "Nuevo", suf, resto, la, lo, float(el.text) if el is not None and el.text else None,
                                  tm.text if tm is not None else "", traza, ruta, et["H"], et["COM"], et["C"], et["A"], et["E"], et["R"], et["obs"],
                                  f"{cerca[1]} ({cerca[0]:.0f} m)" if cerca[0] is not None else "", alerta])
                    continue
                alerta = (alerta + "; " if alerta else "") + f"El número {n_} ya está usado en {z}-{t}: se asigna uno nuevo"; nuevo = True
            d_own = hav((la, lo), (conocidos[cod][2], conocidos[cod][3])) if cod in conocidos and conocidos[cod][2] is not None else None
            if cod and not nuevo and cerca[1] != cod and cerca[0] is not None and cerca[0] < MATCH_M and (d_own is None or cerca[0] < d_own):
                alerta = (alerta + "; " if alerta else "") + f"Está a {cerca[0]:.0f} m de {cerca[1]}: revisar si es el mismo punto"
            if cod and not nuevo and cod in conocidos and conocidos[cod][2] is not None:
                d = hav((la, lo), (conocidos[cod][2], conocidos[cod][3]))
                if d > 150: alerta = (alerta + "; " if alerta else "") + f"Queda a {d:.0f} m de la coordenada del catálogo: ¿corrección o punto distinto?"
            if cod and cod.startswith("P-") and not nuevo:
                z, t, _ = cod.split("-")
                alerta = (alerta + "; " if alerta else "") + "Punto P posicionado: asignar zona (O/E/N/L) o territorio (A../C..) al revisar"
            if cod and nuevo:
                z, t, _ = cod.split("-")
                if cerca[0] is not None and cerca[0] < MATCH_M:
                    alerta = (alerta + "; " if alerta else "") + f"Punto 'nuevo' a {cerca[0]:.0f} m de {cerca[1]}: ¿es el mismo?"
                k = max(usados.get((z, t), {0})) + 1; usados.setdefault((z, t), set()).add(k)
                final = f"{z}-{t}-{k:02d}"
            filas.append([final or "REVISAR", nombre, "Nuevo" if nuevo else ("Conocido" if cod else "—"), suf, resto, la, lo,
                          float(el.text) if el is not None and el.text else None, tm.text if tm is not None else "", traza, ruta, et["H"], et["COM"],
                          et["C"], et["A"], et["E"], et["R"], et["obs"],
                          f"{cerca[1]} ({cerca[0]:.0f} m)" if cerca[0] is not None else "", alerta])
    wb = Workbook(); ws = wb.active; ws.title = "Puntos_importados"
    hdr = ["Código final", "Nombre escrito en Wikiloc", "Tipo de registro", "Sufijo", "Texto del nombre", "Lat", "Lon", "Alt GPS (m)", "Hora (UTC)", "Traza", "Ruta", "Horario en el punto (H:)", "Señal (COM:)",
           "¿Dentro del campo?", "Acceso", "Estado", "Riesgo", "Observaciones", "Punto de catálogo más cercano", "Alertas"]
    for j, h in enumerate(hdr, 1):
        c = ws.cell(1, j, h); c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A2E"); c.alignment = Alignment(wrap_text=True)
    for i, r in enumerate(filas, 2):
        for j, v in enumerate(r, 1): ws.cell(i, j, v)
        if r[-1]: ws.cell(i, len(r)).fill = PatternFill("solid", fgColor="FCE4D6")
    for j, w in enumerate([12, 30, 10, 7, 24, 11, 11, 9, 20, 22, 12, 12, 14, 10, 9, 9, 24, 30, 22, 50], 1):
        ws.column_dimensions[ws.cell(1, j).column_letter].width = w
    wb.save(sys.argv[2])
    print(f"{len(filas)} puntos; con alertas: {sum(1 for r in filas if r[-1])}")
    for r in filas: print(f"{r[1][:30]:30s} → {r[0]:10s} {r[2]:8s} ruta={r[10]:12s} H={r[11]:12s} COM={r[12][:12]:12s} C={r[13]:5s} | {r[-1][:70]}")

if __name__ == "__main__":
    main()
