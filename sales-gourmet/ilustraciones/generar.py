"""Ilustraciones vectoriales de las 20 recetas (SVG, estilo gráfico con textura de acuarela).

Hechas a mano en código: formas simples, paleta común y el color de cada sal de fondo.
No usan fotos ni IA generativa. Uso, desde la raíz del repositorio:

    python3 sales-gourmet/ilustraciones/generar.py

Escribe sales-gourmet/www/img/recetas/<id>.svg (800 × 600, proporción 4:3).
"""
import math
import os
import random

SALIDA = os.path.join(os.path.dirname(__file__), "..", "www", "img", "recetas")
W, H = 800, 600
CX, CY = 400, 312

# Paleta común
P = {
    "papel": "#f6efe4", "plato": "#fbf8f2", "borde": "#ddd2c2", "sombra": "#5b4636",
    "madera": "#b58456", "madera2": "#9c6d43", "hierro": "#3b3633", "hierro2": "#54504c",
    "carne": "#7a3b2a", "carne2": "#c45d4f", "rosado": "#e08d7f", "dorado": "#d9a441", "dorado2": "#b97e2a",
    "papa": "#e8c26b", "verde": "#5f8a4a", "verde2": "#88ad5e", "limon": "#f2cf48", "limon2": "#fbe9a0",
    "crema": "#f3e6c8", "rojo": "#c8402f", "naranja": "#e48a3a", "morado": "#8b3d6e", "zapallo": "#e79a3e",
    "hongo": "#8a6142", "hongo2": "#c9a37a", "ceniza": "#4a4340", "brasa": "#f08a2c",
}
# Fondo por sal (acuarela suave del color de su etiqueta)
FONDO = {"TM-01": "#9bb592", "TM-02": "#c9bf86", "TM-03": "#8fa9c7", "TM-04": "#c99187"}


class Lienzo:
    def __init__(self, semilla):
        self.r = random.Random(semilla)
        self.capas = []

    def add(self, s):
        self.capas.append(s)

    def u(self, a, b):
        return self.r.uniform(a, b)


def defs():
    return """<defs>
  <filter id="acuarela" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="7" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="mancha" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="4" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="60" xChannelSelector="R" yChannelSelector="G"/>
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <filter id="papel">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="11"/>
    <feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.27  0 0 0 0 0.2  0 0 0 0.10 0"/>
  </filter>
  <radialGradient id="brillo" cx="35%" cy="30%" r="70%">
    <stop offset="0" stop-color="#fff" stop-opacity="0.35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </radialGradient>
</defs>"""


def fondo(L, sal):
    c = FONDO[sal]
    L.add(f'<rect width="{W}" height="{H}" fill="{P["papel"]}"/>')
    L.add(f'<g filter="url(#mancha)" opacity="0.55"><ellipse cx="{CX}" cy="{CY}" rx="360" ry="250" fill="{c}"/>'
          f'<circle cx="{L.u(90, 180)}" cy="{L.u(80, 160)}" r="{L.u(50, 90)}" fill="{c}" opacity="0.6"/>'
          f'<circle cx="{L.u(620, 720)}" cy="{L.u(440, 530)}" r="{L.u(50, 90)}" fill="{c}" opacity="0.6"/></g>')


def sombra(L, x, y, rx, ry):
    L.add(f'<ellipse cx="{x + 10}" cy="{y + 16}" rx="{rx}" ry="{ry}" fill="{P["sombra"]}" opacity="0.18" filter="url(#mancha)"/>')


def repartir(L, n, rx, ry, cx=CX, cy=CY, eliptico=True):
    """Posiciones repartidas en grilla con variación, dentro de un óvalo o rectángulo."""
    lado = math.ceil(math.sqrt(n * 1.4))
    pts = []
    for i in range(lado):
        for j in range(lado):
            x = -1 + (2 * i + 1) / lado
            y = -1 + (2 * j + 1) / lado
            if eliptico and x * x + y * y > 0.92:
                continue
            pts.append((cx + (x + L.u(-0.12, 0.12)) * rx, cy + (y + L.u(-0.12, 0.12)) * ry))
    L.r.shuffle(pts)
    return pts[:n]


# ---------- Recipientes ----------
def plato(L, r=230):
    sombra(L, CX, CY, r, r * 0.92)
    L.add(f'<g filter="url(#acuarela)"><circle cx="{CX}" cy="{CY}" r="{r}" fill="{P["plato"]}" stroke="{P["borde"]}" stroke-width="5"/>'
          f'<circle cx="{CX}" cy="{CY}" r="{r * 0.74}" fill="none" stroke="{P["borde"]}" stroke-width="3" opacity="0.7"/></g>')


