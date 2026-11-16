# -*- coding: utf-8 -*-
"""Plan de Negocios v3 (reformulado desde cero). Uso: build_plan_v3.py <dir_gpx> <out_dir>"""
import sys, os, math
import xml.etree.ElementTree as ET
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

GDIR, OUT = sys.argv[1], sys.argv[2]
NS = {"g": "http://www.topografix.com/GPX/1/1"}

# ------------------------------------------------------------------ mapa de contexto
TM = (-38.9011, -71.2909); ACC = (-38.902440, -71.064667); TQ = (-38.832922, -71.058162); LIT = (-38.867250, -71.027544)
BASES = {"Base 1 Inicio": (-38.832050, -71.066724), "Base 2 Vaquero": (-38.814204, -71.050709), "Base 3 Chivero": (-38.807993, -71.063218)}
k = math.cos(math.radians(38.85))
fig, ax = plt.subplots(figsize=(11, 7.2), dpi=150)
for f in sorted(os.listdir(GDIR)):
    r = ET.parse(os.path.join(GDIR, f)).getroot()
    t = [(float(p.get("lat")), float(p.get("lon"))) for p in r.iterfind(".//g:trkpt", NS)]
    ys, xs = zip(*t); ax.plot(xs, ys, color="#bdbdbd", lw=0.7, zorder=1)
ax.plot(TM[1], TM[0], "*", ms=20, color="#d4a017", mec="k", zorder=6); ax.annotate("TIERRAS MÁGICAS\n(Moquehue)", (TM[1], TM[0]), fontsize=9, weight="bold", xytext=(8, 6), textcoords="offset points")
ax.plot(ACC[1], ACC[0], "*", ms=15, color="#ff7f00", mec="k", zorder=6); ax.annotate("Acceso RP13/RP12", (ACC[1], ACC[0]), fontsize=8.5, weight="bold", xytext=(6, -12), textcoords="offset points")
ax.plot(TQ[1], TQ[0], "P", ms=10, color="#7a3e00", zorder=6); ax.annotate("Tranquera 1", (TQ[1], TQ[0]), fontsize=8, xytext=(6, -10), textcoords="offset points")
for n, (la, lo) in BASES.items():
    ax.plot(lo, la, "s", ms=9, color="#0b3d2e", zorder=6); ax.annotate(n, (lo, la), fontsize=7.5, xytext=(6, 3), textcoords="offset points", color="#0b3d2e")
ax.plot(LIT[1], LIT[0], "^", ms=9, color="#c00000", zorder=6); ax.annotate("Litrán", (LIT[1], LIT[0]), fontsize=8, xytext=(6, -10), textcoords="offset points", color="#c00000")
ax.annotate("CAMPO\n(dividido por la RP12)", (-71.075, -38.815), fontsize=10, weight="bold", color="#1b7837", ha="center")
ax.annotate("← hacia Paso Icalma / Chile", (-71.30, -38.84), fontsize=9, color="#762a83")
ax.annotate("Traslado complejo → campo: ≈27,5 km hasta el acceso\n≈34–37 km hasta la Tranquera 1 (ida)", (-71.27, -38.935), fontsize=8.5,
            bbox=dict(boxstyle="round", fc="white", ec="#999"))
ax.set_xlim(-71.33, -71.00); ax.set_ylim(-38.95, -38.72); ax.set_aspect(1 / k)
x0, y0 = -71.32, -38.945; dl = 1 / (111.32 * k); ax.plot([x0, x0 + 2 * dl], [y0, y0], "k-", lw=3); ax.annotate("2 km", (x0, y0), xytext=(0, 4), textcoords="offset points", fontsize=8)
ax.tick_params(labelsize=7); ax.grid(True, lw=0.3, alpha=0.5)
ax.set_title("Paso del Arco Adventure — complejo de origen, acceso y campo (trazas del titular en gris)", fontsize=10)
fig.text(0.01, 0.005, "Esquema sin cartografía de fondo. Distancias por la red de trazas GPX del titular. No representa límites legales ni accesos autorizados.", fontsize=7, color="#555")
MAPA = os.path.join(OUT, "mapa_contexto_v3.png"); ax.plot(-71.291336, -38.900986, "*", ms=12, color="#d4a017", mec="k", zorder=6); ax.annotate("+ MILENKA (≈40 m)", (TM[1], TM[0]), fontsize=8, xytext=(8, -14), textcoords="offset points", color="#7a5c00")
fig.savefig(MAPA, bbox_inches="tight"); plt.close(fig)

# ------------------------------------------------------------------ documento
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)
for s in doc.sections: s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(1.8)
def shade(c, col):
    pr = c._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), col); pr.append(sh)
def T(h, rows, w, size=8):
    t = doc.add_table(rows=1, cols=len(h)); t.style = "Table Grid"; t.autofit = False
    for i, x in enumerate(h):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(x); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "1F3A2E")
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""; r = cs[i].paragraphs[0].add_run("" if v is None else str(v)); r.font.size = Pt(size)
    for i, x in enumerate(w): t.columns[i].width = Cm(x)
    for row in t.rows:
        for i, x in enumerate(w): row.cells[i].width = Cm(x)
    doc.add_paragraph(); return t
def H(t, l=1): doc.add_heading(t, level=l)
def P(t, b=False, i=False):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = b; r.italic = i; return p
def B(t, lab=None):
    p = doc.add_paragraph(style="List Bullet")
    if lab: r = p.add_run(lab + " "); r.bold = True
    p.add_run(t)

