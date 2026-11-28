"""Fotomontajes ILUSTRATIVOS del acceso de Tierras Mágicas.

No son renders fotorrealistas: se pinta sobre las fotos originales (2000x1506)
para mostrar color, proporción y ubicación de cada intervención.
Uso: python3 docs/acceso/montajes/generar_montajes.py
"""
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parent
FOTOS = BASE.parent / "fotos"
OUT = BASE
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
random.seed(7)

# Tono propuesto para pilares y mojones: gris piedra cálido (pintura mineral)
PIEDRA = np.array([150, 141, 126], dtype=float)
MADERA = (78, 52, 34)
MADERA_LUZ = (122, 86, 58)

# ---- Geometría relevada sobre F07 (vista frontal del portal) ----
F07 = {
    "pilar_izq": [(537, 475), (565, 443), (598, 455), (626, 525), (628, 922), (530, 922)],
    "pilar_der": [(1150, 480), (1188, 437), (1225, 460), (1238, 500), (1234, 926), (1148, 926)],
    "mojon_izq": [(0, 772), (40, 757), (86, 786), (92, 1016), (0, 1016)],
    "mojon_der": [(1622, 822), (1690, 760), (1748, 822), (1753, 1032), (1621, 1032)],
    "viga": (612, 524, 1150, 560),
}


def mascara(size, poligonos):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for p in poligonos:
        d.polygon(p, fill=255)
    return m


def teñir(img, mask, color=PIEDRA, ganancia=1.05):
    """Reemplaza el blanco por un tono mineral conservando luces y sombras."""
    a = np.asarray(img).astype(float)
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 235.0
    nuevo = np.clip(color[None, None, :] * (lum[..., None] ** 0.9) * ganancia, 0, 255)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2))).astype(float)[..., None] / 255
    return Image.fromarray((a * (1 - m) + nuevo * m).astype("uint8"))


