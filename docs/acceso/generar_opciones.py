"""Genera opciones.html: tres opciones del acceso, desarrolladas de punta a punta del frente.

Geometría según el croquis del dueño (de izquierda a derecha, vista desde la ruta):
M0 · 6 m · pilar de medidores 100x45x150 · tranquera 5,50 m · M1 · 6 · M2 · 6 · M3 · ala 2 m ·
portal (pilares 45x45x340, luz 3,80 m, retirado 1,50 m) · ala 2 m · M4 · 6 · M5 · 6 · M6 · 6 · M7 · 6 · M8.
Mojones 45x45x150. Desde la tranquera hasta el asfalto hay 20 m de banquina.
Uso: python3 docs/acceso/generar_opciones.py
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent

# ---------------- Geometría (metros, eje x a lo largo de la línea de cerca) ----------------
MOJONES = {"M0": 0.0, "M1": 12.0, "M2": 18.0, "M3": 24.0, "M4": 33.15, "M5": 39.15, "M6": 45.15, "M7": 51.15, "M8": 57.15}
MEDIDORES = (5.5, 6.5)
TRANQUERA = (6.5, 12.0)
HOJA_GRANDE = 9.9
P1, P2 = 26.45, 30.70
ALAS = ((24.45, 26.45), (31.15, 33.15))
TRAMOS = ((0.45, 5.5), (12.45, 18.0), (18.45, 24.0), (33.6, 39.15), (39.6, 45.15), (45.6, 51.15), (51.6, 57.15))
FIN = 57.6
RECESO = 1.5

PIEDRA_PINTADA = "#9a948a"
HORMIGON = "#8e908b"
GRIS_LINEA = "#4a4640"
MAD_NATURAL = "#9a5a36"
MAD_OSCURA = "#3e3029"
PORTON = "#2b2420"
VEGETAL = "#5f8a4a"

OPCIONES = {
    1: dict(
        nombre="Rural liviana",
        lema="El mojón manda: cerca baja y todo lo existente recuperado.",
        poste=0.10, h_poste=0.95, rieles=(0.40, 0.80), riel=0.10, color_cerca=MAD_NATURAL,
        zocalo=0.0, pilar_piedra=False, mojon_piedra=(), alas="cerca", porton="existente",
        cartel="tabla", luces=2, atrio="ripio", faja=0.5, mensulas=False,
        medidores="limpio", interno="1 travesaño",
        montaje="montajes/OP1_rural_liviana_F07.jpg",
        cerca=["9 mojones reparados y pintados en gris piedra (pintura mineral).",
               "7 tramos de cerca de postes escuadrados 4\"×4\" con punta y 2 travesaños pasantes; 0,95 m de alto libre.",
               "Se retira el alambrado; matas nativas aisladas del lado de adentro."],
        portal=["Pilares reparados y pintados en gris piedra; viga nueva de rollizo de 6 m.",
                "Tabla tallada colgada (2,0 × 0,5 m); portón existente reparado e impregnado oscuro en las dos caras.",
                "Alas de cerca igual al resto; atrio de ripio compactado; 2 luces solares bajo la viga.",
                "Sendero de ripio de 1,2 m hasta las cabañas."],
        vehicular=["Pilar de medidores: limpieza, sin revestimiento (el hormigón gris ya está en el tono).",
                   "Tranquera de 5,50 m restaurada: lijado, herrajes, impregnante oscuro en las dos caras y cintas reflectivas.",
                   "Placa «Ingreso · Recepción» en el mojón M1; de noche la ilumina la luminaria pública existente.",
                   "Cerco de soga del camino interno (≈ 50 m) cambiado por postes con 1 travesaño."],
        favor=["La más rápida y barata; casi todo con mano de obra propia.",
               "Los mojones de 1,50 m quedan como protagonistas sobre la cerca baja."],
        contra=["Con nieve alta la cerca de 0,95 m casi desaparece.",
                "El acceso vehicular cambia poco: sigue dominado por el pilar de medidores.",
                "No es la cerca de las fotos de referencia; no se convierte después en la opción 2."],
        nivel="$",
    ),
    2: dict(
        nombre="Patagónico natural",
        lema="La cerca de las fotos de referencia, con piedra solo en la base de los dos accesos.",
        poste=0.127, h_poste=1.15, rieles=(0.35, 0.65, 0.95), riel=0.127, color_cerca=MAD_NATURAL,
        zocalo=0.60, pilar_piedra=False, mojon_piedra=(), alas="cerca", porton="existente",
        cartel="tabla", luces=4, atrio="lajas", faja=0.8, mensulas=False,
        medidores="zocalo", interno="1 travesaño",
        montaje="montajes/OP2_patagonico_natural_F07.jpg",
        cerca=["9 mojones reparados y pintados en gris piedra.",
               "7 tramos de cerca de postes escuadrados 5\"×5\" con punta de diamante y 3 travesaños pasantes de 18'; 1,15 m de alto libre, madera natural rojiza.",
               "Se retira el alambrado; faja nativa continua de 0,8 m del lado de adentro."],
        portal=["Pilares en gris piedra con zócalo de piedra local de 0,60 m; viga nueva de rollizo de 6 m.",
                "Tabla tallada colgada (2,0 × 0,5 m) con «Buen viaje» del lado de adentro; portón existente reparado e impregnado oscuro.",
                "Alas con la misma cerca; atrio con piso de lajas de piedra local.",
                "4 luces solares (cartel y pilares); sendero de ripio con 8 balizas solares."],
        vehicular=["Pilar de medidores con el mismo zócalo de piedra de 0,60 m que el portal, recortado alrededor de las cajas.",
                   "Tranquera de 5,50 m restaurada, impregnante oscuro en las dos caras y cintas reflectivas.",
                   "Placa «Ingreso · Recepción» en M1, a juego con la tabla del portal.",
                   "Cerco interno de ≈ 50 m con los mismos postes de 5\"×5\" y 1 travesaño."],
        favor=["Es la cerca que elegiste en las referencias, de punta a punta.",
               "La piedra en la base del portal y de los medidores une los dos accesos con poca inversión.",
               "Buen equilibrio entre imagen, costo y trabajo propio."],
        contra=["Más madera para impregnar cada 2 o 3 años.",
                "Los zócalos y las lajas necesitan albañil o pircador."],
        nivel="$$",
    ),
    3: dict(
        nombre="Refugio de piedra",
        lema="Piedra en todo lo que marca los dos ingresos; madera oscura y metal negro.",
        poste=0.127, h_poste=1.15, rieles=(0.35, 0.65, 0.95), riel=0.127, color_cerca=MAD_OSCURA,
        zocalo=3.40, pilar_piedra=True, mojon_piedra=("M0", "M1", "M3", "M4"), alas="pirca", porton="nuevo",
        cartel="logo", luces=6, atrio="lajas", faja=1.2, mensulas=True,
        medidores="piedra", interno="2 travesaños",
        montaje="montajes/OP3_refugio_piedra_F07.jpg",
        cerca=["Mojones que flanquean los dos ingresos (M0, M1, M3 y M4) revestidos en piedra; los otros 5, en gris piedra.",
               "7 tramos de cerca de postes escuadrados 5\"×5\" con 3 travesaños, en madera oscura como los portones.",
               "Se retira el alambrado; faja nativa de 1,2 m del lado de adentro."],
        portal=["Pilares revestidos de piedra en toda la altura; viga nueva de rollizo de 6 m con ménsulas metálicas negras.",
                "Panel del logo existente colgado; portón peatonal nuevo de bastidor metálico negro y tablas verticales.",
                "Alas de pirca de piedra seca de 0,60 m en lugar de cerca; atrio de lajas.",
                "6 luces solares (incluye luz baja sobre las pircas); sendero con 8 balizas solares."],
        vehicular=["Pilar de medidores revestido en piedra, con las cajas libres y enmarcadas.",
                   "Tranquera restaurada en oscuro con herrajes negros.",
                   "Placa de metal negro con el logo en M1 y luz solar baja sobre la placa.",
                   "Cerco interno de ≈ 50 m con postes 5\"×5\" y 2 travesaños oscuros."],
        favor=["La imagen más fuerte; los dos ingresos quedan marcados con piedra.",
               "Dialoga con el pilar de piedra del vecino y se lee muy bien con nieve."],
        contra=["La más cara y la más lenta: pircador y herrero.",
                "Reemplaza el portón peatonal, que todavía sirve.",
                "Más riesgo de sobredimensionar el portal."],
        nivel="$$$",
    ),
}


# ---------------- Elevación (dos filas) ----------------
SE = 26          # px por metro en la elevación
XM = 30          # margen
SUELO = 128
FILAS = ((-0.6, 24.75, "Acceso vehicular y tramo izquierdo, M0 a M3"), (23.6, 58.2, "Portal peatonal y tramo derecho, M3 a M8"))
ANCHO_E = (58.2 - 23.6) * SE + 2 * XM


def ex(m):
    return XM + m * SE


def ey(h):
    return SUELO - h * SE


def defs(k):
    return f'''<defs>
  <pattern id="piedra{k}" width="16" height="11" patternUnits="userSpaceOnUse">
    <rect width="16" height="11" fill="#8d877c"/>
    <rect x="1" y="1" width="9" height="4.2" rx="1.5" fill="#a59f94"/><rect x="11" y="1" width="4" height="4.2" rx="1.5" fill="#7f796f"/>
    <rect x="1" y="6" width="4.5" height="4.2" rx="1.5" fill="#968f84"/><rect x="6.5" y="6" width="8.5" height="4.2" rx="1.5" fill="#aaa498"/>
  </pattern>
  <pattern id="lajas{k}" width="20" height="14" patternUnits="userSpaceOnUse">
    <rect width="20" height="14" fill="#7d776d"/><polygon points="1,1 11,1 9,7 1,6" fill="#a8a296"/>
    <polygon points="12,1 19,1 19,8 10,7" fill="#99938a"/><polygon points="1,7 9,8 10,13 1,13" fill="#9f998e"/>
    <polygon points="11,8 19,9 19,13 11,13" fill="#b0aa9e"/>
  </pattern>
  <pattern id="ripio{k}" width="6" height="6" patternUnits="userSpaceOnUse">
    <rect width="6" height="6" fill="#c9bda6"/><circle cx="1.5" cy="1.5" r=".9" fill="#9d917b"/><circle cx="4.5" cy="4" r=".8" fill="#8f846f"/>
  </pattern>
</defs>'''


def e_mojon(nombre, k, o):
    x = MOJONES[nombre]
    piedra = nombre in o["mojon_piedra"]
    fill = f"url(#piedra{k})" if piedra else PIEDRA_PINTADA
    x0, x1, xm = ex(x), ex(x + 0.45), ex(x + 0.225)
    return [f'<polygon points="{x0},{ey(0)} {x0},{ey(1.28)} {xm},{ey(1.5)} {x1},{ey(1.28)} {x1},{ey(0)}" fill="{fill}" stroke="{GRIS_LINEA}" stroke-width="1"/>',
            f'<text x="{ex(x + 0.225)}" y="{SUELO + 14}" text-anchor="middle" font-size="10" fill="var(--muted)">{nombre}</text>']


def e_cerca(a, b, o, receso=False):
    out, op = [], (' opacity=".75"' if receso else "")
    w = max(2.5, o["poste"] * SE)
    n = max(1, round((b - a) / 2.75))
    for h in o["rieles"]:
        out.append(f'<rect x="{ex(a)}" y="{ey(h) - o["riel"] * SE / 2:.1f}" width="{(b - a) * SE:.1f}" height="{max(2, o["riel"] * SE):.1f}" fill="{o["color_cerca"]}"{op}/>')
    for i in range(n + 1):
        cx = ex(a + 0.08 + (b - a - 0.16) * i / n)
        ht = ey(o["h_poste"])
        out.append(f'<polygon points="{cx - w / 2:.1f},{ey(0)} {cx - w / 2:.1f},{ht:.1f} {cx:.1f},{ht - w * 0.7:.1f} {cx + w / 2:.1f},{ht:.1f} {cx + w / 2:.1f},{ey(0)}" fill="{o["color_cerca"]}"{op}/>')
    return out


def e_plantas(a, b, o):
    out, x = [], a + 0.4
    paso = 0.9 if o["faja"] >= 0.8 else 2.4
    while x < b - 0.3:
        r = 4 + (int(x * 7) % 4)
        out.append(f'<ellipse cx="{ex(x):.1f}" cy="{SUELO - r * 0.6:.1f}" rx="{r + 2}" ry="{r}" fill="{VEGETAL}" opacity=".7"/>')
        x += paso
    return out


def e_medidores(k, o):
    a, b = MEDIDORES
    x0, x1 = ex(a), ex(b)
    out = []
    base = f"url(#piedra{k})" if o["medidores"] == "piedra" else HORMIGON
    out.append(f'<path d="M{x0} {ey(0)} L{x0} {ey(1.38)} Q{x0} {ey(1.5)} {x0 + 6} {ey(1.5)} L{x1 - 6} {ey(1.5)} Q{x1} {ey(1.5)} {x1} {ey(1.38)} L{x1} {ey(0)} Z" fill="{base}" stroke="{GRIS_LINEA}"/>')
    if o["medidores"] == "zocalo":
        out.append(f'<rect x="{x0}" y="{ey(0.6)}" width="{x1 - x0}" height="{0.6 * SE}" fill="url(#piedra{k})" stroke="{GRIS_LINEA}"/>')
    marco = ' stroke="#111" stroke-width="2"' if o["medidores"] == "piedra" else ' stroke="#555" stroke-width=".8"'
    for cx in (a + 0.28, b - 0.28):
        out.append(f'<rect x="{ex(cx - 0.13):.1f}" y="{ey(1.25)}" width="{0.26 * SE:.1f}" height="{0.3 * SE:.1f}" fill="#d9dcd6"{marco}/>')
        out.append(f'<rect x="{ex(cx - 0.12):.1f}" y="{ey(0.62)}" width="{0.24 * SE:.1f}" height="{0.22 * SE:.1f}" fill="#f2f2f0"{marco}/>')
    out.append(f'<text x="{ex(6.0)}" y="{SUELO + 14}" text-anchor="middle" font-size="10" fill="var(--muted)">medidores</text>')
    return out


def e_tranquera(o):
    out = []
    for (a, b) in ((TRANQUERA[0] + 0.05, HOJA_GRANDE), (HOJA_GRANDE + 0.04, TRANQUERA[1] - 0.05)):
        x0, x1 = ex(a), ex(b)
        for h in (0.12, 0.42, 0.72, 1.02, 1.3):
            out.append(f'<rect x="{x0}" y="{ey(h) - 2}" width="{x1 - x0}" height="4" fill="{PORTON}"/>')
        for x in (x0, (x0 + x1) / 2 - 2, x1 - 4):
            out.append(f'<rect x="{x}" y="{ey(1.32)}" width="4" height="{1.32 * SE}" fill="{PORTON}"/>')
        out.append(f'<line x1="{x0 + 3}" y1="{ey(0.1)}" x2="{(x0 + x1) / 2}" y2="{ey(1.3)}" stroke="{PORTON}" stroke-width="3.5"/>')
        out.append(f'<line x1="{x1 - 3}" y1="{ey(0.1)}" x2="{(x0 + x1) / 2}" y2="{ey(1.3)}" stroke="{PORTON}" stroke-width="3.5"/>')
        if o["medidores"] != "piedra":
            out.append(f'<rect x="{x1 - 14}" y="{ey(0.8)}" width="9" height="4" fill="#f0a020"/>')
    out.append(f'<text x="{ex(9.25)}" y="{SUELO + 14}" text-anchor="middle" font-size="10" fill="var(--muted)">tranquera</text>')
    return out


def e_placa(o):
    x = MOJONES["M1"]
    col = "#111" if o["medidores"] == "piedra" else "#2a2420"
    return [f'<rect x="{ex(x + 0.03)}" y="{ey(1.12)}" width="{0.39 * SE:.1f}" height="{0.3 * SE:.1f}" fill="{col}" stroke="#c9a96a" stroke-width=".8"/>',
            f'<text x="{ex(x + 0.225)}" y="{ey(0.95)}" text-anchor="middle" font-size="4.5" fill="#e2cda0">INGRESO</text>']


def e_portal(k, o):
    out = []
    for x in (P1, P2):
        x0, x1, xm = ex(x), ex(x + 0.45), ex(x + 0.225)
        base = f"url(#piedra{k})" if o["pilar_piedra"] else PIEDRA_PINTADA
        out.append(f'<polygon points="{x0},{ey(0)} {x0},{ey(3.15)} {xm},{ey(3.4)} {x1},{ey(3.15)} {x1},{ey(0)}" fill="{base}" stroke="{GRIS_LINEA}"/>')
        if o["zocalo"] and not o["pilar_piedra"]:
            out.append(f'<rect x="{x0}" y="{ey(o["zocalo"])}" width="{x1 - x0}" height="{o["zocalo"] * SE}" fill="url(#piedra{k})" stroke="{GRIS_LINEA}"/>')
    g0, g1 = ex(P1 + 0.45), ex(P2)
    if o["porton"] == "existente":
        mid = ex(P1 + 0.45 + 1.4)
        for h in (0.15, 0.45, 0.75, 1.05, 1.35):
            out.append(f'<rect x="{g0 + 1}" y="{ey(h) - 2}" width="{g1 - g0 - 2}" height="4" fill="{PORTON}"/>')
        for x in (g0 + 1, mid - 2, mid + 2, g1 - 4):
            out.append(f'<rect x="{x}" y="{ey(1.4)}" width="3.5" height="{1.4 * SE}" fill="{PORTON}"/>')
        out.append(f'<line x1="{g0 + 3}" y1="{ey(0.1)}" x2="{mid - 3}" y2="{ey(1.35)}" stroke="{PORTON}" stroke-width="3.5"/>')
    else:
        out.append(f'<rect x="{g0 + 1}" y="{ey(1.45)}" width="{g1 - g0 - 2}" height="{1.4 * SE}" fill="#1c1c1c"/>')
        x = g0 + 4
        while x < g1 - 7:
            out.append(f'<rect x="{x:.1f}" y="{ey(1.38)}" width="4.5" height="{1.28 * SE:.1f}" fill="#7a5235"/>')
            x += 6.5
    v0, v1 = ex(P1 - 0.65), ex(P2 + 1.1)
    out.append(f'<rect x="{v0}" y="{ey(2.99)}" width="{v1 - v0}" height="{0.28 * SE}" rx="{0.14 * SE}" fill="#8b6240" stroke="#5a3d27"/>')
    if o["mensulas"]:
        for x in (g0, g1 - 11):
            out.append(f'<polygon points="{x},{ey(2.71)} {x + 11},{ey(2.71)} {x},{ey(2.71) + 11}" fill="#111"/>')
    cx = (g0 + g1) / 2
    if o["cartel"] == "tabla":
        w, h, top = 2.0 * SE, 0.5 * SE, ey(2.55)
        out += [f'<line x1="{cx - w / 3}" y1="{ey(2.71)}" x2="{cx - w / 3}" y2="{top}" stroke="#222"/><line x1="{cx + w / 3}" y1="{ey(2.71)}" x2="{cx + w / 3}" y2="{top}" stroke="#222"/>',
                f'<rect x="{cx - w / 2}" y="{top}" width="{w}" height="{h}" rx="2" fill="#4a3324"/>',
                f'<text x="{cx}" y="{top + h * 0.66}" text-anchor="middle" font-size="7" font-weight="700" fill="#e2cda0" font-family="Georgia,serif" textLength="{w * 0.86:.0f}" lengthAdjust="spacingAndGlyphs">TIERRAS MÁGICAS</text>']
    else:
        w, top = 0.85 * SE, ey(2.6)
        out += [f'<line x1="{cx - w / 3}" y1="{ey(2.71)}" x2="{cx - w / 3}" y2="{top}" stroke="#222"/><line x1="{cx + w / 3}" y1="{ey(2.71)}" x2="{cx + w / 3}" y2="{top}" stroke="#222"/>',
                f'<rect x="{cx - w / 2 - 3}" y="{top - 3}" width="{w + 6}" height="{w + 6}" fill="#5a3d27"/><rect x="{cx - w / 2}" y="{top}" width="{w}" height="{w}" fill="#1f3326"/>',
                f'<polygon points="{cx - 8},{top + 12} {cx - 2},{top + 5} {cx + 3},{top + 10} {cx + 7},{top + 6} {cx + 10},{top + 12}" fill="none" stroke="#d8b878" stroke-width="1"/>']
    out.append(f'<text x="{cx}" y="{SUELO + 14}" text-anchor="middle" font-size="10" fill="var(--muted)">portal peatonal</text>')
    return out


def e_luces(o):
    pts = [(ex(P1 + 1.4), ey(2.71)), (ex(P2 - 0.95), ey(2.71))]
    if o["luces"] >= 4:
        pts += [(ex(P1 + 0.225), ey(2.2)), (ex(P2 + 0.225), ey(2.2))]
    if o["luces"] >= 6:
        pts += [(ex(25.4), ey(0.75)), (ex(32.2), ey(0.75)), (ex(MOJONES["M1"] + 0.225), ey(1.4))]
    return [f'<polygon points="{x},{y} {x - 9},{y + 22} {x + 9},{y + 22}" fill="#f2c46b" opacity=".3"/><circle cx="{x}" cy="{y}" r="2.6" fill="#e0a43a"/>' for x, y in pts]


def e_luminaria_publica():
    x = ex(4.6)
    return [f'<line x1="{x}" y1="{ey(0)}" x2="{x}" y2="{ey(4.3)}" stroke="#666" stroke-width="3"/>',
            f'<line x1="{x}" y1="{ey(4.3)}" x2="{x + 22}" y2="{ey(4.3)}" stroke="#666" stroke-width="2"/><rect x="{x + 18}" y="{ey(4.3)}" width="10" height="3" fill="#ddd"/>',
            f'<text x="{x - 4}" y="{ey(4.0)}" text-anchor="end" font-size="9" fill="var(--muted)">luminaria pública existente</text>']


def e_cota(a, b, y, txt):
    return (f'<line x1="{ex(a)}" y1="{y}" x2="{ex(b)}" y2="{y}" stroke="var(--muted)" stroke-width=".8"/>'
            f'<line x1="{ex(a)}" y1="{y - 3}" x2="{ex(a)}" y2="{y + 3}" stroke="var(--muted)"/><line x1="{ex(b)}" y1="{y - 3}" x2="{ex(b)}" y2="{y + 3}" stroke="var(--muted)"/>'
            f'<text x="{(ex(a) + ex(b)) / 2}" y="{y - 3}" text-anchor="middle" font-size="9.5" fill="var(--muted)">{txt}</text>')


def elevacion_completa(k, o):
    g = []
    g.append(f'<rect x="{ex(-2)}" y="{SUELO}" width="{62 * SE}" height="10" fill="#b9ad94"/>')
    for a, b in TRAMOS:
        g += e_plantas(a, b, o)
    for a, b in TRAMOS:
        g += e_cerca(a, b, o)
    for a, b in ALAS:
        if o["alas"] == "cerca":
            g += e_cerca(a, b, o, receso=True)
        else:
            g.append(f'<rect x="{ex(a)}" y="{ey(0.6)}" width="{(b - a) * SE}" height="{0.6 * SE}" fill="url(#piedra{k})" stroke="{GRIS_LINEA}"/>')
    g += e_luminaria_publica()
    g += e_medidores(k, o)
    g += e_tranquera(o)
    for n in MOJONES:
        g += e_mojon(n, k, o)
    g += e_placa(o)
    g += e_portal(k, o)
    g += e_luces(o)
    yc = SUELO + 32
    for (a, b) in TRAMOS:
        g.append(e_cota(a - (0.225 if a > 1 else 0.225), b + 0.225, yc, "6,00"))
    g.append(e_cota(*MEDIDORES, yc + 16, "1,00"))
    g.append(e_cota(*TRANQUERA, yc + 16, "5,50"))
    for a, b in ALAS:
        g.append(e_cota(a, b, yc + 16, "2,00"))
    g.append(e_cota(P1 + 0.45, P2, yc + 16, "3,80"))
    g.append(f'<line x1="{ex(P2 + 0.8)}" y1="{ey(0)}" x2="{ex(P2 + 0.8)}" y2="{ey(3.4)}" stroke="var(--muted)" stroke-width=".8"/><text x="{ex(P2 + 0.9)}" y="{ey(3.2)}" font-size="9.5" fill="var(--muted)">3,40</text>')
    g.append(f'<line x1="{ex(MOJONES["M2"] + 0.8)}" y1="{ey(0)}" x2="{ex(MOJONES["M2"] + 0.8)}" y2="{ey(1.5)}" stroke="var(--muted)" stroke-width=".8"/><text x="{ex(MOJONES["M2"] + 0.9)}" y="{ey(1.35)}" font-size="9.5" fill="var(--muted)">1,50</text>')
    alto = f'{o["h_poste"]:.2f}'.replace(".", ",")
    g.append(f'<text x="{ex(13.0)}" y="{ey(o["h_poste"]) - 6:.1f}" font-size="9.5" fill="var(--fg)">cerca {alto} m</text>')
    cuerpo = "\n".join(g)
    alto_svg = SUELO + 66
    filas = []
    for i, (a, b, titulo) in enumerate(FILAS):
        filas.append(
            f'<svg viewBox="0 0 {ANCHO_E:.0f} {alto_svg}" role="img" aria-label="Elevación completa desde la ruta, opción {k}, parte {i + 1}">{defs(k) if i == 0 else ""}'
            f'<rect width="{ANCHO_E:.0f}" height="{alto_svg}" fill="var(--surface)"/>'
            f'<clipPath id="clip{k}{i}"><rect x="0" y="0" width="{(b - a) * SE + 2 * XM:.0f}" height="{alto_svg}"/></clipPath>'
            f'<g clip-path="url(#clip{k}{i})"><g transform="translate({-a * SE:.1f},0)">{cuerpo}</g></g>'
            f'<text x="{ANCHO_E - 8:.0f}" y="16" text-anchor="end" font-size="11" font-weight="600" fill="var(--bosque)">{i + 1}/2 · {titulo}</text></svg>')
    return "\n".join(filas)


# ---------------- Planta completa ----------------
SP = 15
PX0 = 24
YF = 140         # línea de cerca
BANQ = 20.0      # m de banquina hasta el asfalto
ANCHO_P = (FIN + 1.6) * SP + 2 * PX0


def px(m):
    return PX0 + (m + 0.8) * SP


def py(d):
    """d > 0 hacia la ruta, d < 0 hacia adentro del lote (metros)."""
    return YF + d * SP


def planta_completa(k, o):
    g = [f'<rect width="{ANCHO_P:.0f}" height="{py(BANQ) + 76:.0f}" fill="var(--surface)"/>']
    # banquina, cuneta y ruta
    g.append(f'<rect x="0" y="{YF + 6}" width="{ANCHO_P:.0f}" height="{BANQ * SP - 6}" fill="#e3d9c2" opacity=".55"/>')
    g.append(f'<rect x="0" y="{py(BANQ - 4)}" width="{ANCHO_P:.0f}" height="{4 * SP}" fill="#ffffff" opacity=".45"/>')
    g.append(f'<text x="{px(36)}" y="{py(BANQ - 1.6)}" font-size="11" fill="var(--muted)">franja libre para el acopio de nieve de la máquina vial</text>')
    g.append(f'<line x1="0" y1="{py(BANQ)}" x2="{ANCHO_P:.0f}" y2="{py(BANQ)}" stroke="var(--bosque)" stroke-width="3" stroke-dasharray="9 5"/>')
    g.append(f'<text x="8" y="{py(BANQ) - 5}" font-size="11" fill="var(--bosque)">cuneta (constructora vial)</text>')
    g.append(f'<rect x="0" y="{py(BANQ) + 8}" width="{ANCHO_P:.0f}" height="58" fill="#8d8a84" opacity=".5"/>')
    g.append(f'<text x="{ANCHO_P / 2:.0f}" y="{py(BANQ) + 42}" text-anchor="middle" font-size="13" fill="var(--fg)">RUTA PROVINCIAL 11 · asfalto +0,50 m</text>')
    # acceso vehicular sobre la banquina
    a, b = TRANQUERA
    g.append(f'<rect x="{px(a)}" y="{YF + 6}" width="{(b - a) * SP}" height="{BANQ * SP - 6}" fill="url(#ripio{k})"/>')
    g.append(f'<rect x="{px(a) - 6}" y="{py(BANQ) - 7}" width="{(b - a) * SP + 12}" height="14" fill="none" stroke="var(--fg)" stroke-width="2"/>')
    g.append(f'<text x="{px(b) + 6}" y="{py(BANQ) + 4}" font-size="11" fill="var(--fg)">alcantarilla</text>')
    g.append(f'<text x="{px(a) + 6}" y="{py(9)}" font-size="11" fill="var(--fg)" transform="rotate(-90 {px(a) + 6} {py(9)})">acceso 20 m · 2,5 %</text>')
    # estacionamiento invernal: módulos de 2,5 x 5 a 1,5 m de la cerca, dejando senda peatonal
    for x0, x1 in ((12.6, 23.8), (33.8, 46.3)):
        x = x0
        while x + 2.5 <= x1:
            g.append(f'<rect x="{px(x)}" y="{py(1.5)}" width="{2.5 * SP}" height="{5 * SP}" fill="none" stroke="#7b725f" stroke-dasharray="3 3"/>')
            x += 2.5
    g.append(f'<text x="{px(13)}" y="{py(7.6)}" font-size="11" fill="var(--muted)">estacionamiento invernal (a acordar con la constructora)</text>')
    g.append(f'<line x1="{px(12.5)}" y1="{py(0.75)}" x2="{px(24.4)}" y2="{py(0.75)}" stroke="#b09f7e" stroke-width="6" opacity=".7"/><line x1="{px(33.2)}" y1="{py(0.75)}" x2="{px(46.4)}" y2="{py(0.75)}" stroke="#b09f7e" stroke-width="6" opacity=".7"/>')
    g.append(f'<text x="{px(47)}" y="{py(0.75) + 4}" font-size="10" fill="var(--muted)">senda peatonal 1,5 m hacia el atrio</text>')
    # interior: faja, camino interno, sendero
    fw = o["faja"] * SP
    for a2, b2 in TRAMOS:
        g.append(f'<rect x="{px(a2)}" y="{YF - fw - 3}" width="{(b2 - a2) * SP}" height="{fw}" fill="{VEGETAL}" opacity=".35"/>')
    g.append(f'<path d="M{px(9.25)} {YF} C{px(9.25)} {YF - 50} {px(8)} {YF - 90} {px(5)} 8" stroke="#b5a585" stroke-width="{5.5 * SP * 0.6:.0f}" fill="none" opacity=".45"/>')
    g.append(f'<path d="M{px(12.2)} {YF - 6} C{px(12.2)} {YF - 50} {px(11)} {YF - 95} {px(8.2)} 8" stroke="{o["color_cerca"]}" stroke-width="2.5" fill="none"/>')
    g.append(f'<text x="{px(12.6)}" y="{YF - 70}" font-size="11" fill="var(--fg)">camino interno · cerco ≈ 50 m ({o["interno"]})</text>')
    mid = (P1 + 0.45 + P2) / 2
    g.append(f'<path d="M{px(mid)} {py(-RECESO) - 4} C{px(mid)} {YF - 70} {px(mid + 2)} {YF - 100} {px(mid + 5)} 8" stroke="#b5a585" stroke-width="{1.2 * SP:.0f}" fill="none" opacity=".6"/>')
    for i in range(1, 8):
        t = i / 8
        x = px(mid) + (px(mid + 5) - px(mid)) * t * t
        y = (py(-RECESO) - 4) + (8 - (py(-RECESO) - 4)) * t
        g.append(f'<circle cx="{x + 12:.1f}" cy="{y:.1f}" r="2.2" fill="#e0a43a"/>')
    g.append(f'<text x="{px(mid + 3)}" y="{YF - 60}" font-size="11" fill="var(--fg)">sendero 1,2 m · balizas solares</text>')
    g.append(f'<text x="{px(42)}" y="20" font-size="11" fill="var(--muted)">hacia cabañas, quincho y tina</text>')
    # atrio
    atr = {"ripio": f"url(#ripio{k})", "lajas": f"url(#lajas{k})"}[o["atrio"]]
    g.append(f'<polygon points="{px(ALAS[0][0])},{YF} {px(P1)},{py(-RECESO)} {px(P2 + 0.45)},{py(-RECESO)} {px(ALAS[1][1])},{YF}" fill="{atr}"/>')
    g.append(f'<text x="{px(mid)}" y="{YF - 6}" text-anchor="middle" font-size="10" fill="var(--fg)">atrio</text>')
    # cerca
    col = o["color_cerca"]
    for a2, b2 in TRAMOS:
        g.append(f'<line x1="{px(a2)}" y1="{YF}" x2="{px(b2)}" y2="{YF}" stroke="{col}" stroke-width="4"/>')
        for i in range(3):
            x = a2 + 0.08 + (b2 - a2 - 0.16) * i / 2
            g.append(f'<rect x="{px(x) - 2.5}" y="{YF - 2.5}" width="5" height="5" fill="{col}"/>')
    for (a2, b2), sentido in zip(ALAS, (1, -1)):
        y1, y2 = (YF, py(-RECESO)) if sentido == 1 else (py(-RECESO), YF)
        if o["alas"] == "cerca":
            g.append(f'<line x1="{px(a2)}" y1="{y1}" x2="{px(b2)}" y2="{y2}" stroke="{col}" stroke-width="4"/>')
        else:
            g.append(f'<line x1="{px(a2)}" y1="{y1}" x2="{px(b2)}" y2="{y2}" stroke="#8d877c" stroke-width="9"/>')
    # mojones, medidores, pilares, tranquera, portón
    for n, x in MOJONES.items():
        fill = f"url(#piedra{k})" if n in o["mojon_piedra"] else PIEDRA_PINTADA
        g.append(f'<rect x="{px(x)}" y="{YF + 1}" width="{0.45 * SP + 1:.1f}" height="{0.45 * SP + 1:.1f}" fill="{fill}" stroke="{GRIS_LINEA}"/>')
        g.append(f'<text x="{px(x + 0.22)}" y="{YF + 22}" text-anchor="middle" font-size="9.5" fill="var(--muted)">{n}</text>')
    mf = {"limpio": HORMIGON, "zocalo": HORMIGON, "piedra": f"url(#piedra{k})"}[o["medidores"]]
    g.append(f'<rect x="{px(MEDIDORES[0])}" y="{YF - 3}" width="{1.0 * SP}" height="{0.45 * SP + 1:.1f}" fill="{mf}" stroke="{GRIS_LINEA}"/>')
    g.append(f'<text x="{px(6.0)}" y="{YF + 34}" text-anchor="middle" font-size="9.5" fill="var(--muted)">medidores</text>')
    r1 = (HOJA_GRANDE - TRANQUERA[0]) * SP
    r2 = (TRANQUERA[1] - HOJA_GRANDE) * SP
    g.append(f'<path d="M{px(TRANQUERA[0])} {YF} A{r1} {r1} 0 0 1 {px(TRANQUERA[0]) + r1 * 0.7:.1f} {YF - r1 * 0.7:.1f}" fill="none" stroke="var(--muted)" stroke-dasharray="3 3"/>')
    g.append(f'<path d="M{px(TRANQUERA[1])} {YF} A{r2} {r2} 0 0 0 {px(TRANQUERA[1]) - r2 * 0.7:.1f} {YF - r2 * 0.7:.1f}" fill="none" stroke="var(--muted)" stroke-dasharray="3 3"/>')
    g.append(f'<line x1="{px(TRANQUERA[0])}" y1="{YF}" x2="{px(TRANQUERA[1])}" y2="{YF}" stroke="{PORTON}" stroke-width="4"/>')
    for x in (P1, P2):
        fill = f"url(#piedra{k})" if (o["pilar_piedra"] or o["zocalo"]) else PIEDRA_PINTADA
        g.append(f'<rect x="{px(x)}" y="{py(-RECESO) - 3.5}" width="{0.45 * SP + 1:.1f}" height="{0.45 * SP + 1:.1f}" fill="{fill}" stroke="{GRIS_LINEA}"/>')
    g.append(f'<line x1="{px(P1 + 0.45)}" y1="{py(-RECESO)}" x2="{px(P2)}" y2="{py(-RECESO)}" stroke="{PORTON}" stroke-width="3" stroke-dasharray="5 2"/>')
    # cotas generales
    yc = py(BANQ) + 70
    g.append(f'<text x="{px(0)}" y="{YF - 112}" font-size="11" fill="var(--muted)">interior del lote</text>')
    g.append(f'<line x1="{px(-0.5)}" y1="{YF}" x2="{px(-0.5)}" y2="{py(BANQ)}" stroke="var(--muted)" stroke-width=".8"/><text x="{px(-0.3)}" y="{py(10)}" font-size="10" fill="var(--muted)">20,00</text>')
    return f'<svg viewBox="0 0 {ANCHO_P:.0f} {py(BANQ) + 76:.0f}" role="img" aria-label="Planta completa del frente, opción {k}">' + "\n".join(g) + "</svg>"


CRITERIOS = [
    ("imagen", "Imagen e identidad patagónica", 25, (3, 4, 5)),
    ("nieve", "Se lee bien con nieve", 15, (3, 4, 5)),
    ("costo", "Inversión controlada", 20, (5, 4, 2)),
    ("mant", "Mantenimiento bajo", 15, (4, 4, 3)),
    ("propia", "Ejecución con mano de obra propia y en plazo", 15, (5, 4, 2)),
    ("reuso", "Reutiliza lo existente", 10, (5, 5, 3)),
]

CANTIDADES = [
    ("Mojones (9)", "9 en gris piedra", "9 en gris piedra", "4 en piedra + 5 en gris piedra"),
    ("Postes escuadrados del frente", "25 de 4\"×4\" × 1,60 m", "25 de 5\"×5\" × 1,85 m", "21 de 5\"×5\" × 1,85 m"),
    ("Travesaños del frente", "14 de 18' + 4 de 10'", "21 de 18' + 6 de 10'", "21 de 18'"),
    ("Cerco del camino interno (≈ 50 m)", "1 travesaño", "1 travesaño, postes 5\"×5\"", "2 travesaños oscuros"),
    ("Piedra en pilares, mojones y medidores", "—", "≈ 3,9 m² (zócalos)", "≈ 33 m²"),
    ("Pircas en las alas", "—", "—", "2 × 2,5 m × 0,60 m"),
    ("Atrio (≈ 5,7 m²)", "ripio", "lajas", "lajas"),
    ("Portón peatonal", "se repara", "se repara", "nuevo, metal + madera"),
    ("Tranquera vehicular", "se restaura", "se restaura", "se restaura, herrajes negros"),
    ("Pilar de medidores", "limpieza", "zócalo de piedra 0,60 m", "revestido en piedra"),
    ("Cartel y placa", "tabla + placa en M1", "tabla + placa en M1", "panel del logo + placa metálica en M1"),
    ("Luces solares", "2", "4 + 8 balizas de sendero", "7 + 8 balizas de sendero"),
    ("Oficios", "propio", "propio + pircador (≈ 6 jornales)", "propio + pircador (≈ 18 jornales) + herrero"),
    ("Inversión relativa", "$", "$$", "$$$"),
]


def tarjeta(k, o):
    def lista(xs):
        return "".join(f"<li>{t}</li>" for t in xs)
    return f'''
<section class="opcion" id="opcion-{k}">
  <header class="op-cab">
    <span class="op-num">Opción {k}</span>
    <h2>{o["nombre"]}</h2>
    <span class="nivel" title="Inversión relativa">{o["nivel"]}</span>
  </header>
  <p class="lema">{o["lema"]}</p>
  <figure class="foto"><img src="{o["montaje"]}" alt="Fotomontaje de la opción {k} sobre la foto del portal"><figcaption>Fotomontaje ilustrativo del portal (foto F07).</figcaption></figure>
  <h3>Elevación completa desde la ruta, de M0 a M8</h3>
  <div class="diag">{elevacion_completa(k, o)}</div>
  <h3>Planta completa del frente</h3>
  <div class="diag">{planta_completa(k, o)}</div>
  <div class="cols3">
    <div><h3>Cerca</h3><ul>{lista(o["cerca"])}</ul></div>
    <div><h3>Portal peatonal</h3><ul>{lista(o["portal"])}</ul></div>
    <div><h3>Acceso vehicular</h3><ul>{lista(o["vehicular"])}</ul></div>
  </div>
  <div class="cols">
    <div><h3>A favor</h3><ul class="mas">{lista(o["favor"])}</ul></div>
    <div><h3>En contra</h3><ul class="menos">{lista(o["contra"])}</ul></div>
  </div>
</section>'''


def pagina():
    filas_c = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in CANTIDADES)
    filas_m = "".join(
        f'<tr><td><label for="peso-{cid}">{txt}</label></td>'
        f'<td><input type="range" id="peso-{cid}" min="0" max="40" step="5" value="{peso}" data-puntos="{",".join(map(str, pts))}"> <output id="out-{cid}">{peso}</output></td>'
        + "".join(f'<td class="num">{p}</td>' for p in pts) + "</tr>"
        for cid, txt, peso, pts in CRITERIOS)
    tarjetas = "".join(tarjeta(k, o) for k, o in OPCIONES.items())
    return f'''<title>Opciones del acceso</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;800&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@500&display=swap">
<style>
/* Layout: una columna de 1080 px; cada opción es una lámina con foto, elevación completa, planta completa y fichas */
:root{{
  --bg:#f3f4f1; --surface:#ffffff; --fg:#1d2420; --muted:#5b655e; --line:#d5dad3; --chip:#e6eae3;
  --bosque:#1f3326; --lenga:#a8622a; --ok:#2f6b3a; --bad:#a3352b;
  --f-display:"Archivo",system-ui,sans-serif; --f-body:"Source Sans 3",system-ui,sans-serif; --f-mono:"JetBrains Mono",ui-monospace,monospace;
  color-scheme:light;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#141a16;--surface:#1c241f;--fg:#e7ebe5;--muted:#a3ada5;--line:#334038;--chip:#26312a;--bosque:#9cc5a6;--lenga:#e0995a;--ok:#7cc48a;--bad:#ec8a7f;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#141a16;--surface:#1c241f;--fg:#e7ebe5;--muted:#a3ada5;--line:#334038;--chip:#26312a;--bosque:#9cc5a6;--lenga:#e0995a;--ok:#7cc48a;--bad:#ec8a7f;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font:17px/1.55 var(--f-body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 64px}}
.wrap{{max-width:1080px;margin:0 auto;display:grid;gap:28px}}
header.portada{{padding-block:36px 8px;border-bottom:3px solid var(--bosque);display:grid;gap:8px}}
.eyebrow{{font:500 12px var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--lenga)}}
h1{{font:800 clamp(28px,5vw,44px)/1.05 var(--f-display);margin:0;color:var(--bosque);text-wrap:balance}}
h2{{font:800 28px/1.1 var(--f-display);margin:0;color:var(--bosque)}}
h3{{font:600 15px var(--f-display);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:18px 0 6px}}
p,li{{max-width:72ch}}
.lead{{font-size:19px;color:var(--muted);margin:0}}
.fijo{{background:var(--surface);border:1px solid var(--line);padding:14px 18px}}
.fijo ul{{margin:6px 0 0;padding-left:18px}}
nav.saltos{{display:flex;flex-wrap:wrap;gap:8px}}
nav.saltos a{{font-weight:600;color:var(--fg);background:var(--chip);padding:6px 12px;border-radius:4px;text-decoration:none}}
nav.saltos a:hover,nav.saltos a:focus-visible{{background:var(--bosque);color:var(--bg);outline:none}}
.opcion{{background:var(--surface);border:1px solid var(--line);padding:20px 22px}}
.op-cab{{display:flex;flex-wrap:wrap;align-items:baseline;gap:12px}}
.op-num{{font:500 13px var(--f-mono);color:var(--lenga);text-transform:uppercase;letter-spacing:.1em}}
.nivel{{margin-left:auto;font:600 18px var(--f-mono);color:var(--lenga)}}
.lema{{margin:4px 0 12px;font-size:18px}}
figure{{margin:0}} figure img{{display:block;width:100%;height:auto;border:1px solid var(--line)}}
figcaption{{font-size:13px;color:var(--muted);padding-top:4px}}
.diag{{overflow-x:auto;border:1px solid var(--line);display:grid;gap:0}}
.diag svg{{display:block;width:100%;min-width:760px;height:auto}}
.diag svg+svg{{border-top:1px dashed var(--line)}}
svg text{{font-family:var(--f-body)}}
.cols,.cols3{{display:grid;gap:8px 28px}}
.cols{{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}}
.cols3{{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}}
.cols>div,.cols3>div{{min-width:0}}
ul{{padding-left:18px;margin:4px 0}}
ul.mas li::marker{{content:"+  ";color:var(--ok);font-weight:700}}
ul.menos li::marker{{content:"−  ";color:var(--bad);font-weight:700}}
.tabla{{overflow-x:auto;border:1px solid var(--line);background:var(--surface)}}
table{{border-collapse:collapse;width:100%;min-width:640px;font-size:15px}}
th,td{{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
th{{font:500 12px var(--f-mono);text-transform:uppercase;letter-spacing:.05em;color:var(--muted);background:var(--chip)}}
td.num,tfoot td{{font-family:var(--f-mono);font-variant-numeric:tabular-nums}}
tfoot td{{font-weight:600;font-size:16px}}
input[type=range]{{width:120px;vertical-align:middle;accent-color:var(--lenga)}}
output{{font-family:var(--f-mono);display:inline-block;width:2.2em;text-align:right}}
td.gana{{color:var(--bg);background:var(--bosque)}}
.reco{{border-left:5px solid var(--bosque);background:var(--surface);padding:14px 18px}}
footer{{font-size:14px;color:var(--muted)}}
@media print{{body{{font-size:13px}} .wrap{{max-width:none;gap:0}} .opcion{{break-before:page;border:0;padding:0}} .foto img{{max-height:95mm;width:auto;margin:0 auto}} .diag{{break-inside:avoid;overflow:visible}} .diag svg{{min-width:0}} nav.saltos{{display:none}} .cols3,.cols{{break-inside:avoid}} #comparar{{break-before:page}}}}
</style>
<div class="wrap">
<header class="portada">
  <span class="eyebrow">Tierras Mágicas · RP 11 Km 8,2 · Villa Pehuenia Moquehue</span>
  <h1>Tres opciones para el acceso</h1>
  <p class="lead">Cada opción está desarrollada de punta a punta del frente: la cerca, los 9 mojones, el portal peatonal y el acceso vehicular con la tranquera, el pilar de medidores, la alcantarilla y la banquina. Para cada una hay un fotomontaje del portal, la elevación completa desde la ruta y la planta completa, ambas a escala con las medidas del croquis.</p>
  <nav class="saltos" aria-label="Opciones"><a href="#opcion-1">Opción 1 · Rural liviana</a><a href="#opcion-2">Opción 2 · Patagónico natural</a><a href="#opcion-3">Opción 3 · Refugio de piedra</a><a href="#comparar">Comparar y elegir</a></nav>
</header>
<div class="fijo">
  <b>Lo que es igual en las tres</b>
  <ul>
    <li>Planta del croquis: 9 mojones de 45 × 45 × 150 cm cada 6 m (M0 a M8), pilar de medidores de 100 × 45 × 150 cm y tranquera de 5,50 m.</li>
    <li>Portal de 3,80 m de luz con pilares de 45 × 45 × 340 cm, retirado 1,50 m hacia adentro, con alas que ocupan 2 m sobre la línea de cerca.</li>
    <li>Viga nueva de 6 m (la actual está podrida). Luz solar cálida y dirigida hacia abajo.</li>
    <li>La constructora vial hace la cuneta, la alcantarilla y la banquina. El acceso tiene 20 m perpendiculares a la ruta, con un 2,5 % de pendiente.</li>
    <li>Si la cuneta impide el paso frente al portal, el portal queda cerrado como portada y se entra a pie por la tranquera.</li>
  </ul>
</div>
{tarjetas}
<section id="comparar" class="opcion">
  <h2>Comparar y elegir</h2>
  <h3>Cantidades principales</h3>
  <div class="tabla"><table>
    <thead><tr><th>Elemento</th><th>Opción 1</th><th>Opción 2</th><th>Opción 3</th></tr></thead>
    <tbody>{filas_c}</tbody>
  </table></div>
  <h3>Matriz de selección</h3>
  <p>Puntaje de 1 a 5 por criterio, según el análisis de este anteproyecto. Mové los pesos según tus prioridades y el total se recalcula sobre 100.</p>
  <div class="tabla"><table id="matriz">
    <thead><tr><th>Criterio</th><th>Peso</th><th>Op. 1</th><th>Op. 2</th><th>Op. 3</th></tr></thead>
    <tbody>{filas_m}</tbody>
    <tfoot><tr><td>Total sobre 100</td><td></td><td id="t1"></td><td id="t2"></td><td id="t3"></td></tr></tfoot>
  </table></div>
  <div class="reco" style="margin-top:16px">
    <b>Recomendación: opción 2, Patagónico natural.</b> Con los pesos de base gana por poco a la opción 1 y supera con claridad a la 3. Usa la cerca de tus referencias de punta a punta y repite la misma piedra en la base del portal y del pilar de medidores, así los dos ingresos se leen como un conjunto. Casi todo se hace con mano de obra propia. Si el presupuesto es lo que más pesa, conviene la opción 1. La opción 3 se justifica solo si se busca la mayor presencia desde la ruta.
  </div>
</section>
<footer>
  <p>Elevaciones a escala aproximada de 1 m = 26 px y plantas de 1 m = 15 px, con las medidas del croquis del dueño. La ubicación de la luminaria pública y el ancho de las hojas de la tranquera son aproximados. Los fotomontajes son ilustrativos, no renders fotorrealistas.</p>
  <p><b>Siguiente paso:</b> elegir una opción. Con eso se arma el proyecto ejecutivo de esa opción: detalles finales, lista de compras y pedido de cotizaciones.</p>
</footer>
</div>
<script>
(function(){{
  const filas=[...document.querySelectorAll('#matriz input[type=range]')];
  function calc(){{
    let tot=[0,0,0],suma=0;
    filas.forEach(r=>{{const w=+r.value;suma+=w;document.getElementById('out-'+r.id.slice(5)).textContent=w;
      r.dataset.puntos.split(',').forEach((p,i)=>tot[i]+=w*(+p));}});
    const res=tot.map(t=>suma?Math.round(t/suma/5*100):0), max=Math.max(...res);
    res.forEach((v,i)=>{{const c=document.getElementById('t'+(i+1));c.textContent=v;c.classList.toggle('gana',v===max&&suma>0);}});
  }}
  filas.forEach(r=>r.addEventListener('input',calc));calc();
}})();
</script>
'''


if __name__ == "__main__":
    (BASE / "opciones.html").write_text(pagina(), encoding="utf-8")
    print("ok opciones.html")