p = doc.add_paragraph(); r = p.add_run("PASO DEL ARCO ADVENTURE"); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)
p = doc.add_paragraph(); r = p.add_run("Plan de Negocios v3.2 — Reformulado desde cero"); r.font.size = Pt(15)
P("Travesías 4x4 y experiencias en el campo y la zona de Paso del Arco, para los huéspedes de Tierras Mágicas, Milenka y complejos asociados; con proyección a travesías binacionales con Chile.", b=True)
P("Versión 3.2 · 16/11/2026 (Milenka: -38.900986, -71.291336, a ≈40 m de Tierras Mágicas, 3 cabañas de 6 plazas, mismos cuadros tarifarios y políticas; ambos son los primeros asociados) · Documento de trabajo para decisión del titular. Reemplaza a las versiones 1 a 2.5, que pasan a ser antecedentes. No es un estudio de factibilidad ni habilita la operación.", i=True)

H("Cómo leer este documento")
T(["Etiqueta", "Significado"], [
    ("CONF", "Confirmado por el titular en esta conversación o en sus sistemas (p. ej. la configuración de reservas de Tierras Mágicas)."),
    ("EXT", "Extraído de archivos del titular (24 GPX, dossier v1, anexo v1)."),
    ("EXTW", "Investigación externa con fuente (§17). Mayormente prensa regional: verificar en fuente oficial."),
    ("INF", "Inferencia analítica propia."), ("HIP", "Hipótesis o propuesta a validar."), ("PEND", "Dato faltante."), ("REC", "Recomendación."),
], [2.5, 14.5])

# 1
H("1. Resumen ejecutivo")
P("Qué cambió respecto del plan anterior", b=True)
B("El plan anterior partía de 24 recorridos GPX y de un campo a desarrollar. Este parte del cliente: los huéspedes de complejos de alojamiento de la zona, empezando por Tierras Mágicas y Milenka (CONF titular). Las rutas dejan de ser la base del plan: se diseñan después, a partir de un relevamiento nuevo desde cero (CONF titular).")
B("El negocio se define como un OPERADOR DE TRAVESÍAS 4x4 Y EXPERIENCIAS DE NATURALEZA con tres ámbitos que se suman por etapas: el campo, la zona aledaña (Villa Pehuenia–Moquehue–Icalma, lado argentino) y, en el futuro, Chile (Icalma, Melipeuco).")
P("Tres hechos que ordenan el plan", b=True)
B("Los dos primeros asociados están juntos en Moquehue: Tierras Mágicas tiene 3 cabañas (6 + 6 + 4 plazas) más un dormi para 4 personas, con estadía mínima de 2 a 3 noches (CONF: sistema de reservas); Milenka, contiguo, tiene 3 cabañas de 6 plazas (CONF titular). Suman 34 plazas. Aun con ocupación plena, el techo es ≈6.200 huéspedes por año con estadías de 2 noches y ≈4.100 con estadías de 3 (34 × 365 ÷ estadía). La demanda real será una fracción de ese techo: el piloto puede apoyarse en estos dos complejos, pero la escala del negocio depende de sumar más asociados.", "Escala de la demanda cautiva (CONF + INF).")
B("De los complejos (Tierras Mágicas y Milenka, contiguos) al acceso RP13/RP12 hay ≈27,5 km y hasta la Tranquera 1 ≈34–37 km (INF, por las trazas del titular). Cada salida suma ≈70 km de traslado ida y vuelta, ≈1,5–2 h ida y vuelta a 35–45 km/h, el ritmo de ruta registrado en las trazas (INF a medir en el relevamiento R0). Un producto 'de medio día en el campo' ocupa casi el día entero de un vehículo y un guía. En invierno, la RP12 hasta la tranquera solo se transita en 4x4 (CONF).", "El traslado pesa (INF).")
B("Llevar huéspedes desde el complejo por RP11, RP13 y RP12 (rutas públicas) es transporte de pasajeros en vía pública. Villa Pehuenia exige una capacitación específica para guías de 4x4 y la provincia tiene un registro de prestadores (EXTW). La habilitación es el primer cuello de botella.", "Regulación (EXTW, PEND).")
P("Recomendación", b=True)
B("GO a la Etapa 0 (≈3–4 meses): relevamiento desde cero con el sistema de códigos y Wikiloc, validación de demanda con huéspedes de Tierras Mágicas y Milenka, y consultas regulatorias y de seguros. Inversión acotada a estudios y equipamiento de seguridad básico.", "1.")
B("Modelo de arranque de costos variables: guías y vehículos habilitados aliados (o el titular, si se habilita), venta a través de los complejos y producto empaquetado con la estadía. Sin flota propia ni obras hasta superar el piloto.", "2.")
B("NO-GO, por ahora, a vehículos, obras en las bases, alojamiento en el campo y productos en Chile.", "3.")