def tabla(L, w=560, h=360, rot=-4):
    sombra(L, CX, CY, w / 2, h / 2)
    vetas = "".join(f'<path d="M{-w / 2 + 20} {y} q {w / 3} {L.u(-8, 8)} {w - 40} 0" stroke="{P["madera2"]}" stroke-width="2" fill="none" opacity="0.5"/>'
                    for y in range(int(-h / 2 + 30), int(h / 2 - 20), 36))
    L.add(f'<g transform="translate({CX} {CY}) rotate({rot})" filter="url(#acuarela)">'
          f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="26" fill="{P["madera"]}"/>{vetas}'
          f'<circle cx="{w / 2 - 36}" cy="{-h / 2 + 36}" r="12" fill="{P["papel"]}" opacity="0.8"/></g>')


def sarten(L, r=200, mango=True):
    sombra(L, CX, CY, r, r * 0.92)
    m = f'<rect x="{CX + r - 10}" y="{CY - 18}" width="190" height="36" rx="18" fill="{P["hierro"]}"/>' if mango else ""
    L.add(f'<g filter="url(#acuarela)">{m}<circle cx="{CX}" cy="{CY}" r="{r}" fill="{P["hierro"]}"/>'
          f'<circle cx="{CX}" cy="{CY}" r="{r - 18}" fill="{P["hierro2"]}"/></g>')


def olla(L, r=200):
    sombra(L, CX, CY, r + 30, r)
    L.add(f'<g filter="url(#acuarela)"><rect x="{CX - r - 46}" y="{CY - 20}" width="{2 * r + 92}" height="40" rx="20" fill="{P["hierro"]}"/>'
          f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="{P["hierro"]}"/><circle cx="{CX}" cy="{CY}" r="{r - 16}" fill="#6b2f22"/></g>')


def bowl(L, r=190, interior="#f1ece2"):
    sombra(L, CX, CY, r, r * 0.92)
    L.add(f'<g filter="url(#acuarela)"><circle cx="{CX}" cy="{CY}" r="{r}" fill="#e9e2d6" stroke="{P["borde"]}" stroke-width="5"/>'
          f'<circle cx="{CX}" cy="{CY}" r="{r - 22}" fill="{interior}"/></g>')


def bandeja(L, w=520, h=340):
    sombra(L, CX, CY, w / 2, h / 2)
    L.add(f'<g filter="url(#acuarela)"><rect x="{CX - w / 2}" y="{CY - h / 2}" width="{w}" height="{h}" rx="30" fill="{P["hierro"]}"/>'
          f'<rect x="{CX - w / 2 + 18}" y="{CY - h / 2 + 18}" width="{w - 36}" height="{h - 36}" rx="20" fill="{P["hierro2"]}"/></g>')


def parrilla(L, x0=150, x1=650, y0=110, y1=520):
    L.add(f'<g filter="url(#acuarela)" stroke="{P["hierro"]}" stroke-width="9" stroke-linecap="round">'
          + "".join(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}"/>' for x in range(x0, x1 + 1, 46)) + '</g>')


def brasas(L):
    L.add(f'<g filter="url(#mancha)"><rect x="40" y="300" width="720" height="290" rx="40" fill="{P["ceniza"]}"/></g>')
    g = "".join(f'<circle cx="{L.u(70, 730)}" cy="{L.u(330, 570)}" r="{L.u(8, 26)}" fill="{L.r.choice([P["brasa"], "#f6b14a", "#d9542a"])}" opacity="{L.u(0.5, 0.95):.2f}"/>' for _ in range(70))
    L.add(f'<g filter="url(#acuarela)">{g}</g>')


# ---------- Ingredientes ----------
def ramita(L, x, y, ang, largo=120, color=None, hoja=(10, 4)):
    color = color or P["verde"]
    hojas = []
    for i in range(1, 9):
        t = i / 9 * largo
        for lado in (-1, 1):
            hojas.append(f'<ellipse cx="{t}" cy="{lado * hoja[0] * 0.7}" rx="{hoja[0]}" ry="{hoja[1]}" transform="rotate({lado * 35} {t} {lado * hoja[0] * 0.7})" fill="{color}"/>')
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)"><line x1="0" y1="0" x2="{largo}" y2="0" stroke="#4d6b3a" stroke-width="3"/>{"".join(hojas)}</g>')


def hojitas(L, cx, cy, rad, n=14, color=None, tam=7):
    color = color or P["verde2"]
    s = "".join(f'<ellipse cx="{cx + L.u(-rad, rad):.0f}" cy="{cy + L.u(-rad, rad):.0f}" rx="{tam}" ry="{tam * 0.55:.1f}" transform="rotate({L.u(0, 180):.0f} {cx} {cy})" fill="{color}" opacity="0.9"/>' for _ in range(n))
    L.add(f'<g filter="url(#acuarela)">{s}</g>')


def puntos(L, cx, cy, rad, n=40, color="#3b2a20", r=(1.5, 3)):
    s = "".join(f'<circle cx="{cx + L.u(-rad, rad):.0f}" cy="{cy + L.u(-rad, rad):.0f}" r="{L.u(*r):.1f}" fill="{color}" opacity="0.7"/>' for _ in range(n))
    L.add(f"<g>{s}</g>")


def limon_gajo(L, x, y, ang, tam=60):
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)">'
          f'<path d="M{-tam} 0 A{tam} {tam} 0 0 0 {tam} 0 Z" fill="{P["limon"]}"/>'
          f'<path d="M{-tam + 9} 0 A{tam - 9} {tam - 9} 0 0 0 {tam - 9} 0 Z" fill="{P["limon2"]}"/>'
          + "".join(f'<line x1="0" y1="0" x2="{(tam - 12) * math.cos(math.radians(a)):.0f}" y2="{(tam - 12) * math.sin(math.radians(a)):.0f}" stroke="{P["limon"]}" stroke-width="3"/>' for a in (30, 60, 90, 120, 150))
          + "</g>")


