"""Genera opciones.html: tres opciones del acceso con elevación y planta a escala.

Geometría según el croquis del dueño: mojones 45x45x150 cada 6 m, portal de 3,80 m de luz
con pilares 45x45x340 retirado 1,50 m, alas de 2 m sobre la línea de cerca.
Uso: python3 docs/acceso/generar_opciones.py
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent
S = 40          # px por metro
X0 = 34         # margen izquierdo
SUELO = 168     # y del terreno en la elevación

# Tramo representado (m, desde la cara izquierda de M2)
M2, M3, P1, P2, M4, M5 = 0.0, 6.0, 8.45, 12.70, 15.15, 21.15
ANCHO = 21.6

PIEDRA_PINTADA = "#9a948a"
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
        montaje="montajes/OP1_rural_liviana_F07.jpg",
        incluye=[
            "Pilares y mojones reparados y pintados en gris piedra (pintura mineral).",
            "Viga nueva de rollizo y tabla tallada colgada (2,0 × 0,5 m).",
            "Portones existentes reparados, con impregnante oscuro en las dos caras.",
            "Cerca de postes escuadrados 4\"×4\" con punta y 2 travesaños pasantes; 0,95 m de alto libre.",
            "Atrio de ripio compactado con borde de rollizo.",
            "2 luces solares bajo la viga, matas nativas aisladas.",
        ],
        favor=["La más rápida y barata; casi todo con mano de obra propia.",
               "Los mojones de 1,50 m quedan como protagonistas sobre la cerca baja."],
        contra=["Con nieve alta la cerca de 0,95 m casi desaparece.",
                "No es la cerca de las fotos de referencia; no se convierte después en la opción 2."],
        nivel="$",
    ),
    2: dict(
        nombre="Patagónico natural",
        lema="La cerca de las fotos de referencia, con piedra solo en la base.",
        poste=0.127, h_poste=1.15, rieles=(0.35, 0.65, 0.95), riel=0.127, color_cerca=MAD_NATURAL,
        zocalo=0.60, pilar_piedra=False, mojon_piedra=(), alas="cerca", porton="existente",
        cartel="tabla", luces=4, atrio="lajas", faja=0.8, mensulas=False,
        montaje="montajes/OP2_patagonico_natural_F07.jpg",
        incluye=[
            "Pilares y mojones en gris piedra; zócalo de piedra local de 0,60 m en el portal y en el pilar de medidores.",
            "Viga nueva de rollizo y tabla tallada colgada (2,0 × 0,5 m), con «Buen viaje» del lado de adentro.",
            "Portones existentes reparados, con impregnante oscuro en las dos caras.",
            "Cerca de postes escuadrados 5\"×5\" con punta de diamante y 3 travesaños pasantes de 18'; 1,15 m de alto libre, madera natural rojiza.",
            "Atrio con piso de lajas de piedra local y sendero de ripio hacia las cabañas.",
            "4 luces solares (cartel y pilares), faja nativa continua de 0,8 m del lado de adentro.",
        ],
        favor=["Es la cerca que elegiste en las referencias.",
               "La piedra en la base del portal y de los medidores une los dos accesos con poca inversión.",
               "Buen equilibrio entre imagen, costo y trabajo propio."],
        contra=["Más madera para impregnar cada 2-3 años.",
                "El zócalo y las lajas necesitan albañil o pircador."],
        nivel="$$",
    ),
    3: dict(
        nombre="Refugio de piedra",
        lema="Piedra en todo lo que marca el ingreso; madera oscura y metal negro.",
        poste=0.127, h_poste=1.15, rieles=(0.35, 0.65, 0.95), riel=0.127, color_cerca=MAD_OSCURA,
        zocalo=3.40, pilar_piedra=True, mojon_piedra=("M3", "M4"), alas="pirca", porton="nuevo",
        cartel="logo", luces=6, atrio="lajas", faja=1.2, mensulas=True,
        montaje="montajes/OP3_refugio_piedra_F07.jpg",
        incluye=[
            "Pilares del portal revestidos de piedra en toda su altura; también los mojones que flanquean el portal y la tranquera (M1, M3 y M4). El resto, en gris piedra.",
            "Viga nueva de rollizo con ménsulas metálicas negras y el panel del logo existente.",
            "Portón peatonal nuevo: bastidor metálico negro y tablas verticales.",
            "Alas del atrio en pirca de piedra seca de 0,60 m en lugar de cerca.",
            "Cerca de postes escuadrados con 3 travesaños, en madera oscura como los portones.",
            "Atrio de lajas, 6 luces solares (incluye luz baja sobre las pircas), faja nativa de 1,2 m.",
        ],
        favor=["La imagen más fuerte y la que mejor se lee con nieve.",
               "Dialoga con el pilar de piedra del vecino."],
        contra=["La más cara y la más lenta: pircador y herrero.",
                "Reemplaza el portón peatonal, que todavía sirve.",
                "Más riesgo de sobredimensionar el portal."],
        nivel="$$$",
    ),
}


def X(m):
    return X0 + m * S


def Y(h):
    return SUELO - h * S


def defs(k):
    return f'''<defs>
  <pattern id="piedra{k}" width="22" height="14" patternUnits="userSpaceOnUse">
    <rect width="22" height="14" fill="#8d877c"/>
    <rect x="1" y="1" width="12" height="5.5" rx="2" fill="#a59f94"/><rect x="14" y="1" width="7" height="5.5" rx="2" fill="#7f796f"/>
    <rect x="1" y="7.5" width="6" height="5.5" rx="2" fill="#968f84"/><rect x="8" y="7.5" width="13" height="5.5" rx="2" fill="#aaa498"/>
  </pattern>
  <pattern id="lajas{k}" width="26" height="18" patternUnits="userSpaceOnUse">
    <rect width="26" height="18" fill="#7d776d"/><polygon points="1,1 14,1 12,9 1,8" fill="#a8a296"/>
    <polygon points="15,1 25,1 25,10 13,9" fill="#99938a"/><polygon points="1,9 12,10 13,17 1,17" fill="#9f998e"/>
    <polygon points="14,10 25,11 25,17 14,17" fill="#b0aa9e"/>
  </pattern>
  <pattern id="ripio{k}" width="8" height="8" patternUnits="userSpaceOnUse">
    <rect width="8" height="8" fill="#c9bda6"/><circle cx="2" cy="2" r="1.1" fill="#9d917b"/><circle cx="6" cy="5" r="1" fill="#8f846f"/>
  </pattern>
</defs>'''


def mojon(x, k, piedra, h=1.5, a=0.45):
    fill = f"url(#piedra{k})" if piedra else PIEDRA_PINTADA
    x0, x1, xm = X(x), X(x + a), X(x + a / 2)
    return (f'<polygon points="{x0},{Y(0)} {x0},{Y(h - 0.22)} {xm},{Y(h)} {x1},{Y(h - 0.22)} {x1},{Y(0)}" '
            f'fill="{fill}" stroke="{GRIS_LINEA}" stroke-width="1.2"/>')


def pilar(x, k, o):
    out = []
    x0, x1, xm = X(x), X(x + 0.45), X(x + 0.225)
    base = f"url(#piedra{k})" if o["pilar_piedra"] else PIEDRA_PINTADA
    out.append(f'<polygon points="{x0},{Y(0)} {x0},{Y(3.15)} {xm},{Y(3.4)} {x1},{Y(3.15)} {x1},{Y(0)}" fill="{base}" stroke="{GRIS_LINEA}" stroke-width="1.2"/>')
    if o["zocalo"] and not o["pilar_piedra"]:
        out.append(f'<rect x="{x0}" y="{Y(o["zocalo"])}" width="{x1 - x0}" height="{o["zocalo"] * S}" fill="url(#piedra{k})" stroke="{GRIS_LINEA}" stroke-width="1.2"/>')
    return out


def cerca(xa, xb, o, receso=False):
    out = []
    op = ' opacity="0.8"' if receso else ""
    w = o["poste"] * S
    n = max(1, round((xb - xa) / 2.75))
    xs = [xa + (xb - xa) * i / n for i in range(n + 1)]
    for h in o["rieles"]:
        out.append(f'<rect x="{X(xa)}" y="{Y(h) - o["riel"] * S / 2:.1f}" width="{(xb - xa) * S:.1f}" height="{o["riel"] * S:.1f}" fill="{o["color_cerca"]}"{op}/>')
    for x in xs:
        cx = X(x)
        ht = Y(o["h_poste"])
        out.append(f'<polygon points="{cx - w / 2:.1f},{Y(0)} {cx - w / 2:.1f},{ht:.1f} {cx:.1f},{ht - w * 0.7:.1f} {cx + w / 2:.1f},{ht:.1f} {cx + w / 2:.1f},{Y(0)}" fill="{o["color_cerca"]}" stroke="#2a1d15" stroke-width=".6"{op}/>')
    return out


def elevacion(k, o):
    g = [defs(k), f'<rect width="{X(ANCHO) + 40}" height="236" fill="var(--surface)"/>']
    g.append(f'<rect x="0" y="{SUELO}" width="{X(ANCHO) + 34}" height="20" fill="#b9ad94"/>')
    # vegetación detrás de la cerca
    for (a, b) in ((0.6, 5.8), (15.7, 21.0)):
        x = a
        while x < b:
            r = 7 + (int(x * 7) % 5)
            g.append(f'<ellipse cx="{X(x):.1f}" cy="{SUELO - r * 0.6:.1f}" rx="{r + 3}" ry="{r}" fill="{VEGETAL}" opacity=".75"/>')
            x += 1.0 if o["faja"] >= 0.8 else 2.2
    # cerca de tramos
    g += cerca(0.45, 6.0, o)
    g += cerca(15.6, 21.15, o)
    # alas (recedidas 1,5 m: se dibujan más claras)
    if o["alas"] == "cerca":
        g += cerca(6.45, 8.45, o, receso=True)
        g += cerca(13.15, 15.15, o, receso=True)
    else:
        for a, b in ((6.45, 8.45), (13.15, 15.15)):
            g.append(f'<rect x="{X(a)}" y="{Y(0.6)}" width="{(b - a) * S}" height="{0.6 * S}" fill="url(#piedra{k})" stroke="{GRIS_LINEA}"/>')
    # mojones
    for nombre, x in (("M2", M2), ("M3", M3), ("M4", M4), ("M5", M5)):
        g.append(mojon(x, k, nombre in o["mojon_piedra"]))
        g.append(f'<text x="{X(x + 0.06)}" y="{SUELO + 34}" font-size="12" fill="var(--muted)">{nombre}</text>')
    # pilares
    g += pilar(P1, k, o)
    g += pilar(P2, k, o)
    # portón
    gx0, gx1 = X(P1 + 0.45), X(P2)
    if o["porton"] == "existente":
        for h in (0.15, 0.45, 0.75, 1.05, 1.35):
            g.append(f'<rect x="{gx0 + 2}" y="{Y(h) - 3}" width="{gx1 - gx0 - 4}" height="6" fill="{PORTON}"/>')
        mid = X(P1 + 0.45 + 1.4)
        for x in (gx0 + 2, mid - 3, mid + 3, gx1 - 6):
            g.append(f'<rect x="{x}" y="{Y(1.4)}" width="5" height="{1.4 * S}" fill="{PORTON}"/>')
        g.append(f'<line x1="{gx0 + 5}" y1="{Y(0.1)}" x2="{mid - 4}" y2="{Y(1.35)}" stroke="{PORTON}" stroke-width="5"/>')
    else:
        g.append(f'<rect x="{gx0 + 2}" y="{Y(1.45)}" width="{gx1 - gx0 - 4}" height="{1.4 * S}" fill="#1c1c1c"/>')
        x = gx0 + 6
        while x < gx1 - 10:
            g.append(f'<rect x="{x:.1f}" y="{Y(1.38)}" width="7" height="{1.28 * S:.1f}" fill="#7a5235"/>')
            x += 10
        g.append(f'<line x1="{(gx0 + gx1) / 2}" y1="{Y(1.45)}" x2="{(gx0 + gx1) / 2}" y2="{Y(0.05)}" stroke="#111" stroke-width="3"/>')
    # viga
    vx0, vx1 = X(P1 - 0.65), X(P2 + 0.45 + 0.65)
    g.append(f'<rect x="{vx0}" y="{Y(2.99)}" width="{vx1 - vx0}" height="{0.28 * S}" rx="{0.14 * S}" fill="#8b6240" stroke="#5a3d27"/>')
    g.append(f'<ellipse cx="{vx1 - 4}" cy="{Y(2.85)}" rx="4" ry="{0.14 * S}" fill="#c49a6c" stroke="#5a3d27"/>')
    if o["mensulas"]:
        for x in (X(P1 + 0.45), X(P2) - 16):
            g.append(f'<polygon points="{x},{Y(2.71)} {x + 16},{Y(2.71)} {x},{Y(2.71) + 16}" fill="#111"/>')
    # cartel
    cx = (X(P1 + 0.45) + X(P2)) / 2
    if o["cartel"] == "tabla":
        w, h, top = 2.0 * S, 0.5 * S, Y(2.55)
        g.append(f'<line x1="{cx - w / 3}" y1="{Y(2.71)}" x2="{cx - w / 3}" y2="{top}" stroke="#222" stroke-width="1.5"/><line x1="{cx + w / 3}" y1="{Y(2.71)}" x2="{cx + w / 3}" y2="{top}" stroke="#222" stroke-width="1.5"/>')
        g.append(f'<polygon points="{cx - w / 2 - 3},{top} {cx},{top - 6} {cx + w / 2 + 3},{top}" fill="#2a2420"/>')
        g.append(f'<rect x="{cx - w / 2}" y="{top}" width="{w}" height="{h}" rx="3" fill="#4a3324"/>')
        g.append(f'<text x="{cx}" y="{top + h * 0.62}" text-anchor="middle" font-size="9" font-weight="700" fill="#e2cda0" font-family="Georgia,serif" textLength="{w * 0.86:.0f}" lengthAdjust="spacingAndGlyphs">TIERRAS MÁGICAS</text>')
    else:
        w, top = 0.85 * S, Y(2.6)
        g.append(f'<line x1="{cx - w / 3}" y1="{Y(2.71)}" x2="{cx - w / 3}" y2="{top}" stroke="#222" stroke-width="1.5"/><line x1="{cx + w / 3}" y1="{Y(2.71)}" x2="{cx + w / 3}" y2="{top}" stroke="#222" stroke-width="1.5"/>')
        g.append(f'<rect x="{cx - w / 2 - 4}" y="{top - 4}" width="{w + 8}" height="{w + 8}" fill="#5a3d27"/><rect x="{cx - w / 2}" y="{top}" width="{w}" height="{w}" fill="#1f3326"/>')
        g.append(f'<polygon points="{cx - 12},{top + 18} {cx - 3},{top + 7} {cx + 5},{top + 15} {cx + 11},{top + 9} {cx + 16},{top + 18}" fill="none" stroke="#d8b878" stroke-width="1.4"/>')
        g.append(f'<text x="{cx}" y="{top + w - 8}" text-anchor="middle" font-size="7" fill="#d8b878" font-family="Georgia,serif">Tierras Mágicas</text>')
    # luces (conos hacia abajo)
    puntos = [(X(P1 + 1.4), Y(2.71)), (X(P2 - 0.95), Y(2.71))]
    if o["luces"] >= 4:
        puntos += [(X(P1 + 0.225), Y(2.2)), (X(P2 + 0.225), Y(2.2))]
    if o["luces"] >= 6:
        puntos += [(X(7.4), Y(0.75)), (X(14.2), Y(0.75))]
    for (x, y) in puntos:
        g.append(f'<polygon points="{x},{y} {x - 14},{y + 34} {x + 14},{y + 34}" fill="#f2c46b" opacity=".28"/><circle cx="{x}" cy="{y}" r="3.5" fill="#e0a43a"/>')
    # cotas
    def cota(a, b, y, txt):
        g.append(f'<line x1="{X(a)}" y1="{y}" x2="{X(b)}" y2="{y}" stroke="var(--muted)" stroke-width="1"/>'
                 f'<line x1="{X(a)}" y1="{y - 4}" x2="{X(a)}" y2="{y + 4}" stroke="var(--muted)"/><line x1="{X(b)}" y1="{y - 4}" x2="{X(b)}" y2="{y + 4}" stroke="var(--muted)"/>'
                 f'<text x="{(X(a) + X(b)) / 2}" y="{y - 4}" text-anchor="middle" font-size="12" fill="var(--muted)">{txt}</text>')
    cota(0.225, 6.225, SUELO + 52, "6,00")
    cota(6.45, 8.45, SUELO + 52, "2,00")
    cota(8.9, 12.7, SUELO + 52, "3,80")
    cota(13.15, 15.15, SUELO + 52, "2,00")
    cota(15.375, 21.375, SUELO + 52, "6,00")
    g.append(f'<line x1="{X(ANCHO) + 14}" y1="{Y(0)}" x2="{X(ANCHO) + 14}" y2="{Y(3.4)}" stroke="var(--muted)"/><text x="{X(ANCHO) + 18}" y="{Y(1.7)}" font-size="12" fill="var(--muted)" transform="rotate(-90 {X(ANCHO) + 18} {Y(1.7)})" text-anchor="middle">3,40</text>')
    alto = f'{o["h_poste"]:.2f}'.replace(".", ",")
    g.append(f'<text x="{X(0.6)}" y="{Y(o["h_poste"]) - 10:.1f}" font-size="12" fill="var(--fg)">cerca {alto} m</text>')
    return f'<svg viewBox="0 0 {X(ANCHO) + 40:.0f} 236" role="img" aria-label="Elevación desde la ruta, opción {k}">' + "\n".join(g) + "</svg>"


def planta(k, o):
    yl, rec = 120, 1.5 * S
    g = [defs(k), f'<rect width="{X(ANCHO) + 40}" height="230" fill="var(--surface)"/>']
    g.append(f'<rect x="0" y="{yl + 30}" width="{X(ANCHO) + 40}" height="60" fill="#d6cbb3" opacity=".6"/>')
    g.append(f'<text x="{X(15.7)}" y="{yl + 66}" font-size="12" fill="var(--muted)">banquina · ruta</text>')
    g.append(f'<text x="{X(15.7)}" y="22" font-size="12" fill="var(--muted)">interior del lote</text>')
    # faja de plantación (adentro)
    fw = o["faja"] * S
    for a, b in ((0.45, 6.0), (15.6, 21.15)):
        g.append(f'<rect x="{X(a)}" y="{yl - fw - 4}" width="{(b - a) * S}" height="{fw}" fill="{VEGETAL}" opacity=".35"/>')
    # atrio
    pts = f"{X(6.45)},{yl} {X(8.45)},{yl - rec} {X(13.15)},{yl - rec} {X(15.15)},{yl}"
    fill = {"ripio": f"url(#ripio{k})", "lajas": f"url(#lajas{k})"}[o["atrio"]]
    g.append(f'<polygon points="{pts}" fill="{fill}" opacity=".9"/>')
    g.append(f'<text x="{X(10.8)}" y="{yl - 12}" text-anchor="middle" font-size="12" fill="var(--fg)">atrio de {o["atrio"]}</text>')
    # línea de cerca
    col = o["color_cerca"]
    g.append(f'<line x1="{X(0.45)}" y1="{yl}" x2="{X(6)}" y2="{yl}" stroke="{col}" stroke-width="5"/>')
    g.append(f'<line x1="{X(15.6)}" y1="{yl}" x2="{X(21.15)}" y2="{yl}" stroke="{col}" stroke-width="5"/>')
    if o["alas"] == "cerca":
        g.append(f'<line x1="{X(6.45)}" y1="{yl}" x2="{X(8.45)}" y2="{yl - rec}" stroke="{col}" stroke-width="5"/><line x1="{X(13.15)}" y1="{yl - rec}" x2="{X(15.15)}" y2="{yl}" stroke="{col}" stroke-width="5"/>')
    else:
        for (a1, b1, a2, b2) in ((6.45, yl, 8.45, yl - rec), (13.15, yl - rec, 15.15, yl)):
            g.append(f'<line x1="{X(a1)}" y1="{b1}" x2="{X(a2)}" y2="{b2}" stroke="url(#piedra{k})" stroke-width="14"/><line x1="{X(a1)}" y1="{b1}" x2="{X(a2)}" y2="{b2}" stroke="{GRIS_LINEA}" stroke-width="1" stroke-dasharray="3 3"/>')
    # postes en tramos
    for a, b in ((0.45, 6.0), (15.6, 21.15)):
        for i in range(3):
            x = a + 0.08 + (b - a - 0.16) * i / 2
            g.append(f'<rect x="{X(x) - 3}" y="{yl - 3}" width="6" height="6" fill="{col}"/>')
    for nombre, x in (("M2", M2), ("M3", M3), ("M4", M4), ("M5", M5)):
        fill = f"url(#piedra{k})" if nombre in o["mojon_piedra"] else PIEDRA_PINTADA
        g.append(f'<rect x="{X(x)}" y="{yl + 1}" width="{0.45 * S}" height="{0.45 * S}" fill="{fill}" stroke="{GRIS_LINEA}"/>')
    for x in (P1, P2):
        fill = f"url(#piedra{k})" if o["pilar_piedra"] or o["zocalo"] else PIEDRA_PINTADA
        g.append(f'<rect x="{X(x)}" y="{yl - rec - 9}" width="{0.45 * S}" height="{0.45 * S}" fill="{fill}" stroke="{GRIS_LINEA}"/>')
    # portón y viga
    g.append(f'<line x1="{X(P1 + 0.45)}" y1="{yl - rec}" x2="{X(P2)}" y2="{yl - rec}" stroke="{PORTON}" stroke-width="4" stroke-dasharray="7 3"/>')
    g.append(f'<line x1="{X(P1 - 0.65)}" y1="{yl - rec - 2}" x2="{X(P2 + 1.1)}" y2="{yl - rec - 2}" stroke="#8b6240" stroke-width="3" opacity=".7"/>')
    # sendero
    g.append(f'<path d="M{X(10.8)} {yl - rec - 10} C{X(10.9)} 20 {X(12.5)} 10 {X(13.5)} 0" stroke="#b5a585" stroke-width="{1.2 * S}" fill="none" opacity=".55"/>')
    g.append(f'<text x="{X(13.4)}" y="30" font-size="12" fill="var(--fg)">sendero 1,2 m</text>')
    # cotas
    g.append(f'<line x1="{X(16.0)}" y1="{yl}" x2="{X(16.0)}" y2="{yl - rec}" stroke="var(--muted)"/><text x="{X(16.1)}" y="{yl - rec / 2 + 4}" font-size="12" fill="var(--muted)">1,50</text>')
    return f'<svg viewBox="0 0 {X(ANCHO) + 40:.0f} 230" role="img" aria-label="Planta del tramo del portal, opción {k}">' + "\n".join(g) + "</svg>"


CRITERIOS = [
    ("imagen", "Imagen e identidad patagónica", 25, (3, 4, 5)),
    ("nieve", "Se lee bien con nieve", 15, (3, 4, 5)),
    ("costo", "Inversión controlada", 20, (5, 4, 2)),
    ("mant", "Mantenimiento bajo", 15, (4, 4, 3)),
    ("propia", "Ejecución con mano de obra propia y en plazo", 15, (5, 4, 2)),
    ("reuso", "Reutiliza lo existente", 10, (5, 5, 3)),
]

CANTIDADES = [
    ("Postes escuadrados", "25 de 4\"×4\" × 1,60 m", "25 de 5\"×5\" × 1,85 m", "21 de 5\"×5\" × 1,85 m"),
    ("Travesaños", "14 de 18' + 4 de 10'", "21 de 18' + 6 de 10'", "21 de 18'"),
    ("Piedra en pilares y mojones", "—", "≈ 3,9 m² (zócalos)", "≈ 28 m² (pilares, 3 mojones y medidores)"),
    ("Pircas en las alas", "—", "—", "2 × 2,5 m × 0,60 m"),
    ("Atrio (≈ 5,7 m²)", "ripio", "lajas", "lajas"),
    ("Portón peatonal", "se repara", "se repara", "nuevo, metal + madera"),
    ("Cartel", "tabla tallada", "tabla tallada", "panel con el logo existente"),
    ("Luces solares", "2", "4 + 8 balizas de sendero", "6 + 8 balizas de sendero"),
    ("Oficios", "propio", "propio + pircador (≈ 4 jornales)", "propio + pircador (≈ 15 jornales) + herrero"),
    ("Inversión relativa", "$", "$$", "$$$"),
]


def tarjeta(k, o):
    inc = "".join(f"<li>{t}</li>" for t in o["incluye"])
    fav = "".join(f"<li>{t}</li>" for t in o["favor"])
    con = "".join(f"<li>{t}</li>" for t in o["contra"])
    return f'''
<section class="opcion" id="opcion-{k}">
  <header class="op-cab">
    <span class="op-num">Opción {k}</span>
    <h2>{o["nombre"]}</h2>
    <span class="nivel" title="Inversión relativa">{o["nivel"]}</span>
  </header>
  <p class="lema">{o["lema"]}</p>
  <figure class="foto"><img src="{o["montaje"]}" alt="Fotomontaje de la opción {k} sobre la foto del portal"><figcaption>Fotomontaje ilustrativo sobre la foto del portal (F07).</figcaption></figure>
  <h3>Elevación desde la ruta</h3>
  <div class="diag">{elevacion(k, o)}</div>
  <h3>Planta del portal y el atrio</h3>
  <div class="diag">{planta(k, o)}</div>
  <div class="cols">
    <div><h3>Qué incluye</h3><ul>{inc}</ul></div>
    <div><h3>A favor</h3><ul class="mas">{fav}</ul><h3>En contra</h3><ul class="menos">{con}</ul></div>
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
/* Layout: una columna de 1080 px; cada opción es una lámina con foto, elevación, planta y fichas */
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
.diag{{overflow-x:auto;border:1px solid var(--line)}}
.diag svg{{display:block;width:100%;min-width:680px;height:auto}}
svg text{{font-family:var(--f-body)}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:8px 28px}}
.cols>div{{min-width:0}}
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
</style>
<div class="wrap">
<header class="portada">
  <span class="eyebrow">Tierras Mágicas · acceso · selección de alternativa</span>
  <h1>Tres opciones para el acceso</h1>
  <p class="lead">Las tres opciones usan la misma planta, la del croquis del dueño, y cambian el tratamiento. Para cada una hay un fotomontaje, la elevación desde la ruta y la planta del portal a escala, qué incluye, y una matriz para elegir.</p>
  <nav class="saltos" aria-label="Opciones"><a href="#opcion-1">Opción 1 · Rural liviana</a><a href="#opcion-2">Opción 2 · Patagónico natural</a><a href="#opcion-3">Opción 3 · Refugio de piedra</a><a href="#comparar">Comparar y elegir</a></nav>
</header>
<div class="fijo">
  <b>Lo que es igual en las tres</b>
  <ul>
    <li>Cerca recta con 9 mojones de 45 × 45 × 150 cm cada 6 m, y la tranquera de 5,50 m junto al pilar de medidores.</li>
    <li>Portal de 3,80 m de luz con pilares de 45 × 45 × 340 cm, retirado 1,50 m hacia adentro, con alas de 2 m sobre la línea de cerca.</li>
    <li>Viga nueva, porque la actual está podrida. Mojones en gris piedra en lugar de blanco. Luz solar cálida dirigida hacia abajo. Banquina libre para estacionar.</li>
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
    <b>Recomendación: opción 2, Patagónico natural.</b> Con los pesos de base gana por poco a la opción 1 y supera con claridad a la 3. Usa la cerca que elegiste en las referencias, mantiene casi todo con mano de obra propia y suma piedra solo donde rinde: en la base del portal y de los medidores. Si el presupuesto es lo que más pesa, conviene la opción 1. La opción 3 se justifica solo si se busca la mayor presencia desde la ruta y se acepta reemplazar el portón peatonal.
  </div>
</section>
<footer>
  <p>Las elevaciones y plantas están a escala aproximada (1 m = 40 px) con las medidas del croquis. Los fotomontajes son ilustrativos, no renders fotorrealistas. El detalle completo, el cómputo y las etapas están en el anteproyecto del acceso.</p>
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