# 2
H("2. Estado del proyecto y pregunta de decisión")
T(["Elemento", "Definición"], [
    ("Fase", "PLC-00 Oportunidad reformulada → PLC-01 Prefactibilidad. Sin producto medido, habilitado, costeado ni vendido."),
    ("Pregunta de decisión", "¿Pueden los huéspedes de una red de complejos sostener un operador de travesías con base en el campo, y con qué productos, precios y modelo operativo?"),
    ("Perfil líder", "Desarrollo de producto y destino turístico."),
    ("Perfiles CORE", "Operaciones y seguridad 4x4 · Comercial B2B (complejos) · CFO / evaluación económica."),
    ("REQUIRED", "Legal-regulatorio (habilitación, transporte, seguros) · Datos/SIG (relevamiento y códigos)."),
    ("CONDITIONAL", "Gastronomía y bromatología (Etapa 1–2) · Ambiental/incendios · Ingeniería de bases."),
    ("FUTURE", "Comercio binacional y frontera (Etapa 4) · Hospitalidad/lodge · Montaña invernal."),
], [3.5, 13.5])

# 3
H("3. Modelo de negocio")
H("3.1 Propuesta de valor", 2)
T(["Para", "Qué recibe"], [
    ("Huésped del complejo", "Una travesía guiada, segura y lista para reservar desde su alojamiento: acceso a un campo privado de montaña y a la zona, con traslado o punto de encuentro, y opción de almuerzo de campo. Sin planificar ni arriesgar su vehículo."),
    ("Complejo asociado", "Una actividad diferencial para vender más noches y mejores tarifas, ingreso por comisión, y argumentos para temporada media y baja. Sin operar ni asumir el riesgo de la actividad."),
    ("Titular", "Monetizar el campo y su conocimiento del territorio con una operación escalable por etapas, alimentada por demanda cautiva."),
], [3.5, 13.5])
H("3.2 Cómo funciona (B2B2C)", 2)
B("Los complejos (Tierras Mágicas, Milenka y asociados) promocionan y venden las travesías a sus huéspedes: en la reserva, en el mensaje de bienvenida y en el Welcome Book.", "Canal:")
B("Paso del Arco Adventure opera: guía, vehículo habilitado (propio más adelante, aliado al inicio), seguridad, recorridos y experiencias en las bases.", "Operación:")
B("El huésped paga la travesía (directo o a través del complejo); el complejo recibe una comisión o el producto se vende en paquete 'estadía + travesías'.", "Cobro:")
B("Tierras Mágicas ya cuenta con un sistema propio de reservas con módulo de turnos para recursos con horario y cupo, mensajes automáticos por WhatsApp y Welcome Book (CONF: repositorio del sistema). Puede ofrecer y agendar las travesías sin desarrollo nuevo (INF a verificar en la práctica).", "Activo existente:")
H("3.3 Fuentes de ingreso", 2)
T(["Fuente", "Descripción", "Estado"], [
    ("Travesías del campo", "Medio día y día completo por las huellas internas del campo", "HIP — núcleo"),
    ("Travesías campo + zona", "Día completo combinando el campo con miradores, lagunas y patrimonio de la zona (con autorizaciones)", "HIP"),
    ("Paquetes 'estadía + travesías'", "2–3 travesías distintas durante una estadía en el complejo (el huésped duerme en el complejo)", "HIP — clave para el canal"),
    ("Experiencias en bases", "Almuerzo de campo en Vaquero, actividades familiares en Chivero, como complemento", "HIP; sujeto a habilitación y régimen de fuego"),
    ("Salidas privadas y grupos", "Grupos, empresas, celebraciones", "HIP"),
    ("Travesías binacionales", "Día con almuerzo en Icalma; travesías de 2+2 días campo–Chile con alojamiento en Chile", "HIP — futuro (Etapa 4)"),
], [4.2, 9.3, 3.5])
H("3.4 Alternativas de operación", 2)
T(["Modelo", "Ventajas", "Desventajas", "Cuándo"], [
    ("A. Prestador aliado habilitado (guía y vehículo)", "Sin inversión; legal desde el día 1; aprovecha guías ya capacitados", "Comparte margen; menos control de la experiencia", "Etapa 0–1 (REC)"),
    ("B. Titular habilitado como prestador, vehículo propio existente", "Más margen y control", "Requiere habilitación personal, seguro y licencia de transporte; capacidad limitada a un vehículo", "Etapa 1 si se habilita"),
    ("C. Flota propia y guías contratados", "Escala y marca propia", "Inversión y costo fijo altos; riesgo de subutilización", "Etapa 2–3 con demanda probada"),
    ("D. Convoy con vehículos de los huéspedes", "Sin inversión en flota; atractivo para dueños de 4x4", "Responsabilidad por vehículos ajenos; segmento acotado", "Complemento desde Etapa 1"),
], [4.4, 4.4, 4.6, 3.6])