def limon_rodaja(L, x, y, r=34):
    L.add(f'<g filter="url(#acuarela)"><circle cx="{x}" cy="{y}" r="{r}" fill="{P["limon"]}"/><circle cx="{x}" cy="{y}" r="{r - 7}" fill="{P["limon2"]}"/>'
          + "".join(f'<line x1="{x}" y1="{y}" x2="{x + (r - 9) * math.cos(math.radians(a)):.0f}" y2="{y + (r - 9) * math.sin(math.radians(a)):.0f}" stroke="{P["limon"]}" stroke-width="3"/>' for a in range(0, 360, 45))
          + "</g>")


def feta_carne(L, x, y, ang, w=70, h=150, borde=None, centro=None, marcas=True):
    borde, centro = borde or P["carne"], centro or P["carne2"]
    m = "".join(f'<line x1="{-w / 2 + 6}" y1="{yy}" x2="{w / 2 - 6}" y2="{yy - 18}" stroke="#3a1c14" stroke-width="5" opacity="0.6"/>' for yy in range(int(-h / 2 + 25), int(h / 2), 34)) if marcas else ""
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)">'
          f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="{w / 3}" fill="{borde}"/>'
          f'<rect x="{-w / 2 + 9}" y="{-h / 2 + 9}" width="{w - 18}" height="{h - 18}" rx="{w / 4}" fill="{centro}"/>{m}</g>')


def papa(L, x, y, r=34, color=None, piel=True):
    color = color or P["papa"]
    rx, ry = r * L.u(0.9, 1.25), r * L.u(0.75, 1.0)
    L.add(f'<g filter="url(#acuarela)"><ellipse cx="{x}" cy="{y}" rx="{rx:.0f}" ry="{ry:.0f}" transform="rotate({L.u(0, 180):.0f} {x} {y})" fill="{P["dorado2"] if piel else color}"/>'
          f'<ellipse cx="{x - 3}" cy="{y - 3}" rx="{rx * 0.8:.0f}" ry="{ry * 0.75:.0f}" transform="rotate({L.u(0, 180):.0f} {x} {y})" fill="{color}"/>'
          f'<ellipse cx="{x - rx * 0.3:.0f}" cy="{y - ry * 0.3:.0f}" rx="{rx * 0.35:.0f}" ry="{ry * 0.2:.0f}" fill="#fff" opacity="0.25"/></g>')


def hongo(L, x, y, s=1.0, ang=0):
    L.add(f'<g transform="translate({x} {y}) rotate({ang}) scale({s})" filter="url(#acuarela)">'
          f'<path d="M-34 0 Q-34 -34 0 -36 Q34 -34 34 0 Z" fill="{P["hongo"]}"/>'
          f'<path d="M-26 -2 Q0 8 26 -2 L22 4 Q0 12 -22 4 Z" fill="{P["hongo2"]}"/>'
          f'<path d="M-10 2 L-12 34 Q0 40 12 34 L10 2 Z" fill="{P["hongo2"]}"/>'
          f'<path d="M-20 -18 q12 -10 24 -12" stroke="#fff" stroke-width="4" opacity="0.25" fill="none"/></g>')


