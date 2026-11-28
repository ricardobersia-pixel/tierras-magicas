"""Proyecto ejecutivo del acceso de Tierras Mágicas: opción 3 «Refugio de piedra» con la tabla tallada.

Genera:
  proyecto_ejecutivo.html               página completa (memoria, planos, paisajismo, detalles, cómputo, obra)
  lista_compras_proyecto_ejecutivo.xlsx  cómputo con columnas de precio para cotizar
Uso: python3 docs/acceso/generar_ejecutivo.py
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

import generar_opciones as G

BASE = Path(__file__).resolve().parent
OP = dict(G.OPCIONES[3], cartel="tabla", luces=6, mojon_piedra=tuple(G.MOJONES), color_cerca=G.MAD_NATURAL)

# ======================================================================
# PAISAJISMO
# ======================================================================
ESPECIES = {
    "CO": dict(nombre="Coirón blanco", cientifico="Festuca pallescens", tipo="Gramínea perenne", alto="0,3-0,5 m",
               flor="—", fuerte="Otoño-invierno: matas pajizas", color="#b9b27a", env="1 L", dist="0,5 m",
               nota="Base de todos los canteros. Rústica, sin riego después del 2.º año."),
    "CH": dict(nombre="Chaura", cientifico="Gaultheria mucronata", tipo="Arbusto bajo perenne", alto="0,3-0,6 m",
               flor="Blanca, primavera", fuerte="Otoño-invierno: bayas rosadas y blancas", color="#3f6b3a", env="1-3 L", dist="0,6 m",
               nota="Verde todo el año; aguanta media sombra."),
    "AM": dict(nombre="Amancay", cientifico="Alstroemeria aurea", tipo="Herbácea perenne con bulbo", alto="0,4-0,8 m",
               flor="Naranja y amarilla, dic-feb", fuerte="Verano", color="#e98a1e", env="1 L", dist="0,4 m (grupos de 3)",
               nota="Flor emblema de la zona. Desaparece en invierno y rebrota. Reemplaza al lupino."),
    "FR": dict(nombre="Frutilla silvestre", cientifico="Fragaria chiloensis", tipo="Cubresuelo rastrero", alto="0,1-0,2 m",
               flor="Blanca, primavera", fuerte="Primavera-verano", color="#86b064", env="maceta 0,5 L", dist="0,3 m",
               nota="Cubre el suelo y frena la erosión. Solo donde no se pisa. Confirmar procedencia andina."),
    "CA": dict(nombre="Calafate", cientifico="Berberis microphylla", tipo="Arbusto espinoso", alto="0,8-1,2 m",
               flor="Amarilla, oct-nov", fuerte="Primavera; fruto azul en verano", color="#d7b52a", env="3 L", dist="1,2 m",
               nota="Contra la cerca, del lado de adentro. Espinoso: lejos de sendero y atrio."),
    "SC": dict(nombre="Siete camisas", cientifico="Escallonia virgata", tipo="Arbusto caducifolio", alto="0,8-1,5 m",
               flor="Blanca, dic-ene", fuerte="Otoño: hoja rojiza", color="#f2efe6", env="3 L", dist="1,2 m",
               nota="Aporta color otoñal junto a los ñires."),
    "CI": dict(nombre="Chilco", cientifico="Fuchsia magellanica", tipo="Arbusto de flor", alto="0,8-1,5 m",
               flor="Roja y violeta, dic-mar", fuerte="Verano", color="#c0275a", env="3 L", dist="1,0 m",
               nota="Necesita humedad: solo con goteo. Del lado de adentro de los pilares del portal."),
    "MU": dict(nombre="Mutisia", cientifico="Mutisia spinosa", tipo="Trepadora", alto="apoyada 1-2 m",
               flor="Rosada a naranja, verano", fuerte="Verano", color="#ef7c5a", env="3 L", dist="1 por pirca",
               nota="Se apoya en la pirca. Confirmar disponibilidad en el vivero."),
    "MI": dict(nombre="Michay", cientifico="Berberis darwinii", tipo="Arbusto perenne", alto="1,0-2,0 m",
               flor="Naranja, oct-nov", fuerte="Primavera", color="#d4661c", env="3-5 L", dist="1,2 m",
               nota="Pantalla de la tina."),
    "NO": dict(nombre="Notro", cientifico="Embothrium coccineum", tipo="Arbusto o arbolito", alto="2-4 m",
               flor="Roja intensa, nov-dic", fuerte="Primavera", color="#b3201c", env="3-5 L", dist="2,5 m",
               nota="Solo en la pantalla de la tina, lejos de la cerca."),
    "PP": dict(nombre="Palo piche", cientifico="Fabiana imbricata", tipo="Arbusto", alto="0,8-1,5 m",
               flor="Blanca a lila, nov-dic", fuerte="Fin de primavera", color="#c9b4d6", env="3 L", dist="1,2 m",
               nota="Tolera suelo pobre y seco."),
    "AR": dict(nombre="Araucaria (pehuén)", cientifico="Araucaria araucana", tipo="Árbol emblema", alto="lento, 10-20 cm por año",
               flor="—", fuerte="Todo el año", color="#2d4a2a", env="ejemplar de vivero", dist="ejemplar aislado",
               nota="Hito al final del sendero, a más de 4 m de construcciones y cables. Solo de vivero autorizado."),
}

# Cantidades por zona (plantas)
ZONAS = [
    ("Z1", "Faja del frente, módulo B (5 tramos: M2-M3, M4-M5, M5-M6, M6-M7, M7-M8)", "1,2 × 5,55 m por tramo",
     {"CO": 25, "CH": 15, "AM": 30, "CA": 5, "SC": 5}),
    ("Z2", "Faja del frente junto a la tranquera, módulo A bajo (M0-medidores y M1-M2)", "1,2 × 5,5 m por tramo",
     {"CO": 10, "CH": 8, "FR": 12, "AM": 6}),
    ("Z3", "Pircas y pilares del portal (lado de adentro)", "≈ 8 m²",
     {"CI": 2, "MU": 2, "FR": 10, "AM": 6}),
    ("Z4", "Lado de adentro del acceso vehicular y pilar de medidores", "≈ 6 m²",
     {"CO": 6, "FR": 10}),
    ("Z5", "Bordes del sendero peatonal (≈ 30 m)", "0,5 m por lado",
     {"CH": 10, "AM": 10, "FR": 20, "AR": 1}),
    ("Z6", "Pantalla vegetal de la tina (≈ 12 m)", "1,5 m de ancho",
     {"MI": 4, "NO": 2, "SC": 3, "PP": 3}),
    ("Z7", "Cerco del camino interno (≈ 50 m)", "puntual",
     {"CA": 6}),
]


def totales_especies():
    tot = {k: 0 for k in ESPECIES}
    for _, _, _, d in ZONAS:
        for k, v in d.items():
            tot[k] += v
    return tot


def simbolo(x, y, cod, r=None):
    e = ESPECIES[cod]
    r = r or {"CO": 6, "CH": 6, "AM": 5, "FR": 4, "CA": 9, "SC": 9, "CI": 8, "MU": 7, "MI": 10, "NO": 12, "PP": 9, "AR": 13}[cod]
    borde = "#555" if cod in ("SC", "PP") else "rgba(0,0,0,.35)"
    txt = "#222" if cod in ("SC", "PP", "CO", "FR", "CA") else "#fff"
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{e["color"]}" stroke="{borde}"/>'
            f'<text x="{x:.1f}" y="{y + 3:.1f}" text-anchor="middle" font-size="{max(6, r - 1)}" font-weight="600" fill="{txt}">{cod}</text>')


def modulo(tipo):
    """Módulo de plantación tipo por tramo de 6 m (escala 1 m = 70 px)."""
    S, X0, Y0 = 70, 40, 60
    W, H = 5.55, 1.2
    g = [f'<rect width="{X0 * 2 + W * S:.0f}" height="{Y0 + H * S + 90:.0f}" fill="var(--surface)"/>']
    g.append(f'<rect x="{X0}" y="{Y0}" width="{W * S}" height="{H * S}" fill="#c8b48a" opacity=".35"/>')
    g.append(f'<line x1="{X0 - 30}" y1="{Y0 + H * S}" x2="{X0 + W * S + 30}" y2="{Y0 + H * S}" stroke="{OP["color_cerca"]}" stroke-width="6"/>')
    for i in range(3):
        x = X0 + (0.08 + (W - 0.16) * i / 2) * S
        g.append(f'<rect x="{x - 4}" y="{Y0 + H * S - 4}" width="8" height="8" fill="{OP["color_cerca"]}"/>')
    g.append(f'<rect x="{X0 - 32}" y="{Y0 + H * S - 2}" width="32" height="32" fill="#9a948a" stroke="#4a4640"/>')
    g.append(f'<rect x="{X0 + W * S}" y="{Y0 + H * S - 2}" width="32" height="32" fill="#9a948a" stroke="#4a4640"/>')
    g.append(f'<text x="{X0 + W * S / 2}" y="{Y0 + H * S + 22}" text-anchor="middle" font-size="12" fill="var(--muted)">línea de cerca · banquina hacia abajo</text>')
    g.append(f'<text x="{X0 + W * S / 2}" y="{Y0 - 10}" text-anchor="middle" font-size="12" fill="var(--muted)">interior del lote</text>')

    def P(xm, ym, c):
        g.append(simbolo(X0 + xm * S, Y0 + ym * S, c, r={"CO": 11, "CH": 12, "AM": 9, "FR": 8, "CA": 17, "SC": 17}[c]))
    if tipo == "B":
        for xm in (1.6, 3.95):
            P(xm, 0.95, "CA" if xm < 2 else "SC")
        for xm in (0.5, 0.95, 4.6, 5.05):
            P(xm, 0.75, "CO")
        P(2.8, 0.25, "CO")
        for xm, ym in ((0.55, 0.25), (2.7, 0.75), (5.0, 0.25)):
            P(xm, ym, "CH")
        for xm, ym in ((1.2, 0.3), (1.55, 0.45), (1.9, 0.3), (3.3, 0.3), (3.65, 0.45), (4.0, 0.3)):
            P(xm, ym, "AM")
        leyenda = "Módulo B · 5 CO · 3 CH · 6 AM · 1 CA · 1 SC (16 plantas)"
    else:
        for xm in (0.5, 1.9, 3.3, 4.7, 5.1):
            P(xm, 0.85, "CO")
        for xm in (1.2, 2.6, 4.0, 5.1):
            P(xm, 0.4, "CH")
        for xm in (0.4, 0.9, 1.6, 2.2, 3.0, 3.6):
            P(xm, 0.2 if xm < 2 else 0.6, "FR")
        for xm in (4.3, 4.6, 4.45):
            P(xm, 0.2 if xm != 4.45 else 0.45, "AM")
        leyenda = "Módulo A · 5 CO · 4 CH · 6 FR · 3 AM (18 plantas, todo < 0,6 m)"
    g.append(f'<text x="{X0}" y="{Y0 + H * S + 52}" font-size="13" font-weight="600" fill="var(--fg)">{leyenda}</text>')
    g.append(f'<text x="{X0}" y="{Y0 + H * S + 70}" font-size="11" fill="var(--muted)">Escala 1 m = 70 px · faja de 1,20 m · cobertura de chip de 5 cm</text>')
    return f'<svg viewBox="0 0 {X0 * 2 + W * S:.0f} {Y0 + H * S + 90:.0f}" role="img" aria-label="Módulo de plantación {tipo}">' + "".join(g) + "</svg>"


def plano_paisajismo():
    """Planta general del frente con zonas de plantación (reusa la geometría de generar_opciones)."""
    px, YF, SP = G.px, G.YF, G.SP
    alto = YF + 70
    g = [G.defs("p"), f'<rect width="{G.ANCHO_P:.0f}" height="{alto}" fill="var(--surface)"/>']
    g.append(f'<rect x="0" y="{YF + 6}" width="{G.ANCHO_P:.0f}" height="60" fill="#e3d9c2" opacity=".55"/>')
    g.append(f'<text x="{px(36)}" y="{YF + 40}" font-size="12" fill="var(--muted)">banquina: sin plantas (estacionamiento invernal y nieve)</text>')
    # zonas
    def zona(x0, x1, d0, d1, cod, color):
        g.append(f'<rect x="{px(x0):.1f}" y="{YF - d1 * SP:.1f}" width="{(x1 - x0) * SP:.1f}" height="{(d1 - d0) * SP:.1f}" fill="{color}" opacity=".28" stroke="{color}"/>')
        g.append(f'<text x="{(px(x0) + px(x1)) / 2:.1f}" y="{YF - (d0 + d1) / 2 * SP + 4:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="var(--fg)">{cod}</text>')
    for a, b in G.TRAMOS:
        es_a = a < 1 or abs(a - 12.45) < 0.1
        zona(a, b, 0.2, 1.4, "Z2" if es_a else "Z1", "#d7b52a" if es_a else "#5f8a4a")
    zona(24.6, 33.0, 1.6, 2.8, "Z3", "#c0275a")
    zona(4.3, 6.4, 0.2, 2.2, "Z4", "#86b064")
    zona(12.1, 13.0, 1.5, 7.0, "Z4", "#86b064")
    # sendero
    mid = (G.P1 + 0.45 + G.P2) / 2
    g.append(f'<path d="M{px(mid)} {YF - 1.6 * SP} C{px(mid)} {YF - 70} {px(mid + 2)} {YF - 100} {px(mid + 5)} 8" stroke="#b5a585" stroke-width="{1.2 * SP:.0f}" fill="none" opacity=".6"/>')
    g.append(f'<path d="M{px(mid)} {YF - 1.6 * SP} C{px(mid)} {YF - 70} {px(mid + 2)} {YF - 100} {px(mid + 5)} 8" stroke="#86b064" stroke-width="{2.2 * SP:.0f}" fill="none" opacity=".25"/>')
    g.append(f'<text x="{px(mid + 3.2)}" y="{YF - 62}" font-size="11" font-weight="700" fill="var(--fg)">Z5 sendero</text>')
    g.append(simbolo(px(mid + 6.2), 16, "AR"))
    g.append(f'<text x="{px(mid + 7.2)}" y="20" font-size="11" fill="var(--fg)">araucaria (hito)</text>')
    # cerca, mojones, pilares, pircas, tranquera
    for a, b in G.TRAMOS:
        g.append(f'<line x1="{px(a)}" y1="{YF}" x2="{px(b)}" y2="{YF}" stroke="{OP["color_cerca"]}" stroke-width="4"/>')
    for (a, b), s in zip(G.ALAS, (1, -1)):
        y1, y2 = (YF, YF - 1.5 * SP) if s == 1 else (YF - 1.5 * SP, YF)
        g.append(f'<line x1="{px(a)}" y1="{y1}" x2="{px(b)}" y2="{y2}" stroke="#8d877c" stroke-width="9"/>')
    g.append(f'<polygon points="{px(G.ALAS[0][0])},{YF} {px(G.P1)},{YF - 1.5 * SP} {px(G.P2 + 0.45)},{YF - 1.5 * SP} {px(G.ALAS[1][1])},{YF}" fill="url(#lajasp)"/>')
    for n, x in G.MOJONES.items():
        fill = "url(#piedrap)" if n in OP["mojon_piedra"] else G.PIEDRA_PINTADA
        g.append(f'<rect x="{px(x)}" y="{YF + 1}" width="8" height="8" fill="{fill}" stroke="#4a4640"/><text x="{px(x) + 4}" y="{YF + 22}" text-anchor="middle" font-size="9.5" fill="var(--muted)">{n}</text>')
    for x in (G.P1, G.P2):
        g.append(f'<rect x="{px(x)}" y="{YF - 1.5 * SP - 4}" width="8" height="8" fill="url(#piedrap)" stroke="#4a4640"/>')
    g.append(f'<rect x="{px(G.MEDIDORES[0])}" y="{YF - 3}" width="15" height="8" fill="url(#piedrap)" stroke="#4a4640"/>')
    g.append(f'<line x1="{px(G.TRANQUERA[0])}" y1="{YF}" x2="{px(G.TRANQUERA[1])}" y2="{YF}" stroke="#2b2420" stroke-width="4"/>')
    g.append(f'<path d="M{px(9.25)} {YF} C{px(9.25)} {YF - 50} {px(8)} {YF - 90} {px(5)} 8" stroke="#b5a585" stroke-width="50" fill="none" opacity=".4"/>')
    g.append(f'<text x="{px(13.4)}" y="{YF - 95}" font-size="11" fill="var(--fg)">Z7 cerco del camino interno: 6 calafates aislados</text>')
    g.append(f'<text x="{px(40)}" y="{YF - 95}" font-size="11" fill="var(--fg)">Z6 pantalla de la tina: fuera de este plano (foto I06)</text>')
    # triángulos de visibilidad
    g.append(f'<polygon points="{px(6.5)},{YF + 6} {px(0)},{YF + 6} {px(6.5)},{YF + 60}" fill="#a1661b" opacity=".12"/><polygon points="{px(12)},{YF + 6} {px(18)},{YF + 6} {px(12)},{YF + 60}" fill="#a1661b" opacity=".12"/>')
    return f'<svg viewBox="0 0 {G.ANCHO_P:.0f} {alto}" role="img" aria-label="Plano general de paisajismo">' + "".join(g) + "</svg>"


# ======================================================================
# DETALLES CONSTRUCTIVOS (SVG esquemáticos, escala indicada en cada uno)
# ======================================================================
def lamina(titulo, cuerpo, notas, vb="0 0 520 420"):
    w = vb.split()[2]
    h = vb.split()[3]
    ys = int(h) - 18 * len(notas) - 6
    txt = "".join(f'<text x="14" y="{ys + 18 * i}" font-size="12" fill="var(--fg)">{n}</text>' for i, n in enumerate(notas))
    return (f'<figure class="det"><svg viewBox="{vb}" role="img" aria-label="{titulo}"><rect width="{w}" height="{h}" fill="var(--surface)"/>'
            f'<defs><pattern id="pd" width="16" height="11" patternUnits="userSpaceOnUse"><rect width="16" height="11" fill="#8d877c"/><rect x="1" y="1" width="9" height="4.2" rx="1.5" fill="#a59f94"/><rect x="11" y="1" width="4" height="4.2" rx="1.5" fill="#7f796f"/><rect x="1" y="6" width="4.5" height="4.2" rx="1.5" fill="#968f84"/><rect x="6.5" y="6" width="8.5" height="4.2" rx="1.5" fill="#aaa498"/></pattern>'
            f'<pattern id="pr" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#c9bda6"/><circle cx="2" cy="2" r="1" fill="#8f846f"/></pattern></defs>'
            f'{cuerpo}{txt}</svg><figcaption>{titulo}</figcaption></figure>')


def T(x, y, s, size=12, anchor="start", fill="var(--fg)"):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{s}</text>'


def L(x1, y1, x2, y2, c="var(--muted)", w=1, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}/>'


def detalles():
    out = []
    # D1 pilar del portal revestido (escala 1 m = 80 px)
    b = []
    b.append('<rect x="190" y="40" width="72" height="272" fill="#cfcac0" stroke="#4a4640"/>')
    b.append('<rect x="180" y="52" width="10" height="260" fill="url(#pd)"/><rect x="262" y="52" width="10" height="260" fill="url(#pd)"/>')
    b.append('<polygon points="178,52 226,18 274,52" fill="#9a948a" stroke="#4a4640"/>')
    b.append('<rect x="120" y="66" width="215" height="22" rx="11" fill="#8b6240" stroke="#5a3d27"/>')
    b.append(L(210, 66, 210, 110, "#333", 2) + L(242, 66, 242, 110, "#333", 2))
    b.append('<rect x="170" y="312" width="112" height="40" fill="none" stroke="var(--muted)" stroke-dasharray="4 3"/>')
    b.append(L(60, 312, 460, 312, "var(--fg)", 2))
    for y in range(90, 312, 40):
        b.append(L(180, y, 196, y, "#2f6b3a", 2))
    b += [T(350, 30, "remate de mortero en punta, ≥ 45°"), T(350, 74, "viga Ø 25-30 cm en caja; 2 varillas"),
          T(350, 90, "roscadas Ø 16 galv. por apoyo, ≥ 25 cm"), T(350, 150, "núcleo existente 45 × 45 (reparar)"),
          T(350, 190, "piedra bola partida 10-12 cm,"), T(350, 206, "mortero 1:3 con hidrófugo"),
          T(350, 246, "grapas inoxidables cada 40 cm"), T(350, 262, "(en verde), con ancla química"),
          T(350, 340, "fundación: VERIFICAR antes de cargar", 12, "start", "#a3352b"),
          T(130, 160, "60", 12, "end"), T(130, 176, "aprox.", 11, "end", "var(--muted)"), L(176, 168, 136, 168)]
    out.append(lamina("D1 · Pilar del portal revestido en piedra (corte)", "".join(b),
                      ["Medida terminada ≈ 60 × 60 × 340 cm. Mortero con temperatura de más de 5 °C y sin helada en 48 h.",
                       "Juntas rehundidas 1 cm; piedra de una sola cantera para todos los elementos."], "0 0 600 420"))
    # D2 mojón revestido + mojón pintado
    b = []
    for x0, piedra, tit in ((70, True, "vista"), (300, True, "M0 a M8 (los 9)")):
        fill = "url(#pd)" if piedra else "#9a948a"
        b.append(f'<polygon points="{x0},300 {x0},120 {x0 + 50},80 {x0 + 100},120 {x0 + 100},300" fill="{fill}" stroke="#4a4640"/>')
        if piedra:
            b.append(f'<polygon points="{x0 - 4},122 {x0 + 50},78 {x0 + 104},122" fill="#9a948a" stroke="#4a4640"/>')
        b.append(T(x0 + 50, 330, tit, 12, "middle"))
    b.append(L(30, 300, 500, 300, "var(--fg)", 2))
    b += [T(190, 140, "piedra bola partida"), T(190, 156, "10-12 cm, cara redondeada"), T(420, 140, "remate de mortero"), T(420, 156, "en punta, ≥ 45°"),
          L(40, 80, 40, 300), T(36, 194, "1,50", 11, "end")]
    out.append(lamina("D2 · Mojones revestidos en piedra bola (los 9)", "".join(b),
                      ["Núcleo existente reparado; piedra asentada en mortero con grapas inoxidables.",
                       "Medida terminada ≈ 65 × 65 × 150 cm. Muestra de 50 × 50 cm en M3 antes de seguir."], "0 0 520 400"))
    # D3 pilar de medidores
    b = ['<rect x="110" y="80" width="300" height="220" fill="url(#pd)" stroke="#4a4640"/>',
         '<polygon points="104,82 260,40 416,82" fill="#9a948a" stroke="#4a4640"/>']
    for x, y, w, h in ((150, 120, 62, 54), (300, 120, 70, 50), (290, 220, 64, 58)):
        b.append(f'<rect x="{x - 10}" y="{y - 10}" width="{w + 20}" height="{h + 20}" fill="#222"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#e6e8e4" stroke="#777"/>')
    b.append('<rect x="150" y="200" width="120" height="32" fill="#161616" stroke="#c9a96a"/>' + T(210, 220, "TIERRAS MÁGICAS", 9, "middle", "#e2cda0"))
    b.append(L(60, 300, 470, 300, "var(--fg)", 2))
    b += [T(420, 120, "marco perimetral libre"), T(420, 136, "de 5 cm en cada caja"), T(420, 236, "placa de metal negro"), T(420, 252, "40 × 11 cm, anclada al"), T(420, 268, "núcleo, no a la piedra"),
          L(110, 320, 410, 320), T(260, 336, "1,00 + revestimiento", 11, "middle", "var(--muted)")]
    out.append(lamina("D3 · Pilar de medidores revestido (cara exterior; la interior igual)", "".join(b),
                      ["Ninguna caja queda tapada ni con la tapa trabada. Lectura y apertura sin obstáculos.",
                       "Coordinar con la distribuidora el día de trabajo; el dueño indica que no hay objeción."], "0 0 600 400"))
    # D4 pirca seca
    b = ['<rect x="80" y="300" width="360" height="30" fill="url(#pr)" stroke="#8f846f"/>',
         '<polygon points="160,300 205,140 315,140 360,300" fill="url(#pd)" stroke="#4a4640"/>',
         '<rect x="195" y="124" width="130" height="20" rx="4" fill="#9a948a" stroke="#4a4640"/>',
         '<rect x="170" y="225" width="180" height="16" fill="#7f796f" stroke="#4a4640"/>',
         L(60, 300, 470, 300, "var(--fg)", 2)]
    b += [T(340, 116, "piedra de remate (coronamiento)"), T(370, 236, "piedra de llave atravesada"), T(370, 252, "cada 1 m"),
          T(380, 290, "base de ripio compactado 15 cm"), L(150, 140, 150, 300), T(144, 224, "0,60", 11, "end"),
          L(160, 345, 360, 345), T(260, 360, "0,45 base", 11, "middle", "var(--muted)"), T(260, 110, "0,35", 11, "middle", "var(--muted)")]
    out.append(lamina("D4 · Pirca de piedra seca en las alas del atrio (corte)", "".join(b),
                      ["Largo de cada ala ≈ 2,5 m (2 m sobre la línea de cerca y 1,50 m de retiro).",
                       "Sin mortero: piedra trabada a mano, caras planas hacia afuera, inclinación leve hacia adentro."], "0 0 560 440"))
    # D5 cerca
    b = [L(20, 300, 540, 300, "var(--fg)", 2)]
    for x in (40, 270, 500):
        b.append(f'<polygon points="{x},380 {x},110 {x + 10},96 {x + 20},110 {x + 20},380" fill="#9a5a36"/>')
    for y in (128, 186, 244):
        b.append(f'<rect x="30" y="{y}" width="500" height="14" fill="#9a5a36" opacity=".85"/>')
    b.append('<rect x="34" y="300" width="32" height="80" fill="none" stroke="var(--muted)" stroke-dasharray="4 3"/>')
    b += [T(70, 90, "poste 5\"×5\" × 1,85 m, punta de diamante"), T(300, 172, "travesaño 2\"×5\" × 5,49 m (18'), en caja", 11), T(300, 230, "tarugo Ø 16 o tirafondo galvanizado", 11),
          T(300, 326, "empotramiento 0,70 m, base impregnada", 11),
          T(300, 342, "apisonada con ripio en capas de 15 cm", 11), T(300, 358, "(o dado de hormigón pobre)", 11),
          L(560, 300, 560, 98), T(564, 200, "1,15", 11), T(564, 141, "0,95", 10), T(564, 199, "0,65", 10), T(564, 257, "0,35", 10)]
    out.append(lamina("D5 · Cerca de postes escuadrados, tramo tipo de 6 m (vista)", "".join(b),
                      ["3 postes por tramo: 2 junto a los mojones (a 2-3 cm, sin perforarlos) y 1 central, ≈ 2,7 m.",
                       "Madera: ciprés, eucalipto colorado o pino CCA. Impregnante natural medio con filtro UV, 3 manos."], "0 0 600 440"))
    # D6 viga + cartel
    b = ['<rect x="30" y="150" width="40" height="230" fill="url(#pd)"/><rect x="470" y="150" width="40" height="230" fill="url(#pd)"/>',
         '<rect x="10" y="120" width="520" height="30" rx="15" fill="#8b6240" stroke="#5a3d27"/>',
         '<polygon points="70,150 100,150 70,180" fill="#111"/><polygon points="470,150 440,150 470,180" fill="#111"/>',
         L(200, 150, 200, 200, "#222", 2), L(340, 150, 340, 200, "#222", 2),
         '<polygon points="166,200 270,188 374,200" fill="#2a2420"/>',
         '<rect x="170" y="200" width="200" height="50" rx="3" fill="#4a3324"/>',
         T(270, 225, "TIERRAS MÁGICAS", 15, "middle", "#e2cda0"), T(270, 242, "CABAÑAS DE MONTAÑA · VILLA PEHUENIA MOQUEHUE", 7, "middle", "#d2be96"),
         L(200, 250, 160, 300, "#666", 1, "3 3"), L(340, 250, 380, 300, "#666", 1, "3 3")]
    b += [T(14, 112, "rollizo Ø 25-30 × 6,00 m, descortezado, impregnado; vuelo 0,65 m por lado"),
          T(104, 172, "ménsula 1/4\" negra", 11), T(378, 184, "botaguas negro", 11),
          T(150, 320, "riendas de cable de acero a los pilares (anti golpeteo con viento)"),
          T(150, 290, "tabla 2,0 × 0,5 m, 2\" de espesor"), T(150, 340, "cadenas o planchuelas galvanizadas; altura libre ≥ 2,10 m")]
    out.append(lamina("D6 · Viga nueva, ménsulas y tabla tallada (vista desde la ruta)", "".join(b),
                      ["Cara interior de la tabla: «BUEN VIAJE · Gracias por elegir Tierras Mágicas».",
                       "Sección de la viga, anclajes y riendas: VERIFICAR por arquitecto o ingeniero (viento y nieve)."], "0 0 560 440"))
    # D7 portón peatonal
    b = ['<rect x="20" y="70" width="30" height="270" fill="url(#pd)"/><rect x="510" y="70" width="30" height="270" fill="url(#pd)"/>']
    for x0 in (55, 283):
        b.append(f'<rect x="{x0}" y="130" width="222" height="190" fill="#1c1c1c"/>')
        for x in range(x0 + 8, x0 + 214, 14):
            b.append(f'<rect x="{x}" y="138" width="10" height="174" fill="#7a5235"/>')
    b.append(L(20, 330, 540, 330, "var(--fg)", 2))
    b += [T(60, 120, "bastidor tubo 60 × 40 × 2 mm, galvanizado + esmalte negro mate"),
          T(60, 360, "2 hojas de ≈ 1,88 × 1,40 m · tablas 1\"×4\" verticales con 1 cm de luz, tono natural medio"),
          T(60, 378, "3 bisagras por hoja con anclaje químico al núcleo del pilar · pasador al piso · cerrojo · tope central"),
          T(60, 396, "5 cm libres sobre el piso del atrio (no apoya en hielo)")]
    out.append(lamina("D7 · Portón peatonal nuevo (vista)", "".join(b), [], "0 0 560 410"))
    # D8 atrio y sendero
    b = ['<rect x="30" y="200" width="250" height="14" fill="#a8a296" stroke="#4a4640"/>',
         '<rect x="30" y="214" width="250" height="14" fill="#e3d6b0"/>', '<rect x="30" y="228" width="250" height="34" fill="url(#pr)"/>',
         '<rect x="320" y="206" width="200" height="22" fill="url(#pr)"/>', '<rect x="320" y="228" width="200" height="34" fill="#c8b48a" opacity=".5"/>',
         '<circle cx="316" cy="206" r="10" fill="#8b6240"/><circle cx="524" cy="206" r="10" fill="#8b6240"/>']
    b += [T(30, 180, "ATRIO (≈ 10 m²)", 13), T(30, 300, "lajas de piedra local 3-5 cm", 12), T(30, 316, "cama de arena 5 cm", 12),
          T(30, 332, "ripio compactado 10 cm", 12), T(30, 348, "pendiente 2 % hacia los canteros", 12),
          T(320, 180, "SENDERO 1,2 m × ≈ 30 m", 13), T(320, 300, "ripio fino 5-10 cm compactado", 12),
          T(320, 316, "geotextil sobre suelo despejado", 12), T(320, 332, "borde de rollizo Ø 10 en ambos lados", 12),
          T(320, 348, "escalones de durmiente si la pendiente > 10 %", 12), T(320, 364, "balizas solares cada ≈ 4 m", 12)]
    out.append(lamina("D8 · Atrio de lajas y sendero peatonal (cortes)", "".join(b), [], "0 0 560 390"))
    # D9 luminaria solar
    b = ['<rect x="40" y="200" width="480" height="26" rx="13" fill="#8b6240" stroke="#5a3d27"/>',
         '<polygon points="200,200 240,130 290,148 250,200" fill="#26364a" stroke="#111"/>',
         L(245, 200, 245, 226, "#333", 2), '<rect x="300" y="226" width="20" height="12" fill="#222"/>',
         '<polygon points="310,238 270,320 350,320" fill="#f2c46b" opacity=".35"/>',
         '<rect x="250" y="320" width="120" height="30" fill="#4a3324"/>']
    b += [T(300, 128, "panel solar sobre la viga, cara a la ruta"), T(300, 144, "(noroeste), inclinado 55-60° para que"), T(300, 160, "resbale la nieve; sin sombra de pinos"),
          T(330, 236, "proyector 2700-3000 K, IP65, 200-300 lm"), T(380, 336, "tabla iluminada desde arriba"),
          T(40, 270, "batería con carga a baja temperatura"), T(40, 286, "(no cargar LiFePO4 común bajo 0 °C)"), T(40, 302, "autonomía ≥ 3 noches · encendido"), T(40, 318, "crepuscular · 30 % después de 00:30")]
    out.append(lamina("D9 · Iluminación solar del cartel (esquema)", "".join(b),
                      ["Mismo criterio en pilares (luz hacia abajo), pircas (luz baja), placa de M1 y balizas del sendero.",
                       "Plan B: si en el primer invierno no alcanza, solo el cartel pasa a 12 V desde el tablero, con electricista."], "0 0 560 410"))
    return "".join(out)


# ======================================================================
# CÓMPUTO
# ======================================================================
def computo():
    tot = totales_especies()
    piedra_pil = 2 * 4 * 0.45 * 3.4
    piedra_moj = 9 * 4 * 0.45 * 1.5
    piedra_med = 2 * (1.0 + 0.45) * 1.5 - 0.4
    piedra = round((piedra_pil + piedra_moj + piedra_med) * 1.10, 1)
    postes_frente, postes_int = 21, 20
    mad_m2 = (postes_frente + postes_int) * 4 * 0.127 * 1.85 + (21 * 3 + 20 * 2) / 3 * 5.49 * 2 * (0.127 + 0.05) + 2 * (5.5 * 1.4) * 2
    rows = [
        # rubro, item, unidad, cantidad, origen, proveedor
        ("Trabajos previos", "Retiro de la viga podrida, ladrillos, alambrado y cerco de soga; limpieza", "gl", 1, "Mano de obra propia", "—"),
        ("Trabajos previos", "Replanteo de la línea de cerca, mojones, portal, atrio y sendero", "gl", 1, "Propio + estacas e hilo", "—"),
        ("Piedra", "Piedra bola partida 10-12 cm para revestimiento (pilares, 9 mojones, medidores) + 10 %", "m²", piedra, "Nuevo", "Cantera / corralón"),
        ("Piedra", "Piedra para pircas secas (2 alas de 2,5 × 0,60 × 0,40 m), incluye remate", "m³", 1.3, "Nuevo o del predio", "Cantera"),
        ("Piedra", "Lajas para atrio 3-5 cm + 10 %", "m²", 11, "Nuevo", "Cantera"),
        ("Piedra", "Mano de obra de pircador: revestimientos, pircas, atrio", "jornal", 24, "Contratada", "Pircador"),
        ("Albañilería", "Cemento, arena, hidrófugo para asiento de piedra y remates", "gl", 1, "Nuevo", "Corralón"),
        ("Albañilería", "Grapas de acero inoxidable + ancla química", "u", 160, "Nuevo", "Ferretería"),
        ("Portal", "Rollizo Ø 25-30 cm × 6,00 m, seco, descortezado e impregnado", "u", 1, "Nuevo", "Aserradero"),
        ("Portal", "Varilla roscada Ø 16 galvanizada + tuercas + resina química (2 apoyos)", "jgo", 1, "Nuevo", "Ferretería"),
        ("Portal", "Ménsulas de planchuela negra", "u", 2, "Nuevo", "Herrero"),
        ("Portal", "Portón peatonal nuevo de 2 hojas (bastidor metálico + tablas), con herrajes", "u", 1, "Nuevo", "Herrero + carpintero"),
        ("Señalética", "Tabla tallada 2,0 × 0,5 m, dos caras, con botaguas, cadenas y riendas", "u", 1, "Nuevo", "Carpintería / tallador"),
        ("Señalética", "Placa de metal negro «Tierras Mágicas · Ingreso · Recepción» para el pilar de medidores", "u", 1, "Nuevo", "Cartelería"),
        ("Cerca", "Postes escuadrados 5\"×5\" × 1,85 m con punta de diamante y 3 cajas (frente)", "u", postes_frente, "Nuevo", "Aserradero"),
        ("Cerca", "Travesaños 2\"×5\" × 5,49 m (18') (frente)", "u", 21, "Nuevo", "Aserradero"),
        ("Cerca", "Postes 5\"×5\" × 1,85 m con 2 cajas (cerco interno ≈ 50 m)", "u", postes_int, "Nuevo", "Aserradero"),
        ("Cerca", "Travesaños 2\"×5\" × 5,49 m (cerco interno, 2 líneas)", "u", 20, "Nuevo", "Aserradero"),
        ("Cerca", "Tarugos de madera dura Ø 16 o tirafondos galvanizados", "u", 3 * postes_frente + 2 * postes_int, "Nuevo", "Ferretería"),
        ("Cerca", "Ripio para apisonar postes", "m³", 2, "Nuevo", "Corralón"),
        ("Madera", "Impregnante natural medio con filtro UV, 3 manos (cerca y cerco interno; la tranquera sigue oscura)", "L", round(mad_m2 * 3 / 10), "Nuevo", "Pinturería"),
        ("Tranquera", "Restauración de la tranquera: lijado, herrajes negros, impregnante", "gl", 1, "Reutilizado", "Propio"),
        ("Sendero", "Ripio fino para sendero (36 m² × 10 cm)", "m³", 3.6, "Nuevo", "Corralón"),
        ("Sendero", "Geotextil", "m²", 40, "Nuevo", "Corralón"),
        ("Sendero", "Rollizo Ø 10 para borde (ambos lados)", "m", 60, "Nuevo o rollizos del predio", "Aserradero"),
        ("Sendero", "Ripio y arena para base del atrio (10 m² × 15 cm)", "m³", 1.5, "Nuevo", "Corralón"),
        ("Iluminación", "Proyector solar con panel separado (cartel)", "u", 2, "Nuevo", "Iluminación"),
        ("Iluminación", "Aplique solar hacia abajo, panel separado (pilares)", "u", 2, "Nuevo", "Iluminación"),
        ("Iluminación", "Luz solar baja (pircas y placa de medidores)", "u", 3, "Nuevo", "Iluminación"),
        ("Iluminación", "Balizas solares para sendero", "u", 8, "Nuevo", "Iluminación"),
        ("Paisajismo", "Chip de corteza o grava local, cobertura de 5 cm", "m³", 5, "Nuevo o del predio", "Vivero / corralón"),
        ("Paisajismo", "Ampliación de riego por goteo: manguera 16 mm con goteros autocompensados", "m", 150, "Nuevo", "Riego"),
        ("Paisajismo", "Tierra fértil para hoyos de plantación", "m³", 2, "Nuevo", "Vivero"),
    ]
    for k, v in tot.items():
        e = ESPECIES[k]
        rows.append(("Plantas", f'{e["nombre"]} ({e["cientifico"]}), {e["env"]}', "u", v, "Nuevo", "Vivero de nativas"))
    return rows


def fmt(v):
    if isinstance(v, float):
        return f"{v:.1f}".replace(".", ",")
    return str(v)


def xlsx(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Lista de compras"
    ws["A1"] = "Tierras Mágicas · Acceso · Proyecto ejecutivo (opción 3 con tabla tallada). Cargar precios de cotización en la columna amarilla."
    ws["A1"].font = Font(bold=True)
    cab = ["Rubro", "Ítem", "Unidad", "Cantidad", "Origen", "Proveedor tipo", "Precio unitario", "Proveedor / fecha", "Subtotal"]
    for i, c in enumerate(cab, 1):
        cell = ws.cell(3, i, c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F3326")
        cell.alignment = Alignment(wrap_text=True)
    amar = PatternFill("solid", fgColor="FFF2CC")
    for r, row in enumerate(rows, 4):
        for j, v in enumerate(row, 1):
            ws.cell(r, j, v)
        ws.cell(r, 7).fill = amar
        ws.cell(r, 8).fill = amar
        ws.cell(r, 9, f'=IF(G{r}="","",D{r}*G{r})')
    fin = 3 + len(rows)
    ws.cell(fin + 2, 2, "TOTAL MATERIALES Y OFICIOS COTIZADOS").font = Font(bold=True)
    ws.cell(fin + 2, 9, f"=SUM(I4:I{fin})").font = Font(bold=True)
    ws.cell(fin + 3, 2, "Imprevistos 10 %")
    ws.cell(fin + 3, 9, f"=0.1*I{fin + 2}")
    ws.cell(fin + 4, 2, "TOTAL ESTIMADO").font = Font(bold=True)
    ws.cell(fin + 4, 9, f"=I{fin + 2}+I{fin + 3}").font = Font(bold=True)
    for col, w in zip("ABCDEFGHI", (16, 70, 8, 10, 22, 22, 16, 24, 16)):
        ws.column_dimensions[col].width = w
    wb.save(BASE / "lista_compras_proyecto_ejecutivo.xlsx")


# ======================================================================
# PLAN DE OBRA
# ======================================================================
SEMANAS = ["1-7 dic", "8-14 dic", "15-21 dic", "22-31 dic", "ene 1-2", "ene 3-4", "feb 1-2", "feb 3-4", "mar 1-2", "mar 3-4", "abr 1-2", "abr 3-4"]
TAREAS = [
    ("E0", "Replanteo, verificación estructural de viga y anclajes, cotizaciones y compras", 0, 2, "Dueño + profesional"),
    ("E0", "Acordar con la constructora vial cuneta, alcantarilla, banquina y paso frente al portal", 0, 2, "Dueño"),
    ("E1", "Retiro de la viga podrida; viga nueva, ménsulas y tabla tallada", 1, 3, "Propio + carpintero"),
    ("E1", "Reparación del núcleo de los 9 mojones; restauración de la tranquera; limpieza", 1, 3, "Propio"),
    ("E2", "Revestimiento de piedra bola: pilares del portal, 9 mojones y pilar de medidores", 4, 7, "Pircador"),
    ("E2", "Pircas de las alas y atrio de lajas", 6, 8, "Pircador"),
    ("E3", "Cerca de postes escuadrados del frente y retiro del alambrado", 5, 8, "Propio + ayudante"),
    ("E3", "Cerco del camino interno (≈ 50 m)", 7, 9, "Propio"),
    ("E3", "Portón peatonal nuevo (fabricación y colocación)", 5, 8, "Herrero"),
    ("E3", "Sendero, balizas y luces solares", 8, 9, "Propio"),
    ("E4", "Paisajismo: preparación de suelo, riego, plantación de otoño y cobertura", 8, 11, "Propio + vivero"),
    ("E5", "Ajustes después del primer invierno (luces, replantes, impregnante)", 11, 11, "Propio"),
]


def gantt():
    cw, x0, rh = 46, 330, 26
    w = x0 + cw * len(SEMANAS) + 10
    h = 30 + rh * len(TAREAS) + 10
    colores = {"E0": "#8d877c", "E1": "#a8622a", "E2": "#6f6a60", "E3": "#3e3029", "E4": "#5f8a4a", "E5": "#9cc5a6"}
    g = [f'<rect width="{w}" height="{h}" fill="var(--surface)"/>']
    for i, s in enumerate(SEMANAS):
        g.append(f'<text x="{x0 + cw * i + cw / 2}" y="18" text-anchor="middle" font-size="10" fill="var(--muted)">{s}</text>')
        g.append(L(x0 + cw * i, 24, x0 + cw * i, h - 6, "var(--line)"))
    g.append(f'<rect x="{x0 + cw * 3.5}" y="24" width="{cw * 2}" height="{h - 30}" fill="#a1661b" opacity=".08"/>')
    for r, (et, txt, a, b, quien) in enumerate(TAREAS):
        y = 30 + rh * r
        g.append(f'<text x="6" y="{y + 16}" font-size="11" fill="var(--fg)"><tspan font-weight="700">{et}</tspan> {txt[:52]}{"…" if len(txt) > 52 else ""}</text>')
        g.append(f'<rect x="{x0 + cw * a + 2}" y="{y + 5}" width="{cw * (b - a + 1) - 4}" height="{rh - 10}" rx="3" fill="{colores[et]}"/>')
    g.append(f'<text x="{x0 + cw * 4.5}" y="{h - 10}" text-anchor="middle" font-size="10" fill="#a1661b">temporada alta: obra solo en días de semana</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Plan de obra semanal">' + "".join(g) + "</svg>"


# ======================================================================
# PÁGINA
# ======================================================================
CSS = """
/* Layout: memoria técnica de una columna; planos en contenedores con scroll; láminas de detalle en grilla */
:root{--bg:#f3f4f1;--surface:#ffffff;--fg:#1d2420;--muted:#5b655e;--line:#d5dad3;--chip:#e6eae3;--bosque:#1f3326;--lenga:#a8622a;--ok:#2f6b3a;--warn:#a1661b;--bad:#a3352b;
--f-display:"Archivo",system-ui,sans-serif;--f-body:"Source Sans 3",system-ui,sans-serif;--f-mono:"JetBrains Mono",ui-monospace,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141a16;--surface:#1c241f;--fg:#e7ebe5;--muted:#a3ada5;--line:#334038;--chip:#26312a;--bosque:#9cc5a6;--lenga:#e0995a;--ok:#7cc48a;--warn:#e3a957;--bad:#ec8a7f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141a16;--surface:#1c241f;--fg:#e7ebe5;--muted:#a3ada5;--line:#334038;--chip:#26312a;--bosque:#9cc5a6;--lenga:#e0995a;--ok:#7cc48a;--warn:#e3a957;--bad:#ec8a7f;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:17px/1.55 var(--f-body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 64px}
.wrap{max-width:1100px;margin:0 auto}
header.portada{padding-block:36px 20px;border-bottom:3px solid var(--bosque);display:grid;gap:10px}
.eyebrow{font:500 12px var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--lenga)}
h1{font:800 clamp(28px,5vw,46px)/1.05 var(--f-display);margin:0;color:var(--bosque);text-wrap:balance}
h2{font:800 26px/1.2 var(--f-display);margin:52px 0 12px;color:var(--bosque);display:flex;gap:12px;align-items:baseline;text-wrap:balance}
h2 .n{font:500 14px var(--f-mono);color:var(--lenga)}
h3{font:600 18px/1.3 var(--f-display);margin:26px 0 8px}
p,li{max-width:74ch}
.lead{font-size:19px;color:var(--muted);margin:0}
.ficha{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
.ficha div{background:var(--surface);padding:12px 14px;min-width:0}
.ficha b{display:block;font:500 11px var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
nav.indice{display:flex;flex-wrap:wrap;gap:6px}
nav.indice a{font-weight:600;font-size:14px;color:var(--fg);background:var(--chip);padding:5px 10px;border-radius:4px;text-decoration:none}
nav.indice a:hover,nav.indice a:focus-visible{background:var(--bosque);color:var(--bg);outline:none}
figure{margin:0} figure img{display:block;width:100%;height:auto;border:1px solid var(--line)}
figcaption{font-size:14px;color:var(--muted);padding:6px 2px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.diag{overflow-x:auto;border:1px solid var(--line);background:var(--surface)}
.diag svg{display:block;width:100%;min-width:760px;height:auto}
.diag svg+svg{border-top:1px dashed var(--line)}
svg text{font-family:var(--f-body)}
.dets{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:14px}
.det{border:1px solid var(--line);background:var(--surface);overflow-x:auto}
.det svg{display:block;width:100%;min-width:440px;height:auto}
.det figcaption{padding:8px 12px;font-weight:600;color:var(--fg)}
.mods{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:14px}
.mods .diag svg{min-width:420px}
.tabla{overflow-x:auto;border:1px solid var(--line);background:var(--surface);margin:10px 0}
table{border-collapse:collapse;width:100%;min-width:680px;font-size:15px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font:500 12px var(--f-mono);letter-spacing:.05em;text-transform:uppercase;color:var(--muted);background:var(--chip)}
td.num{font-family:var(--f-mono);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
.sw{display:inline-block;width:12px;height:12px;border-radius:50%;vertical-align:-1px;margin-right:6px;border:1px solid rgba(0,0,0,.3)}
.aviso{border-left:4px solid var(--warn);background:var(--surface);padding:12px 16px;margin:14px 0}
.aviso.bad{border-color:var(--bad)} .aviso.ok{border-color:var(--ok)}
.estaciones{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.estaciones div{background:var(--surface);border:1px solid var(--line);padding:12px 14px;min-width:0}
.estaciones b{font-family:var(--f-display)}
footer{margin-top:52px;padding-top:14px;border-top:1px solid var(--line);font-size:14px;color:var(--muted)}
@media print{body{font-size:12.5px} .wrap{max-width:none} nav.indice{display:none} h2{break-before:page;margin-top:0} .det,.diag,figure,.tabla tr{break-inside:avoid} .diag svg,.det svg{min-width:0} .dets{grid-template-columns:1fr 1fr}}
"""


def pagina():
    rows = computo()
    xlsx(rows)
    tot = totales_especies()
    filas_esp = "".join(
        f'<tr><td><span class="sw" style="background:{e["color"]}"></span><b>{k}</b></td><td>{e["nombre"]}<br><i>{e["cientifico"]}</i></td>'
        f'<td>{e["tipo"]}</td><td>{e["alto"]}</td><td>{e["flor"]}</td><td>{e["env"]}</td><td>{e["dist"]}</td><td class="num">{tot[k]}</td><td>{e["nota"]}</td></tr>'
        for k, e in ESPECIES.items())
    filas_z = "".join(
        f'<tr><td><b>{z}</b></td><td>{d}</td><td>{sup}</td><td>{" · ".join(f"{c} {n}" for c, n in esp.items())}</td><td class="num">{sum(esp.values())}</td></tr>'
        for z, d, sup, esp in ZONAS)
    total_plantas = sum(tot.values())
    filas_c = "".join(f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td class="num">{fmt(r[3])}</td><td>{r[4]}</td><td>{r[5]}</td></tr>' for r in rows)
    quien = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in [
        ("Limpieza, retiros, replanteo", "Propio", "—"),
        ("Pintura de mojones, restauración de tranquera, impregnante", "Propio", "—"),
        ("Cerca y cerco interno", "Propio con ayudante", "Carpintero solo si las cajas no vienen hechas del aserradero"),
        ("Sendero, balizas, luces solares", "Propio", "—"),
        ("Plantación y riego", "Propio", "Vivero de nativas: elección final y estado de las plantas"),
        ("Revestimientos de piedra, pircas, atrio", "No", "Pircador o albañil con experiencia en piedra"),
        ("Portón peatonal nuevo, ménsulas", "No", "Herrero (y carpintero para las tablas)"),
        ("Viga nueva y cartel", "Montaje con ayuda (≈ 200-300 kg)", "Verificación de arquitecto o ingeniero"),
        ("Electricidad (solo plan B a 12 V)", "No", "Electricista matriculado"),
    ])
    proveedores = {}
    for r in rows:
        proveedores.setdefault(r[5], []).append(f"{r[1]}: {fmt(r[3])} {r[2]}")
    cotiz = "".join(f"<li><b>{p}</b><ul>{''.join(f'<li>{i}</li>' for i in its)}</ul></li>" for p, its in proveedores.items() if p not in ("—", "Propio"))

    return f"""<title>Proyecto ejecutivo del acceso</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;800&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@500&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="portada">
  <span class="eyebrow">PLC-07 · Proyecto ejecutivo · 28/11/2026 · Tierras Mágicas, RP 11 Km 8,2, Villa Pehuenia Moquehue</span>
  <h1>Acceso Tierras Mágicas: refugio de piedra</h1>
  <p class="lead">Proyecto ejecutivo de la opción 3 elegida por el dueño, con la tabla tallada colgante de las opciones 1 y 2 en lugar del panel del logo. Cubre todo el frente de punta a punta: cerca, portal peatonal, acceso vehicular y paisajismo.</p>
  <div class="ficha">
    <div><b>Decisión</b>Opción 3 «Refugio de piedra» con la tabla tallada, los 9 mojones en piedra bola y la cerca en madera natural media</div>
    <div><b>Frente</b>59,54 m · 9 mojones cada 6 m · portal de 3,80 m · tranquera de 5,50 m</div>
    <div><b>Plantas</b>{total_plantas} nativas de 12 especies, en 7 zonas</div>
    <div><b>Obra</b>Diciembre a abril, en 6 etapas (E0 a E5)</div>
  </div>
  <nav class="indice" aria-label="Secciones"><a href="#memoria">Memoria</a><a href="#imagen">Imagen final</a><a href="#planos">Planos</a><a href="#paisajismo">Paisajismo</a><a href="#detalles">Detalles</a><a href="#especificaciones">Especificaciones</a><a href="#computo">Cómputo</a><a href="#obra">Plan de obra</a><a href="#verificar">Verificaciones</a><a href="#cotizar">Pedido de cotización</a></nav>
</header>

<h2 id="memoria"><span class="n">01</span>Memoria descriptiva</h2>
<p>El frente se ordena con tres materiales: <b>piedra bola</b> en los pilares del portal, en los 9 mojones y en el pilar de medidores, <b>madera natural de tono medio</b> en la cerca y en las tablas del portón, y <b>metal negro</b> en herrajes y ménsulas. La tranquera existente se mantiene oscura. Desde la ruta, el frente se lee como un conjunto continuo: los 9 mojones de piedra marcan el ritmo cada 6 m y el portal concentra la imagen.</p>
<ul>
  <li><b>Cerca:</b> 7 tramos de 6 m entre mojones, con postes escuadrados de 5"×5" con punta de diamante, que repiten la forma de los mojones, y 3 travesaños pasantes de 18', en madera natural de tono medio. Mide 1,15 m de alto libre. Se retira el alambrado.</li>
  <li><b>Portal peatonal:</b> retirado 1,50 m, con un atrio de lajas entre dos pircas bajas de piedra seca. Pilares revestidos de 3,40 m, viga nueva de rollizo con ménsulas negras y la tabla tallada «Tierras Mágicas · Cabañas de montaña · Villa Pehuenia Moquehue» colgada. Del lado de adentro dice «Buen viaje». El portón es nuevo, metálico con tablas verticales.</li>
  <li><b>Acceso vehicular:</b> pilar de medidores revestido en piedra, con las cajas libres y enmarcadas, y la placa «Ingreso · Recepción». La tranquera se restaura con herrajes negros. El cerco del camino interno (≈ 50 m) pasa a tener postes de 5"×5" y 2 travesaños.</li>
  <li><b>Paisajismo:</b> solo especies nativas de la cordillera, en franjas bajas del lado de adentro de la cerca. Las flores se concentran en el portal y el sendero, la pantalla vegetal va frente a la tina y una araucaria marca el final del sendero. La banquina queda libre.</li>
  <li><b>Luz:</b> solar, cálida y dirigida hacia abajo, en el cartel, los pilares, las pircas, la placa y el sendero.</li>
</ul>
<div class="aviso">La constructora vial hace la cuneta, la alcantarilla y el relleno de la banquina. Si la cuneta impide el paso frente al portal, el portal queda cerrado como portada y se entra a pie por la tranquera. En ese caso se descuentan el sendero, las balizas y el atrio, y el resto del proyecto no cambia.</div>

<h2 id="imagen"><span class="n">02</span>Imagen final</h2>
<div class="grid2">
  <figure><img src="montajes/OP3_refugio_piedra_F07.jpg" alt="Portal peatonal con pilares de piedra, viga con ménsulas, tabla tallada y portón nuevo"><figcaption>Portal peatonal desde la ruta (fotomontaje ilustrativo sobre F07).</figcaption></figure>
  <figure><img src="montajes/EJ_acceso_vehicular_I02.jpg" alt="Pilar de medidores revestido en piedra con las cajas libres, placa y tranquera restaurada"><figcaption>Acceso vehicular visto desde adentro: pilar de medidores revestido, cajas enmarcadas y placa (fotomontaje sobre I02).</figcaption></figure>
</div>

<h2 id="planos"><span class="n">03</span>Planos generales</h2>
<h3>Elevación completa desde la ruta, de M0 a M8</h3>
<div class="diag">{G.elevacion_completa(3, OP)}</div>
<h3>Planta completa del frente</h3>
<div class="diag">{G.planta_completa(3, OP)}</div>

<h2 id="paisajismo"><span class="n">04</span>Paisajismo</h2>
<p><b>Criterio:</b> plantas nativas de la cordillera, de bajo mantenimiento, en grupos irregulares y nunca en fila. Lo alto va contra la cerca y lo bajo hacia el interior. Nada tapa los mojones, los pilares ni la vista desde la ruta. En los triángulos de visibilidad de la tranquera nada supera los 0,6 m. La banquina queda sin plantas. Las flores se concentran donde se camina (portal y sendero), y el coirón y la chaura sostienen la imagen en invierno.</p>
<h3>Plano general de zonas</h3>
<div class="diag">{plano_paisajismo()}</div>
<h3>Módulos de plantación tipo (por tramo de 6 m)</h3>
<div class="mods"><div class="diag">{modulo("B")}</div><div class="diag">{modulo("A")}</div></div>
<h3>Zonas y cantidades</h3>
<div class="tabla"><table><thead><tr><th>Zona</th><th>Ubicación</th><th>Superficie</th><th>Plantas</th><th>Total</th></tr></thead><tbody>{filas_z}</tbody>
<tfoot><tr><td colspan="4"><b>Total de plantas</b></td><td class="num"><b>{total_plantas}</b></td></tr></tfoot></table></div>
<h3>Especies</h3>
<div class="tabla"><table><thead><tr><th>Código</th><th>Especie</th><th>Tipo</th><th>Altura</th><th>Flor</th><th>Envase</th><th>Distancia</th><th>Cant.</th><th>Uso y notas</th></tr></thead><tbody>{filas_esp}</tbody></table></div>
<div class="aviso">Todas son nativas de los bosques andino-patagónicos. Antes de comprar, el vivero de nativas de la zona (Villa Pehuenia, Aluminé, Junín de los Andes o San Martín de los Andes) tiene que confirmar la especie, la procedencia andina y que se adapten a la altura de Moquehue. Esto vale sobre todo para la frutilla silvestre y la mutisia. Nunca hay que extraer plantas del bosque: la araucaria, en particular, solo se compra en un vivero autorizado.</div>
<h3>Cómo se ve en cada estación</h3>
<div class="estaciones">
  <div><b>Primavera (sep-nov)</b><br>Calafate en amarillo y michay en naranja; notro en rojo intenso en la pantalla de la tina; frutilla silvestre en flor blanca; rebrotan amancay y chilco.</div>
  <div><b>Verano (dic-feb)</b><br>El amancay naranja es la estrella del frente; chilco en rojo y violeta junto al portal; mutisia sobre las pircas; siete camisas y palo piche en blanco.</div>
  <div><b>Otoño (mar-may)</b><br>Ñires en rojo de fondo; siete camisas con hoja rojiza; coirón dorado; bayas rosadas y blancas de la chaura.</div>
  <div><b>Invierno (jun-ago)</b><br>La piedra bola y la madera natural sostienen la identidad; quedan verdes la chaura, el calafate y el michay; el coirón asoma sobre la nieve. Las flores descansan.</div>
</div>
<h3>Plantación, riego y mantenimiento</h3>
<ul>
  <li><b>Época:</b> plantación principal en otoño (marzo-abril), antes de las heladas fuertes. La araucaria, el notro y el chilco, en otoño o a fines de septiembre.</li>
  <li><b>Preparación:</b> descompactar 30 cm. Hoyos del doble del envase, con tierra fértil mezclada 1:1 con la del lugar. Piedras del predio semienterradas entre los grupos.</li>
  <li><b>Cobertura:</b> 5 cm de chip de corteza o de grava del lugar en todos los canteros, para frenar malezas y erosión y proteger del frío.</li>
  <li><b>Riego:</b> se amplía el goteo existente (≈ 150 m de manguera con goteros autocompensados). Los 2 primeros veranos, 2 o 3 riegos por semana. Desde el tercer año, solo el chilco y la pantalla de la tina. Vaciar la red antes del invierno.</li>
  <li><b>Mantenimiento anual:</b> en primavera, desmalezar y reponer la cobertura. En otoño, cortar las varas secas del amancay y peinar el coirón. No hace falta podar, salvo para despejar mojones, pilares y la tranquera.</li>
  <li><b>Exóticas (a decidir por el dueño):</b> retirar los pinos jóvenes que estén a menos de 3 m de la cerca o que vayan a tapar la vista. No ampliar los lupinos y reemplazarlos de a poco por amancay, porque ambas exóticas se consideran invasoras en la zona. El romero existente se mantiene. No sumar enebros ni coníferas junto al portal ni junto a los tanques de gas.</li>
</ul>

<h2 id="detalles"><span class="n">05</span>Detalles constructivos</h2>
<div class="aviso bad"><b>Antes de construir, un profesional tiene que verificar:</b> la sección y el anclaje de la viga con el cartel (viento y nieve), el estado del núcleo y la fundación de los pilares del portal antes de sumarles el peso de la piedra, y el anclaje de las bisagras del portón nuevo. Los detalles fijan el criterio y las medidas de proyecto, no reemplazan ese cálculo.</div>
<div class="dets">{detalles()}</div>

<h2 id="especificaciones"><span class="n">06</span>Especificaciones técnicas</h2>
<h3>Piedra</h3>
<ul><li>Piedra local de una sola cantera para revestimientos, pircas y lajas, de color gris cálido sin vetas blancas fuertes. Antes de comprar el total, armar una muestra de 50 × 50 cm sobre M3.</li>
<li>Revestimiento en piedra bola partida de 10 a 12 cm, con la cara redondeada hacia afuera, asentadas en mortero 1:3 de cemento y arena con hidrófugo, con grapas de acero inoxidable cada 40 cm en altura y juntas rehundidas de 1 cm. Las piedras no deben formar cornisas donde se junte nieve.</li>
<li>Remates en punta de mortero gris, con pendiente de 45° o más, para que la nieve no se acumule.</li>
<li>Trabajar con más de 5 °C y sin pronóstico de helada en las 48 horas siguientes.</li></ul>
<h3>Madera</h3>
<ul><li>Postes y travesaños de ciprés de la cordillera (con guía forestal), eucalipto colorado o pino impregnado CCA. La parte enterrada tiene que ser durable o impregnada.</li>
<li>Pedir las cajas y las puntas hechas en el aserradero. Cortar las puntas antes de impregnar y sellar todas las cabezas.</li>
<li>Impregnante natural de tono medio (roble o cedro) con filtro UV, en 3 manos, en la cerca, el cerco interno y las tablas del portón. Repaso cada 2 o 3 años. La tranquera existente se mantiene oscura.</li>
<li>Viga: rollizo seco de Ø 25-30 cm × 6,00 m, descortezado, sin pudrición ni grietas pasantes, impregnado. Apoyos con membrana bajo la madera.</li></ul>
<h3>Metal</h3>
<ul><li>Portón, ménsulas y botaguas de acero galvanizado en caliente o con antióxido epoxi, terminados en esmalte negro mate. Tornillería galvanizada o inoxidable.</li>
<li>Todos los anclajes van al núcleo de los pilares y nunca a la piedra del revestimiento.</li></ul>
<h3>Iluminación solar</h3>
<ul><li>Equipos con panel separado, 2700-3000 K, IP65 o más y batería apta para cargar con baja temperatura, con autonomía de 3 noches o más. Pedir la ficha técnica.</li>
<li>Toda la luz hacia abajo. Encendido crepuscular y 30 % de potencia después de las 00:30. Reemplazar las luces solares existentes de luz fría.</li></ul>
<h3>Señalética</h3>
<ul><li>Tabla de madera dura (o multilaminado fenólico enchapado) de 2,0 × 0,5 m y 2" de espesor. Letras talladas o en relieve, en color crema. Texto exterior: «TIERRAS MÁGICAS · Cabañas de montaña · Villa Pehuenia Moquehue». Texto interior: «BUEN VIAJE · Gracias por elegir Tierras Mágicas». Botaguas de chapa negra.</li>
<li>Placa del pilar de medidores en metal negro de 40 × 11 cm, con letras crema y la misma tipografía que la tabla.</li></ul>

<h2 id="computo"><span class="n">07</span>Cómputo y lista de compras</h2>
<p>Las cantidades salen de las medidas del croquis del dueño y del plano municipal. La planilla <b>lista_compras_proyecto_ejecutivo.xlsx</b> tiene columnas para el precio y el proveedor y calcula el total con 10 % de imprevistos. No se cargan precios: van los de las cotizaciones.</p>
<div class="tabla"><table><thead><tr><th>Rubro</th><th>Ítem</th><th>Unid.</th><th>Cant.</th><th>Origen</th><th>Proveedor</th></tr></thead><tbody>{filas_c}</tbody></table></div>
<h3>Quién ejecuta</h3>
<div class="tabla"><table><thead><tr><th>Trabajo</th><th>Mano de obra propia</th><th>Requiere</th></tr></thead><tbody>{quien}</tbody></table></div>

<h2 id="obra"><span class="n">08</span>Plan de obra</h2>
<div class="diag">{gantt()}</div>
<ul>
  <li><b>E0 · Diciembre, semanas 1 y 2:</b> replanteo con estacas e hilo, verificación estructural, muestra de piedra en M3, cotizaciones y compras. <b>Gate:</b> no se empieza la obra sin la verificación de la viga y sin el acuerdo con la constructora vial.</li>
  <li><b>E1 · Antes de la temporada alta:</b> la viga nueva y la tabla primero, por seguridad e imagen. Después, la pintura de los mojones y la restauración de la tranquera.</li>
  <li><b>E2 · Enero y febrero:</b> piedra en pilares, mojones y medidores; pircas y atrio. Trabajar en días de semana y tener un paso alternativo por la tranquera.</li>
  <li><b>E3 · Febrero y marzo:</b> la cerca del frente, el cerco interno, el portón nuevo, el sendero y las luces.</li>
  <li><b>E4 · Marzo y abril:</b> paisajismo completo y riego.</li>
  <li><b>E5 · Fin de abril y después del primer invierno:</b> controlar las luces, reponer plantas y retocar el impregnante.</li>
</ul>

<h2 id="verificar"><span class="n">09</span>Verificaciones y riesgos</h2>
<div class="tabla"><table><thead><tr><th>Tema</th><th>Qué hacer</th><th>Cuándo</th></tr></thead><tbody>
<tr><td>Viga, anclajes y cartel</td><td>Cálculo o verificación de un profesional: sección del rollizo, varillas y riendas</td><td>E0</td></tr>
<tr><td>Pilares del portal</td><td>Revisar el núcleo y la fundación al retirar la viga, antes de revestir (la piedra suma ≈ 400 kg por pilar)</td><td>E1</td></tr>
<tr><td>Cuneta frente al portal</td><td>Confirmar con la constructora el paso peatonal; si no hay paso, se aplica la variante sin atrio ni sendero</td><td>E0</td></tr>
<tr><td>Piedra</td><td>Muestra de 50 × 50 cm aprobada por el dueño antes de comprar el total</td><td>E0</td></tr>
<tr><td>Especies</td><td>Confirmación del vivero de nativas (procedencia y disponibilidad)</td><td>E0-E3</td></tr>
<tr><td>Tanques de gas</td><td>Sin luces, cables ni coníferas junto a los tanques; respetar las distancias que indique el gasista</td><td>E3-E4</td></tr>
<tr><td>Luces solares en invierno</td><td>Medir el primer invierno; si no alcanza, el cartel pasa a 12 V (plan B)</td><td>E5</td></tr>
<tr><td>Agua de la ruta nueva (+0,50 m)</td><td>Verificar al terminar la obra vial que el agua vaya a la cuneta y no hacia el atrio ni la tranquera</td><td>Final de la obra vial</td></tr>
</tbody></table></div>

<h2 id="cotizar"><span class="n">10</span>Pedido de cotización por proveedor</h2>
<p>Pedir 3 cotizaciones por proveedor, con fecha, plazo de entrega y forma de pago, y cargarlas en la planilla.</p>
<ul>{cotiz}</ul>

<footer>
  <p>Planos a escala aproximada, con las medidas del croquis del dueño y del plano municipal. Fotomontajes ilustrativos. Generado con <span style="font-family:var(--f-mono)">generar_ejecutivo.py</span>; las cantidades salen del mismo código que dibuja los planos.</p>
  <p><b>Siguiente paso:</b> E0. Pedir las cotizaciones con la lista de la sección 10, encargar la verificación estructural de la viga y armar la muestra de piedra en M3.</p>
</footer>
</div>
"""


if __name__ == "__main__":
    (BASE / "proyecto_ejecutivo.html").write_text(pagina(), encoding="utf-8")
    print("ok proyecto_ejecutivo.html + lista_compras_proyecto_ejecutivo.xlsx")