# 4
H("4. Territorio y ámbitos")
doc.add_picture(MAPA, width=Inches(6.6))
T(["Ámbito", "Qué incluye", "Estado del conocimiento"], [
    ("Campo (CONF)", "≈2.000 ha informadas, entre el Cerro Piñihue y la costa del Arroyo del Arco; dividido por la RP12 pública. Sector oeste: Base 1 Inicio (quincho con cocina y baño) y Base 3 Chivero. Sector este: Base 2 Vaquero. Tranquera 1 sobre la RP12.", "Sin mensura ni polígono. Bases con coordenadas; infraestructura de Vaquero y Chivero no relevada."),
    ("Acceso (CONF)", "Intersección RP13/RP12 (-38.902440, -71.064667) → ≈9,3 km por RP12 hasta la Tranquera 1. Invierno: solo 4x4; resto del año: vehículo de calle no bajo.", "Medido sobre trazas."),
    ("Zona aledaña (AR)", "Villa Pehuenia, Moquehue, lado argentino del Paso Icalma, lagunas (Pilhue, Corazón, del Arco), Aduana Vieja, Batea Mahuida (Comunidad Puel).", "Titularidad y autorizaciones por punto: PEND. Antecedentes: 24 trazas del titular."),
    ("Chile (futuro)", "Icalma, Lonquimay, Melipeuco, Conguillío.", "Sin relevar. Requisitos binacionales: PEND."),
], [3.2, 8.6, 5.2])
B("Contexto territorial sensible: hay reclamos y conflictos territoriales de comunidades mapuche documentados en la zona, incluido uno en el paraje Paso del Arco (EXTW). Antes de invertir: estudio de títulos y mensura.", "Alerta:")
B("Régimen de fuego: la prensa informó la prohibición provincial de hacer fuego por emergencia ígnea (Decreto 198/2025, EXTW). Afecta al asado a la estaca y a cualquier fogón: verificar vigencia y excepciones.", "Alerta:")
B("Los 24 GPX grabados por el titular quedan como ANTECEDENTE (CONF titular: nuevo relevamiento desde cero). Ya sirvieron para medir accesos y distancias; los recorridos comerciales se definen con el relevamiento nuevo.", "Antecedentes:")

# 5
H("5. Clientes y demanda")
H("5.1 Segmentos", 2)
T(["Segmento", "Origen", "Qué busca (HIP)", "Prioridad"], [
    ("Huéspedes de Tierras Mágicas", "Complejo vinculado al titular, Moquehue", "Actividad de naturaleza además de lago, tina y kayaks", "1 — piloto"),
    ("Huéspedes de Milenka", "Complejo contiguo a Tierras Mágicas, 3 cabañas de 6 plazas (CONF)", "Ídem", "1 — piloto"),
    ("Huéspedes de complejos asociados", "Red a construir en Villa Pehuenia–Moquehue", "Ídem", "2"),
    ("Grupos privados y empresas", "Regional", "Exclusividad, celebración, incentivo", "2"),
    ("Entusiastas 4x4", "Regional y nacional", "Recorrer con su propio vehículo con guía", "3"),
    ("Viajeros de travesías largas", "Nacional e internacional", "Multi-día, binacional", "4 — futuro"),
], [4.2, 4.5, 5.6, 2.7])
H("5.2 Cómo se calcula la demanda (sin inventar cifras)", 2)
P("Salidas demandadas por complejo = plazas × 365 × ocupación ÷ estadía media ÷ tamaño de grupo × tasa de compra × travesías por estadía", b=True)
T(["Variable", "Tierras Mágicas", "Milenka", "Fuente"], [
    ("Plazas", "16 en cabañas + 4 en dormi (CONF)", "18 (3 cabañas × 6, CONF titular)", "Sistema de reservas TM · titular"),
    ("Ocupación anual", "PEND (el panel de TM la calcula)", "PEND", "Registros de cada complejo"),
    ("Estadía media", "≥ 2–3 noches por política (CONF); media real PEND", "≥ 2–3 noches: mismas políticas que TM (CONF); media real PEND", "Registros"),
    ("Tamaño de grupo", "PEND", "PEND", "Registros"),
    ("Tasa de compra", "HIP — se mide en el piloto", "HIP", "Preventa y encuestas"),
    ("Travesías por estadía", "HIP", "HIP", "Piloto"),
], [3.5, 5.2, 2.6, 5.7])
P("Techo conjunto de Tierras Mágicas + Milenka (INF): 34 plazas × 365 ÷ estadía media → ≈6.200 huéspedes/año con 2 noches; ≈4.100 con 3 noches (TM sola ≈2.900 / ≈1.950; Milenka sola ≈3.300 / ≈2.200). Es un máximo teórico con ocupación del 100%: la demanda real será una fracción. Ventajas: están a ≈40 m (Milenka -38.900986, -71.291336, CONF), comparten un único punto de salida y se pueden juntar huéspedes de ambos en la misma salida; y como tienen los mismos cuadros tarifarios y políticas (CONF), el paquete “estadía + travesías” puede tener un solo precio y una sola política para los dos.", i=True)
H("5.3 Contexto del destino (EXTW)", 2)
B("Villa Pehuenia–Moquehue registró 95% de ocupación en el fin de año 2025-26 y una semana de 89% en julio de 2026, con +21 puntos interanuales en invierno (prensa citando al Ministerio de Turismo). Verificar series completas en el Observatorio de Turismo de Neuquén.")
B("Competencia: un operador local (Moquehue) ofrece travesías 4x4 regionales, incluido Paso del Arco y la antigua aduana; hay otros prestadores en directorios. Diferencial a construir: acceso exclusivo al campo privado + venta integrada en los complejos + experiencias en las bases.")