def morron(L, x, y, ang, color, largo=90):
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)">'
          f'<path d="M0 0 C{largo * 0.3} {-largo * 0.42:.0f} {largo * 0.7} {-largo * 0.42:.0f} {largo} 0 C{largo * 0.7} {-largo * 0.16:.0f} {largo * 0.3} {-largo * 0.16:.0f} 0 0 Z" fill="{color}"/>'
          f'<path d="M{largo * 0.2} {-largo * 0.14:.0f} C{largo * 0.4} {-largo * 0.26:.0f} {largo * 0.6} {-largo * 0.26:.0f} {largo * 0.8} {-largo * 0.14:.0f}" stroke="#fff" stroke-width="4" opacity="0.3" fill="none"/></g>')


def rodaja_zucchini(L, x, y, r=26):
    L.add(f'<g filter="url(#acuarela)"><circle cx="{x}" cy="{y}" r="{r}" fill="#4f7a3a"/><circle cx="{x}" cy="{y}" r="{r - 6}" fill="#dfe6b0"/>'
          f'<circle cx="{x}" cy="{y}" r="{r * 0.35:.0f}" fill="#c9d48f"/><line x1="{x - r + 8}" y1="{y + 4}" x2="{x + r - 8}" y2="{y - 6}" stroke="#6b5a2a" stroke-width="3" opacity="0.6"/></g>')


def cubo(L, x, y, l, color, ang=0, sombra_c=None):
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)"><rect x="{-l / 2}" y="{-l / 2}" width="{l}" height="{l}" rx="{l / 5}" fill="{color}"/>'
          f'<rect x="{-l / 2 + 4}" y="{-l / 2 + 4}" width="{l * 0.5}" height="{l * 0.3}" rx="3" fill="#fff" opacity="0.25"/></g>')


def cebolla_morada(L, x, y, ang, r=40):
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)" fill="none" stroke-linecap="round">'
          f'<path d="M{-r} 0 A{r} {r} 0 0 1 {r} 0" stroke="{P["morado"]}" stroke-width="9"/>'
          f'<path d="M{-r + 14} 0 A{r - 14} {r - 14} 0 0 1 {r - 14} 0" stroke="#c98fb4" stroke-width="7"/></g>')


def langostino(L, x, y, ang, s=1.0):
    seg = "".join(f'<path d="M0 0 m{30 * math.cos(math.radians(a)):.0f} {30 * math.sin(math.radians(a)):.0f} l{12 * math.cos(math.radians(a)):.0f} {12 * math.sin(math.radians(a)):.0f}" stroke="#f6c09a" stroke-width="3"/>' for a in range(200, 340, 25))
    L.add(f'<g transform="translate({x} {y}) rotate({ang}) scale({s})" filter="url(#acuarela)">'
          f'<path d="M-36 0 A36 36 0 1 1 30 18" stroke="{P["naranja"]}" stroke-width="22" fill="none" stroke-linecap="round"/>{seg}'
          f'<path d="M30 18 l18 10 l-4 -18 z" fill="#d9642a"/></g>')


def choclo(L, x, y, ang, largo=170):
    g = "".join(f'<circle cx="{i}" cy="{j}" r="6" fill="{P["limon"]}" stroke="{P["dorado2"]}" stroke-width="1.5"/>' for i in range(14, largo - 10, 14) for j in (-14, 0, 14))
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)"><rect x="0" y="-26" width="{largo}" height="52" rx="26" fill="{P["dorado"]}"/>{g}'
          + "".join(f'<line x1="{i}" y1="-24" x2="{i + 10}" y2="24" stroke="#3a1c14" stroke-width="6" opacity="0.45"/>' for i in range(30, largo - 20, 40)) + "</g>")


def tira_zucchini(L, x, y, ang, largo=170):
    L.add(f'<g transform="translate({x} {y}) rotate({ang})" filter="url(#acuarela)"><rect x="0" y="-18" width="{largo}" height="36" rx="16" fill="#4f7a3a"/>'
          f'<rect x="6" y="-12" width="{largo - 12}" height="24" rx="12" fill="#dfe6b0"/>'
          + "".join(f'<line x1="{i}" y1="-12" x2="{i + 8}" y2="12" stroke="#3a1c14" stroke-width="5" opacity="0.5"/>' for i in range(24, largo - 10, 32)) + "</g>")


def eneldo(L, cx, cy, n=6):
    for _ in range(n):
        x, y, a = cx + L.u(-60, 60), cy + L.u(-50, 50), L.u(0, 360)
        L.add(f'<g transform="translate({x:.0f} {y:.0f}) rotate({a:.0f})" filter="url(#acuarela)" stroke="{P["verde"]}" stroke-width="2.2" fill="none">'
              + "".join(f'<path d="M0 0 l{20 * math.cos(math.radians(b)):.0f} {20 * math.sin(math.radians(b)):.0f}"/>' for b in range(-60, 61, 20)) + "</g>")