def piedra_textura(size, piedra_px=34, junta=(70, 64, 58)):
    """Mampostería de piedra local (bola/laja) dibujada de forma esquemática."""
    w, h = size
    t = Image.new("RGB", size, junta)
    d = ImageDraw.Draw(t)
    y = 0
    while y < h:
        alto = int(piedra_px * random.uniform(0.6, 1.0))
        x = -random.randint(0, piedra_px)
        while x < w:
            ancho = int(piedra_px * random.uniform(0.9, 1.7))
            g = random.randint(105, 175)
            c = (g + random.randint(-6, 14), g + random.randint(-8, 6), g - random.randint(0, 18))
            d.rounded_rectangle([x + 2, y + 2, x + ancho - 2, y + alto - 2], radius=alto // 3, fill=c)
            d.line([x + 4, y + 4, x + ancho - 6, y + 4], fill=tuple(min(255, v + 25) for v in c), width=2)
            x += ancho
        y += alto
    return t


def zocalo(img, poligono, y_desde, luz_ref=None, piedra_px=None, lum_min=0.35):
    """Aplica piedra en el polígono por debajo de y_desde, sombreada con la foto."""
    w, h = img.size
    m = mascara(img.size, [poligono])
    corte = Image.new("L", img.size, 0)
    ImageDraw.Draw(corte).rectangle([0, y_desde, w, h], fill=255)
    m = Image.fromarray(np.minimum(np.asarray(m), np.asarray(corte)))
    tex = np.asarray(piedra_textura(img.size, piedra_px=piedra_px or max(18, int((poligono[3][0] - poligono[0][0]) / 3.2)))).astype(float)
    a = np.asarray(img).astype(float)
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 225.0
    tex = np.clip(tex * np.clip(lum, lum_min, 1.1)[..., None], 0, 255)
    mm = np.asarray(m).astype(float)[..., None] / 255
    out = Image.fromarray((a * (1 - mm) + tex * mm).astype("uint8"))
    d = ImageDraw.Draw(out)
    xs = [p[0] for p in poligono]
    d.line([min(xs) - 3, y_desde, max(xs) + 3, y_desde], fill=(95, 88, 80), width=5)  # buña/remate
    return out


def travesaño(d, x0, y0, x1, y1, grosor):
    d.line([x0, y0, x1, y1], fill=MADERA, width=grosor)
    d.line([x0, y0 - grosor // 3, x1, y1 - grosor // 3], fill=MADERA_LUZ, width=max(2, grosor // 4))


def poste(d, x, y_top, y_base, ancho):
    d.rectangle([x - ancho // 2, y_top, x + ancho // 2, y_base], fill=MADERA)
    d.rectangle([x - ancho // 2, y_top, x - ancho // 2 + max(2, ancho // 4), y_base], fill=MADERA_LUZ)
    d.polygon([(x - ancho // 2, y_top), (x + ancho // 2, y_top - ancho // 3), (x + ancho // 2, y_top)], fill=MADERA)


def cartel_tabla(img, cx, y_top, ancho, alto, sub=True):
    """Tabla de madera oscura colgada de la viga, letras grabadas color crema."""
    d = ImageDraw.Draw(img)
    x0, x1 = cx - ancho // 2, cx + ancho // 2
    for xc in (x0 + ancho // 8, x1 - ancho // 8):  # cadenas
        d.line([xc, y_top - 34, xc, y_top], fill=(40, 40, 40), width=3)
    d.rounded_rectangle([x0 + 4, y_top + 5, x1 + 4, y_top + alto + 5], radius=6, fill=(30, 24, 20))
    d.rounded_rectangle([x0, y_top, x1, y_top + alto], radius=6, fill=(58, 40, 28), outline=(32, 22, 16), width=3)
    d.polygon([(x0 - 6, y_top), (cx, y_top - 14), (x1 + 6, y_top)], fill=(36, 30, 26))  # botaguas (no retiene nieve)
    t = "TIERRAS MÁGICAS"
    tam = int(alto * (0.42 if sub else 0.55))
    while tam > 8 and d.textlength(t, font=ImageFont.truetype(SERIF, tam)) > ancho * 0.9:
        tam -= 1
    f1 = ImageFont.truetype(SERIF, tam)
    tw = d.textlength(t, font=f1)
    d.text((cx - tw / 2, y_top + alto * 0.12), t, font=f1, fill=(226, 205, 160))
    if sub:
        s = "CABAÑAS DE MONTAÑA · VILLA PEHUENIA MOQUEHUE"
        tam2 = int(alto * 0.14)
        while tam2 > 6 and d.textlength(s, font=ImageFont.truetype(SANS, tam2)) > ancho * 0.92:
            tam2 -= 1
        f2 = ImageFont.truetype(SANS, tam2)
        sw = d.textlength(s, font=f2)
        d.text((cx - sw / 2, y_top + alto * 0.66), s, font=f2, fill=(210, 190, 150))


def cartel_logo(img, cx, y_top, alto):
    """Panel con el logo que ya diseñó el establecimiento (cartel_referencia.png)."""
    ref = Image.open(FOTOS / "cartel_referencia.png").convert("RGB")
    panel = ref.crop((452, 612, 948, 1102))
    ancho = int(alto * panel.width / panel.height)
    panel = panel.resize((ancho, alto), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    x0 = cx - ancho // 2
    for xc in (x0 + ancho // 6, x0 + ancho - ancho // 6):
        d.line([xc, y_top - 30, xc, y_top], fill=(35, 35, 35), width=3)
    d.rectangle([x0 - 9, y_top - 9, x0 + ancho + 9, y_top + alto + 9], fill=(70, 46, 30))
    d.polygon([(x0 - 14, y_top - 9), (cx, y_top - 26), (x0 + ancho + 14, y_top - 9)], fill=(36, 30, 26))
    img.paste(panel, (x0, y_top))


def plantas(img, zonas, densidad=18):
    """Matas nativas esquemáticas (coirón, calafate, chaura) en la base de la cerca."""
    d = ImageDraw.Draw(img, "RGBA")
    for (x0, x1, y) in zonas:
        for _ in range(int((x1 - x0) / 100 * densidad)):
            x = random.uniform(x0, x1)
            r = random.uniform(14, 30)
            tipo = random.random()
            if tipo < 0.45:  # coirón: mata de gramínea
                for k in range(14):
                    ang = random.uniform(-1.2, 1.2)
                    d.line([x, y, x + np.sin(ang) * r * 1.4, y - np.cos(ang) * r * 1.8], fill=(164, 160, 104, 235), width=3)
            else:  # arbusto bajo
                c = (58, 92, 44, 240) if tipo < 0.8 else (74, 104, 52, 240)
                d.ellipse([x - r, y - r * 1.5, x + r, y + 2], fill=c)
                d.ellipse([x - r * 0.6, y - r * 1.4, x + r * 0.2, y - r * 0.6], fill=(96, 128, 66, 200))


def pintar_portero_reparado(img):
    """Hoja chica del portón: se retira la pieza suelta y se repinta oscuro."""
    d = ImageDraw.Draw(img)
    a = np.asarray(img)
    # Se tapa la pieza caída que sobresale bajo la hoja izquierda con el pasto vecino.
    parche = Image.fromarray(a[945:1000, 560:640]).resize((120, 75))
    img.paste(parche, (676, 925))
    # Hoja izquierda redibujada: marco + 4 tablas + diagonal
    x0, y0, x1, y1 = 634, 754, 796, 930
    for y in np.linspace(y0 + 8, y1 - 10, 5):
        d.line([x0, y, x1, y], fill=(36, 28, 24), width=13)
    d.line([x0, y0, x0, y1], fill=(36, 28, 24), width=14)
    d.line([x1, y0, x1, y1], fill=(36, 28, 24), width=14)
    d.line([x0 + 6, y1 - 8, x1 - 6, y0 + 8], fill=(36, 28, 24), width=12)


def limpiar_ladrillos(img):
    a = np.asarray(img)
    parche = Image.fromarray(a[935:975, 880:960])
    img.paste(parche.resize((90, 45)), (975, 935))
    img.paste(parche.resize((80, 40)), (1115, 925))


# ---------------- Alternativas sobre F07 ----------------

def alternativa_1():
    img = Image.open(FOTOS / "F07.jpg").convert("RGB")
    m = mascara(img.size, [F07["pilar_izq"], F07["pilar_der"], F07["mojon_izq"], F07["mojon_der"]])
    img = teñir(img, m)
    pintar_portero_reparado(img)
    limpiar_ladrillos(img)
    viga_nueva(img)
    # Placa de identificación atornillada al pilar derecho
    d = ImageDraw.Draw(img)
    d.rectangle([1160, 640, 1226, 760], fill=(34, 34, 32), outline=(20, 20, 20), width=2)
    f = ImageFont.truetype(SERIF, 15)
    for i, t in enumerate(["TIERRAS", "MÁGICAS"]):
        tw = d.textlength(t, font=f)
        d.text((1193 - tw / 2, 668 + i * 22), t, font=f, fill=(214, 190, 130))
    f2 = ImageFont.truetype(SANS, 9)
    d.text((1193 - d.textlength("CABAÑAS", font=f2) / 2, 720), "CABAÑAS", font=f2, fill=(190, 170, 120))
    plantas(img, [(120, 520, 925), (1250, 1600, 935)], densidad=6)
    return img


MAD_C = (146, 86, 54)
MAD_C_LUZ = (184, 120, 80)
MAD_C_SOMBRA = (92, 52, 32)


CERCA = {"alturas": (0.35, 0.65, 0.95), "h": 1.15, "w": 0.17, "t": 0.13}


def geom_cerca(ini, fin, px_m):
    """Cerca de postes escuadrados con punta de diamante y 3 travesaños pasantes
    (tipología de las fotos de referencia). 3 postes por tramo de 6 m (≈ 2,7 m), 1,15 m libre."""
    (xa, ya), (xb, yb) = ini, fin
    yb_de = lambda x: ya + (yb - ya) * (x - xa) / (xb - xa)
    w = max(6, int(CERCA["w"] * px_m))
    t = max(4, int(CERCA["t"] * px_m))
    n = max(1, round((xb - xa) / (2.7 * px_m)))
    postes = [(xa + (xb - xa) * k / n) for k in range(n + 1)]
    rieles = [(xa - w, yb_de(xa) - h * px_m, xb + w, yb_de(xb) - h * px_m, t) for h in CERCA["alturas"]]
    return [(x, yb_de(x) - CERCA["h"] * px_m, yb_de(x), w) for x in postes], rieles


def dibujar_cerca(d, geom, mascara=False):
    postes, rieles = geom
    c, cl, cs = CERCA.get("colores", (MAD_C, MAD_C_LUZ, MAD_C_SOMBRA))
    if mascara:
        c = cl = cs = 255
    for (x0, y0, x1, y1, t) in rieles:
        d.line([x0, y0, x1, y1], fill=c, width=t)
        d.line([x0, y0 - t / 2 + 1, x1, y1 - t / 2 + 1], fill=cl, width=max(1, t // 4))
        d.line([x0, y0 + t / 2 - 1, x1, y1 + t / 2 - 1], fill=cs, width=max(1, t // 5))
    for (x, yt, yb, w) in postes:
        d.rectangle([x - w / 2, yt, x + w / 2, yb], fill=c)
        d.rectangle([x - w / 2, yt, x - w / 2 + max(1, w // 3), yb], fill=cl)
        d.rectangle([x + w / 2 - max(1, w // 4), yt, x + w / 2, yb], fill=cs)
        d.polygon([(x - w / 2, yt), (x, yt - w * 0.7), (x + w / 2, yt)], fill=cl)
        for (x0, y0, x1, y1, t) in rieles:  # caja del travesaño pasante
            yr = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            d.rectangle([x - w / 2, yr - t / 2, x + w / 2, yr + t / 2], fill=cs)


TRAMOS_F07 = [((0, 958), (530, 922), 130), ((1238, 924), (2000, 992), 130)]


def cerca_travesaños(img, tramos=TRAMOS_F07, encima=None):
    """Dibuja la cerca y vuelve a poner por delante los mojones (están más cerca de la ruta)."""
    antes = img.copy()
    d = ImageDraw.Draw(img)
    for ini, fin, px in tramos:
        dibujar_cerca(d, geom_cerca(ini, fin, px))
    if encima is None:
        encima = mascara(img.size, [F07["mojon_izq"], F07["mojon_der"]])
    img.paste(antes, (0, 0), encima)


def mascara_cerca(size, tramos=TRAMOS_F07):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for ini, fin, px in tramos:
        dibujar_cerca(d, geom_cerca(ini, fin, px), mascara=True)
    return m


def viga_nueva(img, x0=462, x1=1312, y0=517, y1=563):
    """Rollizo nuevo (la viga existente está podrida y se reemplaza)."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) // 2, fill=(124, 90, 62))
    d.line([x0 + 18, y0 + 9, x1 - 18, y0 + 9], fill=(160, 122, 86), width=6)
    d.line([x0 + 18, y1 - 8, x1 - 18, y1 - 8], fill=(104, 70, 44), width=6)
    for x in (x0, x1 - (y1 - y0) * 0.7):
        d.ellipse([x, y0, x + (y1 - y0) * 0.7, y1], fill=(198, 156, 108), outline=(110, 76, 48), width=3)


def alternativa_2(img=None):
    img = img or Image.open(FOTOS / "F07.jpg").convert("RGB")
    m = mascara(img.size, [F07["pilar_izq"], F07["pilar_der"], F07["mojon_izq"], F07["mojon_der"]])
    img = teñir(img, m)
    img = zocalo(img, F07["pilar_izq"], 800)
    img = zocalo(img, F07["pilar_der"], 800)
    pintar_portero_reparado(img)
    limpiar_ladrillos(img)
    viga_nueva(img)
    cerca_travesaños(img)
    cartel_tabla(img, 885, 600, 280, 70)
    plantas(img, [(110, 520, 940), (1250, 1610, 945), (1760, 1990, 1030)], densidad=14)
    # Luminarias: aplique bajo la viga (baña el cartel) y en cada pilar
    d = ImageDraw.Draw(img)
    for x in (780, 990):
        d.rectangle([x - 8, 560, x + 8, 574], fill=(30, 30, 30))
    for (x, y) in ((579, 760), (1192, 772)):
        d.rectangle([x - 9, y, x + 9, y + 22], fill=(32, 32, 32))
    return img


def alternativa_3():
    img = Image.open(FOTOS / "F07.jpg").convert("RGB")
    m = mascara(img.size, [F07["mojon_izq"], F07["mojon_der"]])
    img = teñir(img, m)
    img = zocalo(img, F07["pilar_izq"], 470)
    img = zocalo(img, F07["pilar_der"], 470)
    img = zocalo(img, F07["mojon_der"], 830)
    # Viga renovada: rollizo más grueso + ménsulas metálicas negras
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 560, 515, 1290, 568
    d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(96, 66, 44))
    d.line([x0 + 20, y0 + 9, x1 - 20, y0 + 9], fill=(140, 100, 68), width=6)
    d.line([x0 + 20, y1 - 8, x1 - 20, y1 - 8], fill=(66, 44, 30), width=6)
    d.ellipse([x1 - 30, y0, x1 + 4, y1], fill=(170, 128, 86), outline=(90, 60, 40), width=3)
    for x in (600, 1150):
        d.rectangle([x, 568, x + 50, 580], fill=(24, 24, 24))
        d.polygon([(x + 10, 580), (x + 40, 580), (x + 25, 610)], fill=(24, 24, 24))
    pintar_portero_reparado(img)
    # Portón peatonal rediseñado: bastidor metálico negro con tablas verticales de madera
    d.rectangle([630, 748, 1146, 935], fill=(28, 28, 28))
    for x in range(640, 1140, 26):
        d.rectangle([x, 758, x + 20, 925], fill=(104, 72, 48))
        d.line([x + 3, 760, x + 3, 923], fill=(132, 94, 64), width=2)
    d.line([888, 748, 888, 935], fill=(20, 20, 20), width=6)
    limpiar_ladrillos(img)
    cerca_travesaños(img)
    cartel_logo(img, 888, 605, 135)
    plantas(img, [(100, 525, 945), (1245, 1615, 950), (1760, 1995, 1040), (420, 1500, 1010)], densidad=16)
    # Pircas bajas de piedra seca a cada lado del ingreso (antepecho 45 cm aprox.)
    for (xa, xb, yb) in ((330, 525, 1000), (1245, 1450, 1005)):
        bloque = piedra_textura((xb - xa, 60), piedra_px=24)
        img.paste(bloque, (xa, yb - 60))
    return img


# ---------------- Estaciones (alternativa 2) ----------------

def mascara_vegetal(a):
    hsv = np.asarray(Image.fromarray(a).convert("HSV")).astype(float)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    return ((h > 45) & (h < 150) & (s > 0.22) & (v > 0.12)).astype(float)


def otoño(img):
    a = np.asarray(img).copy()
    veg = mascara_vegetal(a)
    hsv = np.asarray(img.convert("HSV")).astype(float)
    alto = np.zeros(veg.shape)
    alto[:700] = 1.0  # copas de ñires y lengas: rojo/anaranjado
    tono = np.where(alto > 0, 14 + np.random.rand(*veg.shape) * 18, 32 + np.random.rand(*veg.shape) * 8)
    hsv[..., 0] = np.where(veg > 0, tono * 255 / 360, hsv[..., 0])
    hsv[..., 1] = np.where(veg > 0, np.clip(hsv[..., 1] * 1.15, 0, 255), hsv[..., 1])
    out = Image.fromarray(hsv.astype("uint8"), "HSV").convert("RGB")
    out = Image.blend(img, out, 0.82)
    return out


def primavera(img):
    a = np.asarray(img).astype(float)
    veg = mascara_vegetal(a.astype("uint8"))[..., None]
    verde = a * np.array([0.86, 1.08, 0.82])
    out = Image.fromarray(np.clip(a * (1 - veg) + verde * veg, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(out)
    for (x0, x1, y) in ((110, 520, 930), (1250, 1610, 935), (1760, 1990, 1020)):
        for _ in range(int((x1 - x0) / 7)):
            x, yy = random.uniform(x0, x1), y - random.uniform(0, 40)
            c = random.choice([(238, 140, 40), (250, 200, 50), (250, 200, 50), (200, 40, 40)])  # amancay, calafate, notro
            d.ellipse([x - 4, yy - 4, x + 4, yy + 4], fill=c)
    return out


def invierno(img):
    a = np.asarray(img).astype(float)
    alto, ancho = a.shape[:2]
    hsv = np.asarray(img.convert("HSV")).astype(float)
    h, s_, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    lum = a.mean(axis=2)
    # Luz invernal: menos saturación (ñires y lengas sin hoja)
    a = a * 0.3 + lum[..., None] * 0.7
    a = a * np.array([0.94, 0.97, 1.05])
    # Cielo cubierto (incluye el halo del sol)
    cielo = (((h > 180) & (h < 260) & (s_ > 0.12)) | (v > 0.93)).astype(float)
    cielo[650:] = 0
    cielo = np.asarray(Image.fromarray((cielo * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(6))).astype(float) / 255
    a = a * (1 - cielo[..., None]) + np.array([200, 205, 212]) * cielo[..., None]
    # Nieve en el suelo: gradiente suave desde la ladera; lo oscuro (sombras, troncos, casa) queda visible
    y = np.arange(alto)[:, None] * np.ones((1, ancho))
    suelo = np.clip((y - 560) / 120, 0, 1)
    claro = np.clip((lum / 255 - 0.12) / 0.25, 0, 1)
    ruido = np.asarray(Image.fromarray((np.random.rand(alto, ancho) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(3))).astype(float) / 255
    nieve = np.clip(suelo * claro * (0.8 + 0.2 * ruido), 0, 0.92)
    blanco = np.array([238, 241, 246])
    a = a * (1 - nieve[..., None]) + blanco * nieve[..., None]
    # Escarcha fina en copas
    copa = (y < 640) & (cielo < 0.2) & (np.random.rand(alto, ancho) > 0.7)
    a[copa] = a[copa] * 0.55 + blanco * 0.45
    out = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
    # Lo construido se rehace desde la alternativa 2, con luz fría
    base = alternativa_2(Image.open(FOTOS / "F07.jpg").convert("RGB"))
    arq = mascara(out.size, [F07["pilar_izq"], F07["pilar_der"], F07["mojon_izq"], F07["mojon_der"]])
    d_arq = ImageDraw.Draw(arq)
    d_arq.rectangle([630, 745, 1146, 932], fill=255)
    d_arq.rectangle([743, 584, 1028, 672], fill=255)
    d_arq.rectangle([612, 524, 1150, 560], fill=255)
    gb = np.asarray(base).astype(float)
    gb = gb * 0.55 + gb.mean(axis=2, keepdims=True) * 0.3 + np.array([200, 205, 215]) * 0.15
    out.paste(Image.fromarray(np.clip(gb, 0, 255).astype("uint8")), (0, 0), arq.filter(ImageFilter.GaussianBlur(1)))
    d = ImageDraw.Draw(out)
    cerca_m = mascara_cerca(out.size)
    mojones = mascara(out.size, [F07["mojon_izq"], F07["mojon_der"]])
    cerca_m = Image.fromarray(np.where(np.asarray(mojones) > 0, 0, np.asarray(cerca_m)).astype("uint8"))
    out.paste(Image.fromarray(np.clip(gb, 0, 255).astype("uint8")), (0, 0), cerca_m)
    for ini, fin, px in TRAMOS_F07:
        postes, rieles = geom_cerca(ini, fin, px)
        for (x0, y0, x1, y1, t) in rieles[-1:]:
            d.line([x0, y0 - t / 2 - 2, x1, y1 - t / 2 - 2], fill=(240, 243, 248), width=4)
        for (x, yt, yb, w) in postes:
            d.polygon([(x - w / 2 - 1, yt + 1), (x, yt - w * 0.75), (x + w / 2 + 1, yt + 1)], fill=(240, 243, 248))
    nieve_c = (240, 243, 248)
    d.rounded_rectangle([470, 508, 1304, 526], radius=8, fill=nieve_c)
    for cap in ([(537, 480), (565, 443), (598, 455), (612, 492), (568, 466)],
                [(1150, 482), (1188, 437), (1225, 460), (1235, 492), (1190, 458)],
                [(0, 780), (40, 757), (86, 786), (88, 802), (40, 774), (0, 794)],
                [(1622, 834), (1690, 760), (1748, 822), (1750, 838), (1690, 778), (1622, 848)]):
        d.polygon(cap, fill=nieve_c)
    d.polygon([(739, 600), (885, 588), (1031, 600)], fill=nieve_c)
    return out


def noche(img):
    a = np.asarray(img).astype(float)
    a = a * 0.16 * np.array([0.8, 0.9, 1.25])
    out = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
    glow = Image.new("RGB", out.size, (0, 0, 0))
    g = ImageDraw.Draw(glow)
    # Rasante sobre el cartel desde la viga y bañadores bajos en los pilares (2700 K)
    for (cx, cy, rx, ry, k) in (
        (885, 640, 190, 80, 150),
        (579, 860, 70, 260, 110),
        (1192, 860, 70, 260, 110),
        (40, 960, 60, 60, 50),
        (1687, 990, 70, 60, 50),
    ):
        for i in range(18, 0, -1):
            f = i / 18
            col = tuple(int(c * (1 - f) ** 1.6) for c in (k * 1.9, k * 1.35, k * 0.7))
            g.ellipse([cx - rx * f, cy - ry * f, cx + rx * f, cy + ry * f], fill=col)
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    out = Image.fromarray(np.clip(np.asarray(out).astype(float) + np.asarray(glow).astype(float), 0, 255).astype("uint8"))
    # Volvemos a poner el cartel legible (iluminado)
    base = alternativa_2(Image.open(FOTOS / "F07.jpg").convert("RGB"))
    m = Image.new("L", out.size, 0)
    ImageDraw.Draw(m).rectangle([742, 598, 1028, 672], fill=255)
    lit = Image.fromarray(np.clip(np.asarray(base).astype(float) * 0.85, 0, 255).astype("uint8"))
    out.paste(lit, (0, 0), m)
    return out


# ---------------- Vista desde la ruta (F09) con alternativa 2 ----------------

def ruta_alternativa_2():
    img = Image.open(FOTOS / "F09.jpg").convert("RGB")
    cajas = [(678, 910, 727, 1032), (1132, 908, 1184, 1030), (1498, 905, 1554, 1000),
             (1542, 760, 1588, 968), (1748, 768, 1792, 968), (1946, 905, 2000, 1002)]
    a = np.asarray(img)
    hsv = np.asarray(img.convert("HSV"))
    blanco = (hsv[..., 1] < 70) & (hsv[..., 2] > 120)
    m = np.zeros(blanco.shape, dtype="uint8")
    for (x0, y0, x1, y1) in cajas:
        m[y0:y1, x0:x1] = np.where(blanco[y0:y1, x0:x1], 255, 0)
    img = teñir(img, Image.fromarray(m))
    # Pilar de medidores: zócalo de piedra hasta 0,60 m aprox. dejando libres las ventanas
    img = zocalo(img, [(40, 870), (64, 855), (130, 853), (152, 870), (152, 1000), (40, 1000)], 950)
    d = ImageDraw.Draw(img)
    # Placa "INGRESO / RECEPCIÓN" sobre el poste derecho del portón vehicular (no sobre los medidores)
    d.rectangle([700, 850, 790, 890], fill=(34, 34, 32))
    f = ImageFont.truetype(SANS, 12)
    d.text((707, 856), "INGRESO", font=f, fill=(220, 198, 140))
    d.text((707, 872), "RECEPCIÓN →", font=f, fill=(220, 198, 140))
    # Cerca de postes escuadrados entre mojones; los mojones quedan por delante
    moj = np.zeros(m.shape, dtype="uint8")
    for (x0, y0, x1, y1) in cajas[:3] + cajas[5:]:
        moj[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    cerca_travesaños(img, [((728, 1032), (1132, 1012), 45), ((1184, 1005), (1500, 978), 42),
                           ((1792, 978), (1948, 986), 40)], encima=Image.fromarray(moj))
    # Viga nueva del portal
    viga_nueva(img, 1522, 1808, 796, 814)
    cartel_tabla(img, 1666, 822, 150, 34, sub=False)
    plantas(img, [(735, 1125, 1040), (1190, 1490, 1015), (1795, 1945, 1000)], densidad=4)
    return img


def ruta_actual_anotada():
    img = Image.open(FOTOS / "F09.jpg").convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    f = ImageFont.truetype(SANS, 26)
    rotulos = [
        ((95, 925), "P0 pilar de medidores"),
        ((320, 870), "T1 tranquera vehicular"),
        ((702, 970), "M1"), ((1158, 968), "M2"), ((1526, 950), "M3"),
        ((1565, 700), "P1"), ((1770, 705), "P2"), ((1668, 870), "T2"), ((1972, 955), "M4"),
        ((560, 760), "cerco de soga"), ((1175, 690), "rollizo suelto"),
    ]
    for (x, y), t in rotulos:
        tw = d.textlength(t, font=f)
        d.rounded_rectangle([x - tw / 2 - 8, y - 18, x + tw / 2 + 8, y + 18], radius=8, fill=(20, 20, 20, 190))
        d.text((x - tw / 2, y - 15), t, font=f, fill=(255, 220, 120))
    return img


def diagnostico_portal():
    img = Image.open(FOTOS / "F07.jpg").convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    f = ImageFont.truetype(SANS, 26)
    notas = [
        ((580, 400), "P1 pilar: encalado descascarado, orificios"),
        ((1190, 395), "P2 pilar: idem"),
        ((880, 495), "V1 viga rollizo: verificar anclaje y pudrición en apoyos"),
        ((715, 1000), "T2 hoja chica con diagonal suelta"),
        ((1020, 985), "ladrillos sueltos"),
        ((70, 1060), "M5 mojón"), ((1690, 1075), "M6 mojón"),
        ((330, 760), "alambrado bajo s/ varillas"),
        ((1650, 700), "pino joven (exótico)"),
    ]
    for (x, y), t in notas:
        tw = d.textlength(t, font=f)
        x = min(max(x, tw / 2 + 12), 2000 - tw / 2 - 12)
        d.rounded_rectangle([x - tw / 2 - 8, y - 18, x + tw / 2 + 8, y + 18], radius=8, fill=(20, 20, 20, 190))
        d.text((x - tw / 2, y - 15), t, font=f, fill=(255, 220, 120))
    return img



# ---------------- Vista desde el interior (I04) con alternativa 2 ----------------

I04 = {
    "pilar_izq": [(705, 668), (735, 645), (765, 665), (775, 700), (776, 1026), (704, 1026)],
    "pilar_der": [(1205, 675), (1240, 655), (1275, 680), (1281, 720), (1279, 1028), (1202, 1028)],
    "mojones": [[(463, 872), (498, 848), (532, 870), (541, 976), (462, 976)],
                [(1392, 872), (1420, 850), (1448, 875), (1450, 956), (1391, 956)],
                [(1928, 882), (1965, 860), (2000, 880), (2000, 996), (1928, 996)]],
}


def interior_alternativa_2():
    img = Image.open(FOTOS / "I04.jpg").convert("RGB")
    m = mascara(img.size, [I04["pilar_izq"], I04["pilar_der"]] + I04["mojones"])
    img = teñir(img, m)
    img = zocalo(img, I04["pilar_izq"], 976)
    img = zocalo(img, I04["pilar_der"], 978)
    # Cara interior del portón: hoy está gris sin pintar; se pinta igual que la exterior
    a = np.asarray(img).astype(float)
    x0, y0, x1, y1 = 778, 896, 1192, 1032
    caja = a[y0:y1, x0:x1]
    mx, mn = caja.max(axis=2), caja.min(axis=2)
    madera = ((mx - mn) < 38) & (mx < 200)
    caja[madera] = caja[madera] * 0.32 + np.array([30, 24, 20]) * 0.68
    a[y0:y1, x0:x1] = caja
    img = Image.fromarray(a.astype("uint8"))
    frente = img.copy()
    viga_nueva(img, 636, 1345, 711, 749)
    # La cerca queda del lado de adentro de los mojones: se dibuja por delante
    cerca_travesaños(img, [((0, 1000), (704, 1000), 118), ((1281, 1003), (2000, 1009), 118)],
                     encima=mascara(img.size, [[(84, 700), (142, 700), (146, 1142), (84, 1142)]]))
    # Cara interior del cartel: mensaje de despedida
    d = ImageDraw.Draw(img)
    cx, yt, an, al = 990, 775, 250, 60
    for xc in (cx - an // 3, cx + an // 3):
        d.line([xc, 749, xc, yt], fill=(40, 40, 40), width=3)
    d.polygon([(cx - an // 2 - 5, yt), (cx, yt - 12), (cx + an // 2 + 5, yt)], fill=(36, 30, 26))
    d.rounded_rectangle([cx - an // 2, yt, cx + an // 2, yt + al], radius=5, fill=(58, 40, 28), outline=(32, 22, 16), width=3)
    f = ImageFont.truetype(SERIF, 24)
    t = "BUEN VIAJE"
    d.text((cx - d.textlength(t, font=f) / 2, yt + 8), t, font=f, fill=(226, 205, 160))
    f2 = ImageFont.truetype(SANS, 11)
    t2 = "GRACIAS POR ELEGIR TIERRAS MÁGICAS"
    d.text((cx - d.textlength(t2, font=f2) / 2, yt + 44), t2, font=f2, fill=(210, 190, 150))
    return img


def tina_pantalla():
    """Anota sobre I06 dónde conviene una pantalla vegetal entre la tina y la ruta."""
    img = Image.open(FOTOS / "I06.jpg").convert("RGB")
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.polygon([(130, 900), (560, 820), (1000, 760), (1150, 700), (1160, 800), (1020, 870), (600, 930), (150, 990)],
              fill=(60, 140, 70, 110), outline=(40, 110, 50, 255))
    f = ImageFont.truetype(SANS, 30)
    for i, t in enumerate(["Pantalla de nativas 1,2-1,8 m entre la tina y la ruta:",
                           "tapa tránsito y polvo, deja ver la montaña"]):
        tw = d.textlength(t, font=f)
        d.rounded_rectangle([600 - tw / 2 - 10, 640 + i * 44, 600 + tw / 2 + 10, 680 + i * 44], radius=8, fill=(20, 20, 20, 200))
        d.text((600 - tw / 2, 643 + i * 44), t, font=f, fill=(255, 220, 120))
    return Image.alpha_composite(img.convert("RGBA"), capa).convert("RGB")


# ---------------- Opciones para selección (F07) ----------------

def opcion_1():
    """Rural liviana: mojón protagonista, cerca baja de 2 travesaños."""
    CERCA.update(alturas=(0.40, 0.80), h=0.95, w=0.13, t=0.11)
    try:
        img = Image.open(FOTOS / "F07.jpg").convert("RGB")
        m = mascara(img.size, [F07["pilar_izq"], F07["pilar_der"], F07["mojon_izq"], F07["mojon_der"]])
        img = teñir(img, m)
        pintar_portero_reparado(img)
        limpiar_ladrillos(img)
        viga_nueva(img)
        cerca_travesaños(img)
        cartel_tabla(img, 885, 600, 280, 70)
        plantas(img, [(110, 520, 940), (1250, 1610, 945)], densidad=6)
    finally:
        CERCA.update(alturas=(0.35, 0.65, 0.95), h=1.15, w=0.17, t=0.13)
    return img


def opcion_3():
    """Refugio de piedra: piedra en pilares y mojones del ingreso, cerca oscura, portón nuevo."""
    CERCA["colores"] = ((52, 40, 32), (86, 68, 54), (30, 24, 20))
    try:
        img = Image.open(FOTOS / "F07.jpg").convert("RGB")
        img = zocalo(img, F07["pilar_izq"], 470)
        img = zocalo(img, F07["pilar_der"], 470)
        img = zocalo(img, F07["mojon_izq"], 760)
        img = zocalo(img, F07["mojon_der"], 760)
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = 520, 515, 1250, 566
        d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(96, 66, 44))
        d.line([x0 + 20, y0 + 9, x1 - 20, y0 + 9], fill=(140, 100, 68), width=6)
        d.ellipse([x1 - 34, y0, x1, y1], fill=(170, 128, 86), outline=(90, 60, 40), width=3)
        for x in (630, 1120):
            d.rectangle([x, 566, x + 44, 578], fill=(24, 24, 24))
            d.polygon([(x + 8, 578), (x + 36, 578), (x + 22, 606)], fill=(24, 24, 24))
        d.rectangle([630, 748, 1146, 935], fill=(28, 28, 28))
        for x in range(640, 1140, 26):
            d.rectangle([x, 758, x + 20, 925], fill=(104, 72, 48))
            d.line([x + 3, 760, x + 3, 923], fill=(132, 94, 64), width=2)
        d.line([888, 748, 888, 935], fill=(20, 20, 20), width=6)
        limpiar_ladrillos(img)
        cerca_travesaños(img)
        cartel_tabla(img, 885, 600, 280, 70)
        plantas(img, [(110, 520, 945), (1250, 1610, 950), (1760, 1995, 1040)], densidad=14)
    finally:
        CERCA.pop("colores", None)
    return img


def acceso_vehicular_op3():
    """I02: pilar de medidores y mojón M1 revestidos en piedra, cajas libres con marco."""
    img = Image.open(FOTOS / "I02.jpg").convert("RGB")
    orig = img.copy()
    pilar = [(1628, 640), (1660, 605), (1930, 600), (1966, 640), (1962, 1100), (1626, 1100)]
    img = zocalo(img, pilar, 598, piedra_px=46, lum_min=0.75)
    mojon = [(80, 790), (110, 752), (186, 760), (206, 800), (206, 1050), (82, 1050)]
    img = zocalo(img, mojon, 748, piedra_px=34, lum_min=0.8)
    d = ImageDraw.Draw(img)
    for (x0, y0, x1, y1) in ((1720, 725, 1782, 778), (1865, 722, 1933, 772), (1855, 947, 1918, 1005)):
        d.rectangle([x0 - 12, y0 - 12, x1 + 12, y1 + 12], fill=(30, 30, 30))
        img.paste(orig.crop((x0, y0, x1, y1)), (x0, y0))
    # remate de mortero en punta (descarga nieve) y placa
    d.polygon([(1622, 610), (1797, 560), (1972, 610)], fill=(150, 144, 132), outline=(90, 86, 80))
    d.polygon([(76, 760), (143, 722), (210, 760)], fill=(150, 144, 132), outline=(90, 86, 80))
    d.rectangle([1672, 836, 1918, 904], fill=(22, 22, 22), outline=(200, 170, 110), width=2)
    f = ImageFont.truetype(SERIF, 21)
    t = "TIERRAS MÁGICAS"
    d.text((1795 - d.textlength(t, font=f) / 2, 845), t, font=f, fill=(226, 205, 160))
    f2 = ImageFont.truetype(SANS, 13)
    t2 = "INGRESO · RECEPCIÓN"
    d.text((1795 - d.textlength(t2, font=f2) / 2, 875), t2, font=f2, fill=(210, 190, 150))
    plantas(img, [(1450, 1600, 1110), (230, 520, 1040)], densidad=8)
    return img

def guardar(img, nombre, ancho=1600):
    img = img.resize((ancho, int(ancho * img.height / img.width)), Image.LANCZOS)
    img.save(OUT / nombre, quality=82)
    print("ok", nombre)


if __name__ == "__main__":
    guardar(diagnostico_portal(), "00_diagnostico_portal_F07.jpg")
    guardar(ruta_actual_anotada(), "00_diagnostico_ruta_F09.jpg")
    guardar(alternativa_1(), "A1_refaccion_economica_F07.jpg")
    a2 = alternativa_2()
    guardar(a2, "A2_patagonico_natural_F07.jpg")
    guardar(alternativa_3(), "A3_refugio_premium_F07.jpg")
    guardar(a2, "A2_estacion_1_verano.jpg")
    guardar(otoño(a2), "A2_estacion_2_otono.jpg")
    guardar(invierno(a2), "A2_estacion_3_invierno.jpg")
    guardar(primavera(a2), "A2_estacion_4_primavera.jpg")
    guardar(noche(a2), "A2_noche_iluminacion.jpg")
    guardar(ruta_alternativa_2(), "A2_vista_desde_ruta_F09.jpg")
    guardar(Image.open(FOTOS / "I04.jpg"), "I04_interior_actual.jpg")
    guardar(interior_alternativa_2(), "A2_vista_desde_interior_I04.jpg")
    guardar(tina_pantalla(), "00_tina_pantalla_vegetal_I06.jpg")
    guardar(opcion_1(), "OP1_rural_liviana_F07.jpg")
    guardar(a2, "OP2_patagonico_natural_F07.jpg")
    guardar(opcion_3(), "OP3_refugio_piedra_F07.jpg")
    guardar(acceso_vehicular_op3(), "EJ_acceso_vehicular_I02.jpg")