# 6
H("6. Portafolio de productos")
P("Sin tarifas ni capacidades: se fijan con el relevamiento, el piloto y las cotizaciones. Todos parten del complejo (traslado) o de un punto de encuentro.", i=True)
T(["Cód.", "Producto", "Ámbito", "Duración desde el complejo (INF)", "Cliente", "Etapa"], [
    ("T1", "Travesía del Campo — medio día en el campo", "Campo", "≈5–6 h con traslado", "Familias, parejas", "1"),
    ("T2", "Gran Travesía del Campo — día completo con almuerzo en Vaquero", "Campo", "Día completo", "Grupos, parejas", "1"),
    ("T3", "Campo y Paso del Arco — campo + Aduana Vieja, lagunas y miradores", "Campo + zona AR", "Día completo", "Todos", "2"),
    ("T4", "Paquete Estadía + Travesías — 2 o 3 travesías distintas durante la estadía", "Campo + zona", "2–3 días (duerme en el complejo)", "Huéspedes de 3+ noches", "1–2"),
    ("T5", "Convoy con tu 4x4 — guía y radio para vehículos de huéspedes", "Campo", "Medio día / día", "Dueños de 4x4", "1–2"),
    ("T6", "Mesa de campo — almuerzo y actividades en Vaquero / Chivero", "Campo", "Medio día", "Familias, no 4x4", "2"),
    ("T7", "Invierno en el campo — travesía corta en nieve con almuerzo caliente", "Campo", "Medio día", "Turismo de invierno", "3 (prefactibilidad)"),
    ("T8", "Día de frontera — Icalma con almuerzo de cocina chilena", "Binacional", "Día completo", "Con documentación", "4"),
    ("T9", "Travesía binacional 2 + 2 — dos días campo, dos días Chile con alojamiento en Chile", "Binacional", "4 días", "Viajeros de aventura", "4"),
], [1, 6.3, 2.4, 3, 2.6, 1.7], size=7.5)
P("Clave comercial (REC): el producto que mejor encaja con el canal es T4. Convierte la estadía en un programa, sube el ticket del complejo y reparte el costo del traslado en un vínculo de varios días.", b=True)

# 7
H("7. Modelo operativo")
B("Reserva en el complejo o por WhatsApp → confirmación con cupo y requisitos → recordatorio con qué llevar → retiro en el complejo o encuentro en la Tranquera 1 → briefing en Inicio → travesía → regreso → reseña.", "Flujo:")
B("Fuera del invierno, el huésped puede llegar por su cuenta hasta Inicio en vehículo de calle no bajo (CONF): reduce el traslado y evita el transporte de pasajeros. En invierno: solo con traslado 4x4 habilitado.", "Encuentro vs. traslado:")
B("Todo recorrido que una el sector oeste con Vaquero cruza la RP12: cruces fijos, señalización y un procedimiento para el convoy.", "Cruce de la RP12:")
B("Dirección (titular) · Operaciones y seguridad (puede detener una salida) · Guía/conductor habilitado · Apoyo/cierre en salidas de más de un vehículo · Base/cocina en T2 y T6 · Reservas en los complejos.", "Roles mínimos:")
B("Comunicación (medir cobertura; radio o satelital), botiquín y primeros auxilios, kit de recuperación, ficha de cada recorrido con puntos de retorno, reglas de clima y cancelación, registro de cada salida.", "Seguridad:")

# 8
H("8. Relevamiento desde cero (Etapa 0)")
P("Objetivo: construir la base de datos del territorio con la que se diseñan los productos. Se hace con Wikiloc y el sistema de códigos ZONA/TERRITORIO-TIPO-NN ya definido (Anexo A).")
T(["Bloque", "Qué relevar", "Resultado"], [
    ("R0 Accesos desde los complejos", "Tierras Mágicas y Milenka (contiguos: un solo punto de salida) → acceso RP13/RP12 → Tranquera 1; tiempos reales por estación; puntos de encuentro y estacionamiento", "Tiempos de traslado medidos; punto de encuentro"),
    ("R1 Campo completo", "Bases, tranqueras, cruces de la RP12, huellas internas, miradores, vados, aguadas, límites (Cerro Piñihue, costa del Arroyo del Arco), puesto del Arroyo del Arco, puntos de riesgo", "Mapa base del campo; 2–3 recorridos internos candidatos con tiempos"),
    ("R2 Zona aledaña (AR)", "Aduana Vieja, lagunas, miradores, patrimonio; titularidad y autorizaciones de cada punto", "Recorridos campo + zona candidatos"),
    ("R3 Servicios", "Gastronomía, combustible, salud, aliados en la zona", "Mapa de servicios y aliados"),
    ("R4 Chile (gabinete)", "Requisitos de cruce y transporte; aliados en Icalma y Melipeuco", "Informe de prefactibilidad binacional (no se releva en campo todavía)"),
], [3.6, 8.4, 5])
B("Kit ya disponible (CONF de entregas previas): ficha de bolsillo para nombrar puntos en Wikiloc, importador que convierte el GPX descargado en planilla y alerta errores, GPX de puntos conocidos y hoja de ruta de 5 jornadas para el campo (se agrega R0).", "Herramientas:")
B("Fotos geolocalizadas por punto; tiempos con el reloj del celular; una traza por jornada; marcar cada tramo de ruta pública.", "Método:")