def salero(L, x, y, color):
    """Cuenquito de sal con el color de la sal de la receta (toque de identidad)."""
    L.add(f'<g filter="url(#acuarela)"><ellipse cx="{x + 4}" cy="{y + 8}" rx="44" ry="40" fill="{P["sombra"]}" opacity="0.15"/>'
          f'<circle cx="{x}" cy="{y}" r="40" fill="#efe7da" stroke="{P["borde"]}" stroke-width="4"/>'
          f'<circle cx="{x}" cy="{y}" r="30" fill="#faf6ee"/></g>')
    puntos(L, x, y, 18, 30, color, (1.6, 3.2))


# ---------- Composiciones por receta ----------
def r_bife(L):
    tabla(L)
    for i in range(6):
        feta_carne(L, 260 + i * 52, 300 + i * 4, 12, 58, 170)
    ramita(L, 520, 420, -20, 140)
    salero(L, 650, 150, "#355a3a")


def r_ciervo(L):
    plato(L)
    for i in range(5):
        feta_carne(L, 300 + i * 38, 300, 20, 54, 150, "#4a1f1a", "#9e3b3b")
    for (x, y) in [(470, 230), (520, 300), (480, 370), (440, 420), (540, 390)]:
        papa(L, x, y, 32)
    L.add(f'<path d="M250 400 q60 30 120 0" stroke="#5a1e2c" stroke-width="16" fill="none" opacity="0.7" filter="url(#acuarela)"/>')
    ramita(L, 360, 200, 25, 110, P["verde"], (8, 3))


def r_jabali(L):
    olla(L)
    pts = repartir(L, 16, 140, 140)
    for x, y in pts[:10]:
        cubo(L, x, y, L.u(50, 64), L.r.choice(["#9a5038", "#b0644a", "#8a4430"]), L.u(0, 90))
    for x, y in pts[10:]:
        hongo(L, x, y, 0.95, L.u(-30, 30))
    hojitas(L, CX, CY, 120, 18, P["verde2"], 6)


def r_hongos(L):
    sarten(L)
    for x, y in repartir(L, 10, 130, 130):
        hongo(L, x, y, L.u(1.2, 1.45), L.u(-40, 40))
    hojitas(L, CX, CY, 130, 26, P["verde"], 6)


def r_papas(L):
    bandeja(L)
    for x, y in repartir(L, 16, 205, 125, eliptico=False):
        papa(L, x, y, L.u(30, 38))
    ramita(L, 250, 210, 15, 150)
    ramita(L, 450, 410, -25, 150)
    puntos(L, CX, CY, 200, 50, "#f8f2e4", (1.5, 3))