# 9
H("9. Legal, seguridad y sostenibilidad")
T(["Tema", "Estado", "Con quién verificar"], [
    ("Habilitación de prestador 4x4 / capacitación municipal", "Capacitación obligatoria informada en 2025 (EXTW); requisitos exactos PEND", "Municipalidad de Villa Pehuenia"),
    ("Registro provincial de prestadores", "Res. 437/2024 informada (EXTW); alcance PEND", "Ministerio de Turismo de Neuquén"),
    ("Transporte de pasajeros desde los complejos", "Necesario si se retira al huésped (INF); requisitos PEND", "Autoridad provincial de transporte"),
    ("Seguros (RC, accidentes personales, vehículos, huéspedes con su 4x4)", "PEND", "2–3 aseguradoras, por escrito"),
    ("Contratos con complejos", "PEND: comisión, responsabilidad, cancelaciones, datos de huéspedes", "Asesor legal"),
    ("Gastronomía en bases", "PEND", "Autoridad bromatológica"),
    ("Fuego e incendios", "Prohibición informada (EXTW); vigencia PEND", "Manejo del Fuego provincial"),
    ("Títulos, mensura y contexto territorial", "PEND crítico", "Abogado, agrimensor, catastro"),
    ("Ambiente: huellas fijas, vados, fauna, áreas protegidas", "Antecedente de denuncias por 4x4 en áreas protegidas (EXTW 2026)", "Autoridad ambiental"),
    ("Binacional (Etapa 4)", "PEND: transporte internacional, documentación, seguros en Chile, controles sanitarios de alimentos, horarios del paso", "Organismos de frontera de ambos países"),
], [5, 6.5, 5.5], size=7.5)
B("Posicionarse como '4x4 responsable': huellas fijas, grupos chicos, sin ingreso a áreas protegidas ni a campos ajenos sin autorización. Es además un diferencial frente a la mala prensa del rubro.", "Sostenibilidad (REC):")

# 10
H("10. Estrategia comercial")
B("Acuerdo marco con Tierras Mágicas y Milenka, los primeros asociados (CONF): comisión o precio neto, materiales, reservas, cancelaciones; salidas compartidas entre huéspedes de ambos. Luego, una red de 5–10 complejos asociados en Villa Pehuenia–Moquehue (HIP: el número sale del punto de equilibrio).", "1. Red de complejos:")
B("La travesía aparece en la reserva, en el mensaje de confirmación, en la bienvenida y en el Welcome Book del complejo; en el sistema de Tierras Mágicas puede cargarse como turno con cupo (INF).", "2. Integración en la estadía:")
B("Paquete 'Estadía + Travesías' (T4) para estadías de 3+ noches; incentivo para temporada media y baja. Tierras Mágicas y Milenka comparten cuadros tarifarios y políticas (CONF): el paquete se arma sobre ese tarifario común (mismas temporadas, estadías mínimas, seña y cancelación) y la travesía se suma con su propia política de clima.", "3. Paquete:")
B("Fotos y videos propios del relevamiento, mapa ilustrado, ficha clara por producto (duración medida, exigencia, qué incluye, clima y cancelación). No publicar rutas ni accesos no autorizados.", "4. Contenido:")
B("Marca: evaluar si 'Paso del Arco' (topónimo asociado a un paraje con conflicto territorial) conviene como marca principal; verificar registro.", "5. Marca:")
B("Tasa de compra por complejo, ocupación por salida, ticket medio, margen por salida, reseñas, recompra y recomendación de los complejos.", "KPIs:")

# 11
H("11. Etapas y criterios GO / NO-GO")
T(["Etapa", "Alcance", "Inversión admisible", "GO si…"], [
    ("0 — Relevamiento y validación (≈3–4 meses)", "R0–R4; consultas legales y seguros; acuerdo con TM y Milenka; preventa o encuesta a huéspedes", "Estudios, agrimensura, seguridad básica, combustible de relevamiento", "Títulos y límites sin conflicto que impida operar; encuadre legal escrito; seguro cotizado; 2+ recorridos internos con ficha; interés medido de huéspedes"),
    ("1 — Piloto con huéspedes (1 temporada)", "T1, T2, T4, T5 con prestador aliado; registro de cada salida", "Mejoras mínimas en Inicio, señalización, comunicaciones, material comercial", "Cero incidentes graves; margen por salida positivo con costos reales; tasa de compra ≥ umbral definido; satisfacción ≥ umbral"),
    ("2 — Red de complejos y zona", "5–10 complejos; T3, T6; experiencias en bases", "Adecuación de Vaquero/Chivero solo con demanda probada", "Punto de equilibrio anual alcanzado; complejos que renuevan"),
    ("3 — Escala e invierno", "Flota propia si conviene; T7", "Vehículos, equipo invernal", "Análisis propio vs. aliado favorable; prefactibilidad invernal aprobada"),
    ("4 — Binacional y pernocte", "T8, T9; base o alojamiento en el campo o en Chile", "Según estudio específico", "Requisitos binacionales escritos; socio en Chile; demanda probada de T3/T4"),
], [3.6, 4.6, 4, 4.8], size=7.5)

# 12
H("12. Modelo económico-financiero")
P("El libro 'Modelo_Economico_Paso_del_Arco_v3.xlsx' tiene fórmulas listas y datos de entrada vacíos (salvo las plazas de Tierras Mágicas, CONF). No se inventan precios ni costos.")
T(["Bloque", "Lógica"], [
    ("Demanda por complejo", "plazas × 365 × ocupación ÷ estadía ÷ grupo × tasa de compra × travesías por estadía = salidas/año"),
    ("Costo por salida", "traslado (km complejo↔campo × consumo × combustible + desgaste) + km del recorrido + horas de guía y apoyo + comida + seguro por persona + comisión del complejo + pago al prestador aliado + impuestos"),
    ("Margen por salida", "ingreso (precio × personas) − costo variable"),
    ("Punto de equilibrio", "costos fijos anuales ÷ margen medio por salida = salidas/año; ÷ salidas por complejo = complejos necesarios"),
    ("Escenarios", "conservador / base / favorable sobre salidas, precio y costo"),
    ("Flujo 12 meses y CAPEX por etapa", "estacionalidad mensual; inversiones solo con su cotización y condición de liberación"),
], [4, 13])
B("Con un traslado de ≈70 km por salida y grupos chicos, el costo de traslado y las horas de guía dominan el costo variable (INF). Palancas: agrupar huéspedes de varios complejos por salida, encuentro en la Tranquera 1 fuera del invierno, y paquetes de varios días.", "Lectura:")