def r_risotto(L):
    plato(L)
    L.add(f'<g filter="url(#acuarela)"><circle cx="{CX}" cy="{CY}" r="150" fill="{P["crema"]}"/></g>')
    s = "".join(f'<ellipse cx="{CX + L.u(-130, 130):.0f}" cy="{CY + L.u(-130, 130):.0f}" rx="7" ry="3.5" transform="rotate({L.u(0, 180):.0f} {CX} {CY})" fill="#fbf4df" stroke="#e2cf9f" stroke-width="1"/>' for _ in range(260))
    L.add(f'<g clip-path="circle(140px at {CX}px {CY}px)">{s}</g>')
    for _ in range(6):
        hongo(L, CX + L.u(-90, 90), CY + L.u(-90, 90), 0.65, L.u(-30, 30))
    L.add('<g filter="url(#acuarela)">' + "".join(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + 16:.0f}" y2="{y + L.u(-6, 6):.0f}" stroke="{P["verde"]}" stroke-width="4" stroke-linecap="round"/>' for x, y in [(CX + L.u(-110, 110), CY + L.u(-110, 110)) for _ in range(18)]) + "</g>")


def r_huevos(L):
    tabla(L, 520, 340, 3)
    L.add(f'<g filter="url(#acuarela)"><rect x="210" y="200" width="380" height="230" rx="40" fill="#c99456"/><rect x="226" y="214" width="348" height="202" rx="32" fill="#e7c48c"/></g>')
    L.add(f'<g filter="url(#mancha)"><ellipse cx="{CX}" cy="{CY}" rx="150" ry="90" fill="#f6d35b"/></g>')
    for _ in range(9):
        L.add(f'<g filter="url(#acuarela)"><ellipse cx="{CX + L.u(-120, 120):.0f}" cy="{CY + L.u(-60, 60):.0f}" rx="{L.u(18, 30):.0f}" ry="{L.u(12, 18):.0f}" fill="#fbe58e"/></g>')
    L.add('<g filter="url(#acuarela)">' + "".join(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + 14:.0f}" y2="{y + L.u(-5, 5):.0f}" stroke="{P["verde"]}" stroke-width="4" stroke-linecap="round"/>' for x, y in [(CX + L.u(-130, 130), CY + L.u(-70, 70)) for _ in range(22)]) + "</g>")


def r_noquis(L):
    plato(L)
    for _ in range(22):
        x, y, a = CX + L.u(-140, 140), CY + L.u(-140, 140), L.u(0, 180)
        if math.hypot(x - CX, y - CY) > 150:
            continue
        L.add(f'<g transform="translate({x:.0f} {y:.0f}) rotate({a:.0f})" filter="url(#acuarela)"><ellipse rx="26" ry="17" fill="#f2dca0"/>'
              + "".join(f'<line x1="{i}" y1="-13" x2="{i}" y2="13" stroke="#d6b66a" stroke-width="2.5"/>' for i in (-12, -4, 4, 12)) + "</g>")
    L.add(f'<g filter="url(#mancha)" opacity="0.5"><circle cx="{CX - 40}" cy="{CY + 20}" r="70" fill="#f0c95a"/></g>')
    hojitas(L, CX, CY, 140, 20, P["verde"], 8)
    puntos(L, CX, CY, 140, 60, "#fffdf4", (2, 4))


def r_vegetales_asados(L):
    bandeja(L, 540, 350)
    cols = [P["rojo"], P["limon"], P["zapallo"], P["morado"]]
    pts = repartir(L, 22, 205, 120, eliptico=False)
    for x, y in pts[:6]:
        morron(L, x - 50, y, L.u(0, 360), L.r.choice(cols[:2]), L.u(100, 120))
    for x, y in pts[6:12]:
        cubo(L, x, y, 54, P["zapallo"], L.u(0, 90))
    for x, y in pts[12:17]:
        rodaja_zucchini(L, x, y, 34)
    for x, y in pts[17:]:
        cebolla_morada(L, x, y, L.u(0, 360), 42)
    hojitas(L, CX, CY, 200, 18, P["verde"], 7)


def r_focaccia(L):
    tabla(L, 580, 380, -3)
    L.add(f'<g transform="translate({CX} {CY}) rotate(-3)" filter="url(#acuarela)"><rect x="-230" y="-140" width="460" height="280" rx="50" fill="{P["dorado2"]}"/>'
          f'<rect x="-216" y="-126" width="432" height="252" rx="44" fill="{P["dorado"]}"/></g>')
    s = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{P["dorado2"]}" opacity="0.8"/>' for x in range(CX - 180, CX + 190, 52) for y in range(CY - 95, CY + 100, 48))
    L.add(f'<g filter="url(#acuarela)">{s}</g>')
    for _ in range(6):
        ramita(L, CX + L.u(-180, 120), CY + L.u(-90, 90), L.u(0, 360), 60, P["verde"], (7, 2.5))
    puntos(L, CX, CY, 190, 70, "#fbf4e2", (1.6, 3.4))


def r_ceviche(L):
    bowl(L, 200, "#efe1c4")
    for x, y in repartir(L, 18, 135, 135):
        cubo(L, x, y, L.u(44, 54), L.r.choice(["#fbf6ee", "#f2cfc0", "#f6e2d6"]), L.u(0, 90))
    for x, y in repartir(L, 6, 120, 120):
        cebolla_morada(L, x, y, L.u(0, 360), L.u(30, 38))
    hojitas(L, CX, CY, 120, 22, P["verde"], 8)
    limon_gajo(L, 620, 470, -20, 56)
    limon_rodaja(L, 180, 150, 36)


def r_pollo(L):
    plato(L)
    for i in range(5):
        feta_carne(L, 300 + i * 46, 300, 18, 56, 170, "#c98a4b", "#f1dcb6")
    limon_gajo(L, 520, 210, 30, 52)
    ramita(L, 280, 430, -10, 120, P["verde"], (8, 3))
    puntos(L, CX, CY, 120, 40)


def r_langostinos(L):
    plato(L)
    for i in range(7):
        a = i / 7 * 360
        langostino(L, CX + 100 * math.cos(math.radians(a)), CY + 100 * math.sin(math.radians(a)), a + 90, 0.85)
    limon_gajo(L, CX, CY + 10, 0, 50)
    eneldo(L, CX, CY, 7)


def r_veg_parrilla(L):
    parrilla(L)
    choclo(L, 170, 190, 6, 250)
    tira_zucchini(L, 170, 330, -5, 250)
    tira_zucchini(L, 200, 430, 3, 240)
    morron(L, 450, 250, 8, P["rojo"], 200)
    morron(L, 460, 380, -8, P["limon"], 180)
    eneldo(L, 520, 470, 6)
    L.add(f'<g filter="url(#acuarela)"><circle cx="680" cy="150" r="36" fill="{P["limon"]}" opacity="0.9"/></g>')


def r_asado(L):
    parrilla(L, 120, 680, 120, 500)
    for k, y in enumerate((230, 360)):
        L.add(f'<g filter="url(#acuarela)"><rect x="150" y="{y - 52}" width="500" height="104" rx="36" fill="{P["carne"]}"/>'
              f'<rect x="162" y="{y - 40}" width="476" height="80" rx="28" fill="#9a4a35"/></g>')
        for x in range(190, 640, 82):
            L.add(f'<g filter="url(#acuarela)"><ellipse cx="{x + k * 20}" cy="{y}" rx="18" ry="22" fill="#efe3cf"/><ellipse cx="{x + k * 20}" cy="{y}" rx="9" ry="12" fill="#d8c3a2"/></g>')
    puntos(L, 400, 300, 240, 60, "#f2e6d4", (1.5, 3))


def r_cordero(L):
    brasas(L)
    L.add(f'<g filter="url(#acuarela)" stroke="{P["hierro"]}" stroke-width="16" stroke-linecap="round">'
          f'<line x1="400" y1="40" x2="400" y2="560"/><line x1="230" y1="180" x2="570" y2="180"/><line x1="260" y1="400" x2="540" y2="400"/></g>')
    L.add(f'<g filter="url(#acuarela)"><path d="M270 170 Q240 290 290 410 Q400 470 510 410 Q560 290 530 170 Q400 120 270 170 Z" fill="#8a4a2a"/>'
          f'<path d="M300 190 Q280 290 315 385 Q400 430 485 385 Q520 290 500 190 Q400 150 300 190 Z" fill="#b8693d"/></g>')
    L.add('<g filter="url(#acuarela)" stroke="#f3e6d2" stroke-width="7" stroke-linecap="round" opacity="0.8">'
          + "".join(f'<line x1="{340 + i * 30}" y1="{220 + abs(i - 2) * 6}" x2="{335 + i * 30}" y2="{370 - abs(i - 2) * 6}"/>' for i in range(5)) + "</g>")
    for x in (150, 250, 560, 660):
        L.add(f'<g filter="url(#mancha)" opacity="0.8"><path d="M{x} 470 q-30 -70 0 -140 q30 70 0 140" fill="#f6b14a"/></g>')


def r_bondiola(L):
    tabla(L)
    for i in range(6):
        x = 250 + i * 54
        L.add(f'<g transform="translate({x} 310) rotate(10)" filter="url(#acuarela)"><ellipse rx="40" ry="92" fill="#8a4a2a"/>'
              f'<ellipse rx="32" ry="82" fill="#e7b39a"/><path d="M-20 -40 q20 30 0 80" stroke="#f6dccc" stroke-width="6" fill="none" opacity="0.8"/></g>')
    ramita(L, 520, 430, -15, 120)
    L.add(f'<path d="M230 440 q90 26 200 0" stroke="#6a2a2f" stroke-width="14" fill="none" opacity="0.6" filter="url(#acuarela)"/>')


def r_veg_rescoldo(L):
    brasas(L)
    for x, y in [(250, 330), (520, 340)]:
        L.add(f'<g filter="url(#acuarela)"><circle cx="{x}" cy="{y}" r="78" fill="#3a2a22"/><circle cx="{x}" cy="{y}" r="58" fill="#d9a06a"/>'
              f'<circle cx="{x}" cy="{y}" r="40" fill="#e9c08f"/><circle cx="{x}" cy="{y}" r="22" fill="#f3d8b0"/></g>')
    morron(L, 300, 500, -8, "#a8291c", 210)
    L.add(f'<g filter="url(#acuarela)"><path d="M540 490 q90 -100 200 0 q-100 60 -200 0" fill="{P["zapallo"]}"/><path d="M565 490 q75 -70 150 0" stroke="#f6c37a" stroke-width="14" fill="none"/></g>')
    puntos(L, 400, 380, 280, 60, "#1e1714", (2, 4))
    hojitas(L, 260, 320, 40, 10, P["verde2"], 6)


def r_papas_rescoldo(L):
    brasas(L)
    for x, y, s in [(270, 330, 1.0), (530, 350, 0.95)]:
        L.add(f'<g transform="translate({x} {y}) scale({s})" filter="url(#acuarela)">'
              f'<path d="M-120 20 L-90 -70 L0 -40 L90 -75 L125 20 L80 90 L-80 90 Z" fill="#c9cdd2"/>'
              f'<path d="M-100 20 L-75 -50 L0 -25 L75 -55 L105 20 L65 75 L-65 75 Z" fill="#e3e6ea"/>'
              f'<ellipse cx="0" cy="12" rx="78" ry="55" fill="{P["dorado2"]}"/><ellipse cx="0" cy="8" rx="64" ry="44" fill="#f2df9e"/>'
              f'<path d="M-40 -10 q20 50 0 70 M10 -14 q-14 40 6 66 M40 -6 q14 30 -6 54" stroke="#fff3c4" stroke-width="12" fill="none" stroke-linecap="round"/>'
              f'<rect x="-14" y="-6" width="26" height="20" rx="4" fill="#fbe8a6"/></g>')
    hojitas(L, 270, 320, 40, 8, P["verde"], 6)
    hojitas(L, 530, 340, 40, 8, P["verde"], 6)


def r_trucha(L):
    tabla(L, 600, 340, -2)
    L.add(f'<g transform="translate({CX - 20} {CY}) rotate(-6)" filter="url(#acuarela)">'
          f'<path d="M-240 0 Q-120 -100 120 -60 Q200 -40 230 0 Q200 40 120 60 Q-120 100 -240 0 Z" fill="#7d8a7a"/>'
          f'<path d="M-200 10 Q-80 70 120 45 Q190 30 215 5 Q100 22 -200 10 Z" fill="#e7a58f"/>'
          f'<path d="M230 0 L300 -60 L285 0 L300 60 Z" fill="#6b776a"/>'
          f'<circle cx="-190" cy="-14" r="10" fill="#f6efe4"/><circle cx="-190" cy="-14" r="5" fill="#2b2420"/>'
          + "".join(f'<circle cx="{L.u(-150, 180):.0f}" cy="{L.u(-50, 10):.0f}" r="{L.u(3, 6):.1f}" fill="#3b4038" opacity="0.7"/>' for _ in range(28))
          + "".join(f'<line x1="{x}" y1="-60" x2="{x + 30}" y2="60" stroke="#3a2a20" stroke-width="7" opacity="0.45"/>' for x in range(-120, 160, 60))
          + "</g>")
    limon_rodaja(L, 230, 450, 32)
    limon_rodaja(L, 300, 470, 28)
    eneldo(L, 560, 430, 6)


COMPOSICIONES = {
    "bife-chorizo-fogon": ("TM-01", r_bife), "ciervo-papas": ("TM-01", r_ciervo), "jabali-hongos": ("TM-01", r_jabali),
    "hongos-salteados": ("TM-01", r_hongos), "papas-horno-romero": ("TM-01", r_papas),
    "risotto-hongos": ("TM-02", r_risotto), "huevos-ciboulette": ("TM-02", r_huevos), "noquis-hierbas": ("TM-02", r_noquis),
    "vegetales-asados": ("TM-02", r_vegetales_asados), "focaccia-hierbas": ("TM-02", r_focaccia),
    "trucha-parrilla": ("TM-03", r_trucha), "ceviche-trucha": ("TM-03", r_ceviche), "pollo-limon": ("TM-03", r_pollo),
    "langostinos-plancha": ("TM-03", r_langostinos), "vegetales-parrilla-eneldo": ("TM-03", r_veg_parrilla),
    "asado-tira": ("TM-04", r_asado), "cordero-cruz": ("TM-04", r_cordero), "bondiola-horno": ("TM-04", r_bondiola),
    "vegetales-rescoldo": ("TM-04", r_veg_rescoldo), "papas-rescoldo": ("TM-04", r_papas_rescoldo),
}


def generar():
    os.makedirs(SALIDA, exist_ok=True)
    for i, (rid, (sal, fn)) in enumerate(COMPOSICIONES.items()):
        L = Lienzo(1000 + i)
        fondo(L, sal)
        fn(L)
        L.add(f'<rect width="{W}" height="{H}" filter="url(#papel)"/>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Ilustración: {rid}">'
               + defs() + "".join(L.capas) + "</svg>\n")
        with open(os.path.join(SALIDA, f"{rid}.svg"), "w") as f:
            f.write(svg)
    print(f"{len(COMPOSICIONES)} ilustraciones en {os.path.normpath(SALIDA)}")


if __name__ == "__main__":
    generar()