# 13
H("13. Riesgos principales")
T(["Riesgo", "Impacto", "Mitigación"], [
    ("Demanda cautiva insuficiente (TM + Milenka = 34 plazas)", "Crítico", "Red de complejos desde la Etapa 0; medir la tasa de compra antes de invertir"),
    ("Habilitación y transporte de pasajeros", "Crítico", "Prestador aliado habilitado; consultas escritas; encuentro en la tranquera cuando se pueda"),
    ("Títulos y contexto territorial", "Crítico", "Estudio de títulos y mensura como primer gate"),
    ("Seguridad de pasajeros y cruce de la RP12", "Crítico", "Fichas de recorrido, procedimientos, comunicaciones, capacitación"),
    ("Fuego y bromatología en las bases", "Alto", "Menú sin fuego abierto; habilitación; agua segura"),
    ("Clima y estacionalidad (RP12 solo 4x4 en invierno)", "Alto", "Calendario por estación; productos de temporada media; costos variables"),
    ("Reputación del 4x4 en la zona", "Alto", "Código de conducta; huellas fijas; sin áreas protegidas"),
    ("Dependencia de un vehículo/guía", "Medio", "Al menos dos prestadores aliados"),
    ("Inflación y tipo de cambio", "Alto", "Precios revisables; modelo en moneda constante"),
    ("Binacional (futuro)", "Alto", "Solo con requisitos escritos y socio chileno"),
], [6.5, 2, 8.5], size=8)

# 14
H("14. Plan de los próximos 90 días")
T(["Semana", "Tarea", "Responsable", "Entregable"], [
    ("1–2", "Cargar ocupación y estadía media de Tierras Mágicas (panel) y de Milenka; acordar condiciones con Milenka", "Titular", "Tabla de complejos completa"),
    ("1–4", "Relevamiento R0 y R1 con Wikiloc y códigos", "Titular", "GPX + fotos → planilla importada"),
    ("1–6", "Consultas escritas: Municipalidad (4x4), Turismo (registro), transporte, fuego, bromatología", "Titular / asesor", "Respuestas escritas"),
    ("2–6", "Cotizar seguros; contactar 2 prestadores 4x4 habilitados", "Titular", "Cotizaciones y propuestas"),
    ("2–8", "Estudio de títulos y presupuesto de mensura", "Abogado / agrimensor", "Informe"),
    ("4–8", "Encuesta o preventa a huéspedes de TM y Milenka; borrador de acuerdo con complejos", "Titular", "Tasa de interés medida; acuerdo marco"),
    ("6–10", "Relevamiento R2–R3; diseño de T1, T2 y T4 con tiempos medidos", "Titular + producto", "Fichas de producto"),
    ("8–12", "Completar el modelo económico con datos reales", "CFO", "Modelo v3 completo"),
    ("12–14", "Comité GO/NO-GO Etapa 0", "Titular", "Acta"),
], [1.6, 9, 3, 3.4], size=8)

# 15
H("15. Datos faltantes críticos")
T(["Dato", "Para qué", "Cómo"], [
    ("Milenka: ocupación y estadía media reales, condiciones del acuerdo (plazas, coordenada, tarifas y políticas ya CONF)", "Demanda y acuerdo", "Titular / Milenka"),
    ("Ocupación y estadía media real de Tierras Mágicas", "Demanda", "Panel de Finanzas/Estadísticas del sistema de TM"),
    ("Tiempos reales de traslado complejo → campo por estación", "Producto y costo", "Relevamiento R0"),
    ("Requisitos de habilitación y transporte", "Modelo operativo", "Consultas escritas"),
    ("Seguros", "Costo y viabilidad", "Cotizaciones"),
    ("Títulos, mensura, contexto territorial", "Gate de inversión", "Estudio legal y agrimensura"),
    ("Disposición a pagar y tasa de compra de huéspedes", "Precio y demanda", "Encuesta / preventa / piloto"),
    ("Régimen de fuego vigente", "Gastronomía", "Manejo del Fuego"),
    ("Infraestructura real de Vaquero y Chivero", "T2, T6", "Relevamiento R1"),
    ("Requisitos binacionales y aliados en Chile", "T8, T9", "Gabinete R4"),
], [6.5, 3.5, 7])

# 16
H("16. Decisiones del titular")
for i, d in enumerate([
    "Aprobar la Etapa 0 y su tope de gasto.",
    "Acordar con Milenka las condiciones (comisión o paquete) y definir la lista de complejos a invitar después.",
    "Definir si operará como prestador habilitado o con aliados al inicio.",
    "Aprobar el modelo de comisión o de paquete con los complejos.",
    "Encargar el estudio de títulos y la mensura.",
    "Fijar los umbrales de los gates (tasa de compra, satisfacción, margen mínimo).",
    "Decidir la marca comercial.",
], 1): B(d, f"D{i}.")

# Anexos
H("Anexo A. Sistema de códigos (resumen)")
T(["Elemento", "Formato", "Ejemplo"], [
    ("Punto en el campo", "ZONA-TIPO-NN (zona de 1 letra: R, O, E, N, L, P)", "O-BAS-01 Base 1 Inicio"),
    ("Punto fuera del campo", "TERRITORIO-TIPO-NN (A=Argentina / C=Chile + lugar)", "CIC-GAS-01 almuerzo en Icalma"),
    ("Complejos asociados", "TERRITORIO-ALO-NN", "AMO-ALO-01 Tierras Mágicas · AMO-ALO-02 Milenka"),
    ("Ruta de un día", "RUT-PDA/AR/CL/BI-NN", "RUT-BI-01"),
    ("Travesía de varios días", "TRV-ÁMBITO-NN.Dn", "TRV-BI-01.D3"),
    ("En Wikiloc", "Se escribe como sea cómodo: 'amo alo 1', 'o bas 1'; puntos nuevos 'e vad n1'", "Ver Ficha de bolsillo v2"),
], [4, 7.5, 5.5])
P("Los complejos pasan a ser puntos del sistema: Tierras Mágicas = AMO-ALO-01 y Milenka = AMO-ALO-02 (Moquehue, contiguos); los demás asociados reciben su código ALO al relevarlos. Así, cada producto se describe como una secuencia que empieza y termina en el complejo.", i=True)
H("Anexo B. Qué se conserva de las versiones anteriores")
T(["Elemento", "Destino en v3"], [
    ("24 GPX del titular y su auditoría", "Antecedente. Sirvieron para medir accesos y distancias; no definen productos."),
    ("Matrices de 24 circuitos, priorización y portafolio v2", "Archivados (carpeta archivo_v2). Reemplazados por el portafolio T1–T9."),
    ("Investigación externa (regulación 4x4, fuego, demanda, competencia, contexto territorial)", "Se mantiene, con fuentes."),
    ("Respuestas del titular (RP12 pública, Tranquera 1, límites, transitabilidad, autoría)", "Se mantienen como CONF."),
    ("Sistema de códigos, ficha de bolsillo, importador y hoja de ruta", "Se mantienen como herramientas del relevamiento."),
], [6.5, 10.5])

H("17. Fuentes externas")
for n, u in [
    ("Villa Pehuenia lanza curso obligatorio para guías de travesías en 4x4 — NoticiasNQN (abr-2025)", "https://www.noticiasnqn.com.ar/noticias/2025/04/22/312417-villa-pehuenia-lanza-curso-obligatorio-para-guias-de-travesias-en-4x4"),
    ("Neuquén abrió la inscripción para formar prestadores (Res. 437/2024) — NoticiasNQN (jul-2026)", "https://www.noticiasnqn.com.ar/noticias/2026/07/23/344683-neuquen-abrio-la-inscripcion-para-formar-nuevos-prestadores-de-actividades-turisticas"),
    ("Denuncian ingreso ilegal de 4x4 a áreas protegidas — NoticiasNQN (jul-2026)", "https://www.noticiasnqn.com.ar/noticias/2026/07/23/344677-denuncian-el-ingreso-ilegal-de-camionetas-4x4-a-areas-protegidas-de-villa-pehuenia"),
    ("Multas por fuego en zonas prohibidas; Decreto 198/2025 — NoticiasNQN (dic-2025)", "https://www.noticiasnqn.com.ar/noticias/2025/12/26/325637-multaron-a-personas-por-acampar-y-hacer-fuego-en-zonas-prohibidas-en-la-zona-cordillerana"),
    ("Villa Pehuenia-Moquehue: 89% de ocupación en invierno 2026 — NoticiasNQN", "https://www.noticiasnqn.com.ar/noticias/2026/08/01/346030-villa-pehuenia-moquehue-alcanzo-un-89por_ciento-de-ocupacion-y-lidero-el-turismo-invernal-en-neuquen"),
    ("Fin de año 2025-26: 95% de ocupación — NoticiasNQN", "https://www.noticiasnqn.com.ar/noticias/2026/01/05/326095-villa-pehuenia-moquehue-fue-el-destino-preferido-para-recibir-el-2026-con-ocupacion-del-95por_ciento"),
    ("Observatorio de Turismo de Neuquén (fuente oficial a consultar)", "https://turismo.neuquen.gob.ar/observatorio-de-turismo"),
    ("Excursiones de un operador local (Moquehue) — Interpatagonia", "https://www.interpatagonia.com/villapehuenia/excursiones-impodi.html"),
    ("Conflicto territorial y desarrollo turístico en Villa Pehuenia-Moquehue — UNCo", "https://rdi.uncoma.edu.ar/handle/uncomaid/17079?show=full"),
    ("Reclamo territorial en el paraje Paso del Arco — La Izquierda Diario", "https://www.izquierdadiario.es/Neuquen-Exigen-la-regularizacion-de-las-tierras-de-la-comunidad-Tuwvn-Kupalmeo-Maliqueo"),
    ("Batea Mahuida y Comunidad Puel — NoticiasNQN (jul-2026)", "https://www.noticiasnqn.com.ar/noticias/2026/07/13/343558-nieve-antorchas-y-tradicion-batea-mahuida-celebro-sus-26-anos"),
]:
    B(f"{n} — {u}")
doc.save(os.path.join(OUT, "Plan_de_Negocios_Paso_del_Arco_v3_2.docx")); print("ok")
