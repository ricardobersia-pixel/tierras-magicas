# -*- coding: utf-8 -*-
import sys, os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
sys.path.insert(0, sys.argv[1])
from data_v23 import *
from docx.shared import Inches
MAPDIR = sys.argv[3]

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(1.8)

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), color); tcPr.append(sh)

def H(t, l=1): doc.add_heading(t, level=l)
def P(t, b=False, i=False):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = b; r.italic = i; return p
def B(t, lab=None):
    p = doc.add_paragraph(style="List Bullet")
    if lab:
        r = p.add_run(lab + " "); r.bold = True
    p.add_run(t); return p
def T(headers, rows, widths=None, size=8):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    for j, h in enumerate(headers):
        c = t.rows[0].cells[j]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(size)
        r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "1F3A2E")
    for row in rows:
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = ""; r = cells[j].paragraphs[0].add_run("" if v is None else str(v)); r.font.size = Pt(size)
    if widths:
        t.autofit = False
        for j, w in enumerate(widths): t.columns[j].width = Cm(w)
        for row in t.rows:
            for j, w in enumerate(widths): row.cells[j].width = Cm(w)
    doc.add_paragraph()
    return t

# Portada
p = doc.add_paragraph(); r = p.add_run("PASO DEL ARCO ADVENTURE"); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)
p = doc.add_paragraph(); r = p.add_run("Plan de Negocios v2.3 — Análisis integral, portafolio, modelo operativo y estructura económico-financiera"); r.font.size = Pt(14)
P("Versión 2.3 · 16/11/2026 · Documento de trabajo para decisión del titular. Base documental: Dossier IA v1, Anexo Maestro v1, los 24 GPX originales (RutasWKLC.zip) y el acceso RP13/RP12 con coordenada del titular (-38.902440, -71.064667), más investigación externa citada. No es un estudio de factibilidad ni habilita la operación.", i=True)
P("Complemento obligatorio: libro 'Matrices_y_Modelo_Financiero_Paso_del_Arco_v2_3.xlsx' (matrices completas, auditoría GPX, priorización con puntajes editables y modelo financiero con fórmulas).", i=True)

H("Cómo leer este documento")
T(["Etiqueta", "Significado"], [
    ("CONF", "Dato confirmado/aportado por el titular (según Dossier v1)."),
    ("EXT", "Dato extraído de archivos (Dossier v1, Anexo v1, GPX según su descripción)."),
    ("EXTW", "Investigación externa en internet, con fuente en §15. Mayormente prensa regional: verificar en fuente oficial."),
    ("INF", "Inferencia analítica propia a partir de los datos."),
    ("HIP", "Hipótesis/propuesta a evaluar."),
    ("PEND", "Pendiente de relevar o verificar."),
    ("REC", "Recomendación del equipo consultor."),
], [3, 14])
P("Ningún dato original fue modificado. Donde v2 propone una clasificación distinta a v1, se muestran ambas.")

# 0 Estado
H("0. Estado del proyecto y pregunta de decisión")
T(["Elemento", "Definición"], [
    ("Fase del ciclo de vida", "PLC-00 Oportunidad → entrada a PLC-01 Prefactibilidad. No hay producto medido, costeado, habilitado ni vendido."),
    ("Pregunta de decisión", "¿Justifica el territorio invertir en una Etapa 0 de validación de bajo costo, y bajo qué condiciones se habilita un piloto comercial?"),
    ("Respuesta corta (REC)", "SÍ a Etapa 0 con presupuesto acotado y tope fijado por el titular. NO a inversiones en vehículos, obras mayores o alojamiento hasta superar los gates de §9."),
    ("Perfil líder", "Desarrollo de destinos y producto turístico."),
    ("Perfiles CORE", "Operaciones y seguridad 4x4 · CFO/evaluación de inversiones · Legal-territorial."),
    ("REQUIRED", "SIG/datos (auditoría GPX) · Comercial/marketing."),
    ("CONDITIONAL", "Gastronomía y bromatología (Etapa 1–2) · Ingeniería de bases · Ambiental/incendios."),
    ("FUTURE", "Hospitalidad/lodge (Etapa 4) · Montaña invernal y rescate (Etapa 3)."),
], [4, 13])

# 1 Diagnóstico
H("1. Diagnóstico integral")
H("1.1 Lo que el proyecto tiene", 2)
B("Territorio informado de ~2.000 ha en el entorno de Paso del Arco / Villa Pehuenia–Moquehue (CONF; sin mensura).")
B("Tres bases georreferenciadas; Inicio con quincho, cocina y baño informados (CONF).")
B("24 GPX originales con 53 waypoints (EXT, auditados en v2.1): 1.318 km sumados, pero ≈457 km de red única (≈65% de superposición). Registros entre feb-2024 y nov-2026; ninguno de julio a septiembre.")
B("Destino con demanda turística probada a nivel destino: 95% de ocupación en fin de año 2025-26 y 89% en una semana de julio 2026, +21 puntos interanuales en invierno (EXTW, prensa regional citando al Ministerio de Turismo). Un resumen de búsqueda atribuye al Observatorio de Turismo de Neuquén 99.753 turistas y 71% de ocupación en plazas en la temporada estival 2024-25: dato a verificar en la fuente oficial.")
B("Borradores de manual operativo (PA-OPS-MAN-001), modelo operativo-comercial, modelo financiero y plan de implementación (EXT; no adjuntos a este análisis).")
H("1.2 Lo que el proyecto no tiene todavía", 2)
B("Acreditación de superficie, límites y título; ningún circuito medido, inspeccionado ni habilitado; ninguna tarifa, costo, capacidad ni demanda propia; ninguna habilitación ni seguro verificado (EXT, Dossier v1 §14–15).")
H("1.3 Hallazgos críticos de este análisis (nuevos respecto de v1)", 2)
B("Las tres bases están a 1,3–2,7 km entre sí (triángulo de ≈155 ha). Un campo de 2.000 ha equivale a un cuadrado de ≈4,5 km de lado. Por lo tanto, los tracks de 70–150 km clasificados como 'candidato núcleo' no pueden ser internos: son regionales o contienen tramos externos. El producto realmente propio será corto/medio día; las travesías largas dependen en gran medida de terceros.", "Escala (INF, cálculo propio; CONFIRMADO por los GPX en v2.1: solo 1 de 24 trazas, XX Circuito campo, queda íntegramente en el radio de 3 km de las bases).")
B("Lo defendible no son las rutas (muchas son caminos regionales que ya recorren otros operadores, EXTW) sino el acceso exclusivo a un campo privado de montaña + bases + hospitalidad rural. El plan se reorienta a ese activo.", "El activo real (INF).")
B("Existen reclamos y conflictos territoriales de comunidades mapuche documentados en la zona, incluido uno situado en el paraje Paso del Arco (EXTW). No se sabe si afectan al campo. Es el primer gate: sin título y límites claros no se invierte.", "Contexto territorial (EXTW).")
B("La prensa informa que el Decreto 198/2025 (emergencia ígnea) prohibía hacer fuego en todo Neuquén (EXTW, dic-2025). El asado a la estaca, núcleo de la propuesta de Vaquero, puede no ser operable en verano. Se requiere verificar vigencia y excepciones y diseñar un menú sin fuego abierto.", "Fuego vs. asado (EXTW).")
B("Villa Pehuenia implementó en 2025 una capacitación obligatoria para prestadores de excursiones 4x4, con requisitos informados de residencia en Neuquén ≥2 años, edad >21 y licencia para conducir 4x4 y transporte de pasajeros; la provincia tiene un registro de prestadores (Res. 437/2024) (EXTW). Esto condiciona quién puede guiar y favorece aliarse con prestadores ya habilitados.", "Regulación 4x4 (EXTW).")
B("En 2026 hubo denuncias por ingreso ilegal de 4x4 a áreas protegidas y una investigación por maniobras sobre una laguna congelada en Batea Mahuida (EXTW). Riesgo reputacional para el rubro, y a la vez oportunidad: posicionarse como '4x4 responsable en campo privado'.", "Licencia social (EXTW).")
H("1.4 Calidad de datos", 2)
P("v2.1: 17 discrepancias registradas (hoja 15). Resueltas con los GPX: los km del catálogo se reproducen exactamente; los 53 waypoints existen (el anexo omitió 6 nombres repetidos); 'Quincho' = Inicio (6 m); 'Puesto Vaquero' = Vaquero (31 m); el waypoint 'Inicio' de 009 es el inicio del track. Nuevas: saltos en línea recta incluidos en los km; altitudes sesgadas entre archivos; ~65% de redundancia; autoría Wikiloc no confirmada; posible carácter público del eje N–S.")

# 2 Plan de negocios
H("2. Plan de negocios — síntesis")
T(["Componente", "Propuesta v2"], [
    ("Misión (HIP)", "Abrir a visitantes un campo privado de montaña en Pehuenia con experiencias 4x4, de campo y gastronomía operadas con estándares profesionales de seguridad y cuidado ambiental."),
    ("Propuesta de valor (HIP)", "Exclusividad (territorio privado, grupos chicos) + seguridad (operación guiada, huellas controladas) + autenticidad rural (Vaquero, Chivero) + combinabilidad (medio día a jornada completa)."),
    ("Segmentos prioritarios (HIP)", "1) Turistas alojados en Villa Pehuenia–Moquehue (familias y parejas); 2) propietarios de 4x4; 3) grupos privados y empresas; 4) B2B formación en manejo (a validar)."),
    ("Modelo inicial (REC)", "Mixto D: alianza con prestadores 4x4 habilitados + convoy con vehículos de clientes; sin flota propia hasta evidencia."),
    ("Ingresos (HIP)", "Excursiones, gastronomía, experiencias familiares, cursos, salidas privadas; fee de acceso para operadores aliados."),
    ("Ventaja competitiva a construir", "Acceso exclusivo + bases + relato rural + estándar de seguridad documentado. Las travesías regionales no son diferenciales por sí solas."),
    ("Horizonte", "Etapa 0 (validación) → Etapa 1 (piloto de una temporada) → Etapas 2–4 condicionadas a gates."),
], [4, 13])

# 3 Bases
H("3. Matriz territorial — bases y puestos")
T(["Código", "Base", "Coordenadas", "Aportado (CONF)", "Lectura analítica (INF/EXTW)", "Validaciones (PEND)"],
  [(b[0], b[1], "Sin coordenadas" if b[2] is None else f"{b[2]:.6f}, {b[3]:.6f}", b[4], b[6], b[7]) for b in BASES], [2.2, 2, 2.8, 3.2, 4.5, 3.8], size=7)
P("Distancias en línea recta (cálculo propio; no son distancias por camino ni prueban conexión):", b=True)
T(["Desde", "Hasta", "km", "Rumbo °"], [(a, b, f"{c:.2f}", d) for a, b, c, d in DIST_BASES], [4, 5, 2, 2])
B("Coordenada del titular -38.902440, -71.064667, a ≈1.166 m. Desde ahí, por la rama NE (INF: RP12): Vista del Aluminé 1,3 km → Tranquera 9,3 km → Inicio ≈10,1 km (+≈330 m) → Cruce N 12,0 km → Vaquero ≈12,1 km → Chivero ≈13,1 km (camino final sin traza). Litrán queda a ≈6,9 km al SE por la RP13. Distancias por trazas, no comerciales.", "Acceso RP13/RP12 (CONF):")
B("RP12 pública en todo su recorrido; el campo queda dividido por ella, entre el Cerro Piñihue y la costa del Arroyo del Arco (referencias, no límites catastrales). Sector OESTE: Inicio, Chivero, Tranquera 1 (-38.832922, -71.058162) y el ramal hacia el Punto límite campo. Sector ESTE: Vaquero y, probablemente, el cruce de río que podría ser el Arroyo del Arco (HIP). Hasta la Tranquera 1: solo 4x4 en invierno; vehículo de calle no bajo el resto del año.", "Respuestas del titular (CONF, 16/11):")
B("(1) Fuera del invierno, el cliente puede llegar por su cuenta hasta Inicio: los productos de base (P01, P02, P04–P06) no necesitan traslado. (2) En invierno, la llegada exige 4x4: traslado con prestador habilitado o producto solo para clientes con 4x4. (3) Todo circuito que una el sector oeste con Vaquero cruza la RP12: hacen falta puntos de cruce fijos, señalización y un protocolo para el convoy. (4) XVilla Unión Corto va un 69% por la RP12: deja de ser un circuito propio. XX Circuito campo va solo un 14% por la ruta (≈20 km por huellas propias) y se confirma como circuito insignia.", "Implicancias (INF/REC):")
B("Inicio es la primera base desde el acceso: se confirma su papel de recepción, briefing y control (la v2.1 lo había puesto en duda por un error de estimación). Vaquero y Chivero forman el polo norte, ≈2–3 km más adelante, junto al Cruce N, donde llega un segundo camino desde el este.", "Lectura (INF/REC):")
B("Llegar a las bases exige ≈10–13 km de camino, probablemente público. Eso suma ≈20–26 km ida y vuelta por salida si el vehículo parte del acceso; impone requisitos de transporte para trasladar pasajeros; y condiciona el producto en invierno y en el deshielo. Alternativa a evaluar: que los clientes lleguen a Inicio en su propio vehículo (verificar si el camino es apto para 4x2).", "Consecuencias:")
B("Vaquero y Chivero están a ≈1,3 km: pueden diseñarse como un único polo con dos ambientes, compartiendo sanitarios, agua y personal, lo que reduce CAPEX y OPEX (REC).")
B("Las tres bases están concentradas; el resto del campo no tiene nodos. Ubicar el puesto del Arroyo del Arco es útil como punto de retorno/evacuación (REC).")
B("Organización territorial propuesta (HIP): zona de recepción (Inicio); polo de experiencias (Vaquero–Chivero); zona de circuitos internos con huellas fijas; zonas de exclusión (áreas sensibles, aguadas, sectores con animales); salidas regionales solo con autorización.")

# 4 Circuitos
sec = doc.add_section(); sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = sec.page_height, sec.page_width
H("4. Matriz individual de los 24 circuitos")
P("Clasificación v2 = propuesta de análisis, no clasificación aprobada. km = longitud geométrica del Catálogo Preliminar (EXT), con discrepancias abiertas frente al Plano Funcional. Ningún circuito es comercializable hasta validarse.", i=True)
T(["Código", "Nombre", "km", "Waypoints", "Relación con bases", "Clasif. v1 → v2", "Justificación", "Usos posibles", "Inspección / faltante", "Riesgos"],
  [(c[0], c[1], f"{c[2]:.2f}", c[5] or "—", c[7], f"{c[3]} → {CATS[c[8]]}" + (f" (alt. {CATS[c[9]]})" if c[9] else ""), c[10], c[12], c[14] + " Falta: " + c[16], c[15]) for c in CIRCUITOS],
  [1.7, 2.6, 1, 2.8, 2.2, 2.6, 4.2, 2.8, 3.8, 2.4], size=6.5)
P("Estacionalidad y potencial paisajístico de cada circuito: ver hoja 02 del libro.", i=True)

# 5 Priorización

H("4 bis. Auditoría de los 24 GPX y acceso RP13/RP12 (v2.1–2.2)")
P("Método único y reproducible (scripts/gpx_analyze.py): " + GPX_PARAMS["metodo"] + "; saltos >200 m detectados; tiempo en movimiento con velocidad ≥2 km/h; radio proxy de 3 km alrededor de las bases (NO es el límite del campo). Hash SHA-256 de cada archivo en la hoja 02b.", i=True)
doc.add_picture(os.path.join(MAPDIR, "mapa_regional.png"), width=Inches(9))
doc.add_picture(os.path.join(MAPDIR, "mapa_nucleo.png"), width=Inches(6.2))
T(["Código", "Nombre", "km", "km netos", "Fecha", "h mov.", "km/h", "% radio 3 km", "% traza única", "Mín. a I / V / C (km)", "Clasif. v2.1", "Ola"],
  [(c[0], c[1], f"{GPX[c[1]]['km']:.2f}", f"{GPX[c[1]]['km_sin_saltos_1km']:.2f}", GPX[c[1]]['t_start'][:10], GPX[c[1]]['moving_h'],
    round(GPX[c[1]]['km_sin_saltos_1km']/GPX[c[1]]['moving_h'],1) if GPX[c[1]]['moving_h'] else "", GPX[c[1]]['pct_nucleo_proxy'], GPX[c[1]]['pct_celdas_nuevas'],
    f"{GPX[c[1]]['near']['Inicio']['km']:.2f} / {GPX[c[1]]['near']['Vaquero']['km']:.2f} / {GPX[c[1]]['near']['Chivero']['km']:.2f}", CATS[c[8]], c[17]) for c in CIRCUITOS],
  [1.6, 4.2, 1.2, 1.2, 1.8, 1.0, 1.0, 1.3, 1.3, 2.8, 2.8, 2.6], size=6.5)
H("Hallazgos de la auditoría", 2)
B("Las 24 longitudes del catálogo se reproducen al centésimo con haversine: el catálogo es consistente con los archivos. 5 archivos incluyen saltos en línea recta >1 km (003, 006, 018, 021, 024): usar km netos.", "Distancias:")
B("Registros entre el 05/02/2024 (XCP) y el 01/11/2026 (XCampo Paso del Arco). Tres en junio de 2026 (019, 006, 015): hubo tránsito a comienzos del invierno. Ningún registro entre julio y septiembre: la operación invernal no tiene evidencia.", "Estacionalidad:")
B("Velocidades en movimiento de 25–46 km/h en la mayoría de los archivos indican caminos consolidados. XX Circuito campo (~17 km/h, +694 m) es el único con ritmo típico de huella 4x4. Los tiempos son de registro: no equivalen a duración comercial (sin paradas, briefing ni grupo).", "Ritmo:")
B("'Quincho' = Base Inicio (6 m); 'Puesto Vaquero' = Base Vaquero (31 m); 'Castillo' (003) = 'Grupo el Arco' (024), 1,9 km al N de Chivero (HIP: formación rocosa que podría dar nombre al lugar); 'Foto' (021) = 'Vado Aduana Vieja' (012); 'Río' (004) = Puente/Vado (013), sobre el camino de acceso desde Litrán. 'Punto límite campo' a 3,55 km al O de Inicio es la primera referencia de límite con coordenada. Laguna Pilhue (≈2,7 km al O de Inicio) queda al este de ese punto: hay que preguntar si es interna.", "Waypoints:")
B("Chivero: ningún GPX pasa a menos de 140 m; el camino a esa base no está registrado.", "Hueco de información:")
B("Coordenada del titular " + f"{ACCESO['lat']:.6f}, {ACCESO['lon']:.6f}" + ". " + ACCESO["metodo"] + " Distancias en la hoja 01_Bases.", "Acceso RP13/RP12:")
B("v2.1 había estimado el acceso junto a Chivero/Vaquero; con el dato del titular quedó desplazado ≈10 km al sur. Ese punto es otro cruce, el 'Cruce N', donde un camino desde el este se une al eje N–S.", "Corrección:")
B("La rama NE que sale del acceso hacia Inicio, el Cruce N y Vaquero sería la RP12 (INF por descarte). Si es pública en todo su recorrido, la llegada a las bases y parte de 019 y 022 corren por vía pública. Eso cambia el encuadre legal (transporte) y la seguridad (tránsito de terceros). Falta saber dónde está la tranquera de ingreso al campo sobre esa ruta (D24, R15).", "Alerta vial:")
B("No consta si las trazas son registros propios o descargas de terceros en Wikiloc (X15). No publicarlas hasta confirmarlo.", "Autoría:")

H("4 ter. Relevamiento de puntos de interés con fotos (v2.3)")
P("El titular grabó las 24 trazas y planea una traza con todos los puntos de interés y fotografías. Para que sirva al plan, se entregan un GPX base (PDA_POI_base_v1.gpx, con los 24 puntos que ya tienen coordenada), la planilla 19 del libro (para completar en el campo) y este protocolo.")
T(["Paso", "Instrucción"], PROTOCOLO, [3, 14], size=7.5)
T(["Código", "Punto", "Tipo", "Coordenada", "Origen", "Qué relevar"],
  [(p[0], p[1], p[2], "PEND" if p[3] is None else f"{p[3]:.6f}, {p[4]:.6f}", p[5], p[7]) for p in POI], [2.2, 5, 2.2, 3.6, 4.5, 6], size=7)
P("Este relevamiento resuelve, sin costo, cinco datos faltantes: los límites de referencia (D29), las lagunas norte y el mirador de las antenas (D30), si Pilhue, la Aduana Vieja y el Castillo son internos (D26), los cruces de la RP12 (D31) y el camino a Chivero. Con él se arman las fichas de producto y el material visual propio.", b=True)

H("5. Priorización de circuitos para inspección")
P("Criterios y pesos (REC, editables en hoja 03): " + "; ".join(f"{k} {d} ({int(w*100)}%)" for k, d, w in CRITERIOS) + ".")
sc = sorted(CIRCUITOS, key=lambda c: -sum(s*w for s, (_, _, w) in zip(c[18], CRITERIOS)))
T(["#", "Código", "Nombre", "km", "Puntaje", "Ola", "Por qué"],
  [(i + 1, c[0], c[1], f"{c[2]:.2f}", f"{sum(s*w for s, (_, _, w) in zip(c[18], CRITERIOS)):.2f}", c[17], c[10][:180] + ("…" if len(c[10]) > 180 else "")) for i, c in enumerate(sc)],
  [0.7, 1.8, 4.5, 1.2, 1.3, 3, 12], size=7)
H("Plan de inspección por olas (REC)", 2)
B("022 XX Circuito campo (primero: ≈20 km por huellas propias, solo 14% sobre la RP12); segmentos internos de 003 XCP (ramal oeste Chivero→Punto límite campo y bucle norte Cima–Aduana Vieja–Castillo); camino a Chivero, que ningún GPX documenta; puntos de cruce de la RP12.", "Ola 1 — campo:")
B("Hecho en v2.1: recálculo, waypoints clave, fechas y mapas. v2.2: acceso del titular incorporado. Pendiente: confirmar que la rama NE es la RP12, si es pública y dónde empieza el campo.", "Ola 1 — gabinete:")
B("013 XLeña (cruce del río y acceso desde Litrán), 004, 006 (dato de junio), 010 (¿Laguna Pilhue dentro del campo?).", "Ola 2:")
B("012, 021, 024, 008, 009, 023: gabinete legal/ambiental/titularidad; campo solo con autorizaciones.", "Ola 3:")
B("001, 002, 005, 007, 011, 014, 016, 017, 018, 020: traslados, trazas redundantes o destinos de terceros. v2.3: 019 pasa a Ola 2 (69% sobre la RP12 pública).", "Ola 4:")
P("Correcciones de v2.1 sobre v2 (los GPX las desmienten): XF1 C y XFelicinda están a 9–10 km de las bases (externos); XLeña y XBLDMR corren mayormente por caminos de acceso. Por eso salen de la Ola 1. Lectura de fondo: el inventario contiene UN solo circuito claramente local; el portafolio propio debe construirse derivando tramos internos (022 + 003), no eligiendo entre los 24 archivos.", b=True)

sec = doc.add_section(); sec.orientation = WD_ORIENT.PORTRAIT; sec.page_width, sec.page_height = sec.page_height, sec.page_width
# 6 Portafolio
H("6. Portafolio de productos y experiencias")
P("Sin tarifas ni capacidades: se fijan tras medir y cotizar (modelo, hoja 08). La ficha completa de cada producto (recursos, costos, canales, riesgos, validaciones) está en la hoja 04.", i=True)
T(["Cód.", "Producto", "Concepto", "Cliente", "Base", "Etapa", "Validación clave"],
  [(p[0], p[1], p[3], p[4], p[7], p[13], p[12]) for p in PORTAFOLIO], [1, 3, 4.5, 3.5, 1.8, 1.8, 3.4], size=7)
P("Arquitectura del portafolio (REC): una 'escalera' de producto: Bautismo (P01) → Campo + Vaquero (P02) → Jornada completa (P03) → Travesía regional (P09); con productos laterales de gastronomía (P04), familia (P05/P06), comunidad 4x4 (P07), formación (P08), privados (P10), invierno (P11) y actividades no motorizadas (P12). Cada escalón reutiliza circuitos y bases ya validados.")
P("Oportunidades no consideradas en v1: P08 Escuela de manejo 4x4 en terreno privado (posible demanda B2B de empresas con flotas en caminos no pavimentados; a validar con entrevistas) y P12 territorio multi-actividad, que reduce la dependencia del 4x4 y su riesgo reputacional.", b=True)

# 7 Modelo operativo
H("7. Modelo de negocio y modelo operativo recomendado")
T(["Alt.", "Modelo", "Ventajas", "Desventajas", "Riesgos", "Escalabilidad"], [(m[0], m[1], m[2], m[3], m[6], m[7]) for m in MODELOS], [0.8, 3, 4, 4, 3.5, 2], size=7.5)
H("Recomendación (REC): modelo D", 2)
B("Etapa 1: el campo opera como anfitrión territorial y gastronómico; la conducción de pasajeros la realizan prestadores 4x4 habilitados aliados (contrato con exclusividad por circuito, estándar de seguridad del campo y fee por salida/pax). En paralelo, convoyes con vehículos de clientes bajo guía propia o aliada.")
B("La flota propia (modelo A) solo se evalúa en Etapa 3, cuando el análisis A vs. C de la hoja 09 muestre que, con la ocupación real, el costo vehicular propio por salida es menor que el pago al aliado.")
B("Datos que faltan para decidir en forma definitiva: requisitos escritos de habilitación (D10), cotización de seguros (D13), condiciones de aliados, ocupación real del piloto, costo de vehículos (D17).")
H("Organización mínima (REC)", 2)
T(["Rol", "Etapa 0–1", "Notas"], [
    ("Dirección (titular)", "Sí", "Decisiones, contratos, gates."),
    ("Responsable de operaciones y seguridad", "Sí (puede ser externo a tiempo parcial)", "Puede detener o cancelar salidas por seguridad (Manual v1)."),
    ("Guías 4x4 habilitados", "Aliados", "Cumplir los requisitos municipales y provinciales."),
    ("Responsable de base / cocina", "Sí, por salida", "Carnet de manipulador; agua segura."),
    ("Reservas y administración", "Parcial", "WhatsApp, cobros, registro de salidas."),
    ("Datos/SIG", "Externo, por proyecto", "Auditoría GPX, mapas."),
], [5, 4, 8])

# 8 Comercial
H("8. Estrategia comercial y de marketing")
H("8.1 Investigación externa (EXTW) — separada de los antecedentes internos", 2)
T(["Actor", "Oferta", "Relación"], [(c[0], c[1], c[2]) for c in COMPETENCIA], [4.5, 8, 4.5], size=7.5)
B("No se encontraron tarifas publicadas de excursiones 4x4 en la zona: se requiere relevamiento directo (mystery shopping, D14).")
B("La demanda del destino está concentrada en el verano (pico de enero) y en el invierno (julio, nieve). Las temporadas intermedias son la debilidad estructural (INF a confirmar con el Observatorio).")
H("8.2 Posicionamiento (REC)", 2)
P("'El campo de montaña privado de Pehuenia: aventura 4x4 responsable, mesa de campo y vida rural, en grupos chicos.' Diferenciación frente a los operadores de travesías regionales: exclusividad, huellas propias controladas, hospitalidad rural y seguridad documentada. Marca 'Paso del Arco Adventure': verificar disponibilidad registral y evaluar si el topónimo, asociado a un paraje con conflicto territorial, conviene como marca principal (D20).")
H("8.3 Canales (REC, por orden de prioridad)", 2)
B("Alianzas con alojamientos (comisión o fee): mayor intención de compra en destino.", "1.")
B("Prestadores 4x4 habilitados y agencias receptivas: como operadores aliados y como canal.", "2.")
B("Venta directa por WhatsApp y web simple con calendario: mayor margen; requiere fotos y video propios.", "3.")
B("B2B: clubes 4x4, empresas (P08/P10), concesionarias.", "4.")
B("Plataformas de actividades: solo con producto estable (comisiones a relevar).", "5.")
H("8.4 Marketing digital y experiencia del cliente", 2)
B("Contenido propio (paisaje, gastronomía, seguridad); no publicar rutas, lagunas ni accesos no autorizados (regla del Dossier v1).")
B("Recorrido del cliente: consulta → ficha clara (incluye/no incluye, exigencia, clima, cancelación) → confirmación → recordatorio con qué llevar → briefing → experiencia → foto/recuerdo → pedido de reseña → oferta de recompra (P03/P11).")
B("KPIs: consultas, conversión, anticipación de reserva, ocupación por salida, ticket medio, MC por producto, NPS, reseñas, repetición, incidentes por cada 100 salidas.")

# 9 Etapas
H("9. Estructura de inversión por etapas y criterios GO/NO-GO")
T(["Etapa", "Horizonte", "Alcance", "Inversión admisible", "GO / NO-GO"], [(e[0], e[1], e[2], e[3], e[4]) for e in ETAPAS], [2.6, 2, 4, 3.4, 5], size=7.5)
P("Regla: ninguna inversión importante sin evidencia de demanda, costos y viabilidad. Los importes de cada ítem se cargan en la hoja 13 con su cotización.", b=True)

# 10 Financiero
H("10. Modelo económico-financiero")
P("El libro contiene un modelo con fórmulas listo para completar. Todos los datos de entrada están vacíos a propósito; se verificó que las fórmulas recalculen sin errores con valores de prueba (descartados).")
T(["Bloque", "Hoja", "Fórmula / lógica"], [
    ("Costo por salida", "09", "CV = impuestos + comisión + km × consumo/100 × precio combustible × vehículos + km × desgaste × vehículos + horas × tarifa (guía, apoyo, cocina) + alimentos × pax + seguro × pax + consumibles + pago a aliado"),
    ("Margen de contribución", "09", "MC = precio × pax − CV; MC% = MC / ingreso; precio mínimo por pax para MC=0"),
    ("Modelo de vehículos", "09", "Propio: depreciación (valor − residual)/km de vida × km + seguro anual / salidas; vs. pago al aliado"),
    ("Costos fijos (OPEX)", "10", "Suma mensual × 12"),
    ("Punto de equilibrio", "10", "Salidas/año = CF anual / MC ponderado por mix"),
    ("Capital de trabajo", "10", "CF mensual × meses de cobertura en temporada baja"),
    ("Escenarios", "11", "Conservador / base / favorable = factores sobre salidas, precio y CV (derivarlos del piloto)"),
    ("Flujo 12 meses", "12", "Salidas anuales × índice estacional mensual; necesidad máxima de caja = mínimo acumulado"),
    ("CAPEX y rentabilidad", "13", "CAPEX por etapa; VAN, TIR y año de recupero a 5 años"),
], [3.5, 1.2, 12.3], size=7.5)
H("Cotizaciones y mediciones necesarias", 2)
B("Mediciones de piloto: km reales, horas, consumo, pax por salida, tiempos de base.")
B("Cotizaciones: seguros (RC, AP, flota, gastronomía), radios/satelital, mejoras de bases, kit de recuperación, extintores, web, honorarios legales y de agrimensura, fee de aliados.")
B("Mercado: tarifas comparables, disposición a pagar, comisiones de canal.")
B("Macro: moneda del modelo e indexación (Argentina: inflación y tipo de cambio). REC: modelar en moneda constante y revisar las tarifas en forma periódica.")
P("Lectura de riesgo económico (INF): con productos cortos y grupos chicos, el MC por salida es sensible a las horas de personal y a la comisión de canal. El ensayo de prueba mostró cómo una comisión de 15% más 3 roles por salida pueden dejar márgenes muy bajos: hay que diseñar productos con personal polivalente y empaquetar gastronomía para elevar el ticket.")

# 11 Riesgos
H("11. Matriz de riesgos")
T(["ID", "Categoría", "Riesgo", "Prob.", "Impacto", "Mitigación", "Momento"], [(r[0], r[1], r[2], r[3], r[4], r[5], r[7]) for r in RIESGOS], [0.9, 2, 5, 1.5, 1.4, 5, 2.2], size=7)
H("Seguridad, legalidad y sostenibilidad: obligaciones a verificar", 2)
T(["Tema", "Estado", "Con quién verificar"], [
    ("Habilitación de prestador 4x4 / curso municipal obligatorio", "Informado por prensa (EXTW); requisitos exactos PEND", "Municipalidad de Villa Pehuenia"),
    ("Registro provincial de prestadores (Res. 437/2024)", "EXTW; alcance PEND", "Ministerio de Turismo de Neuquén"),
    ("Transporte de pasajeros (licencia profesional, habilitación de vehículos)", "Requisito de licencia informado para guías (EXTW); habilitación de vehículos PEND", "Autoridad provincial de transporte"),
    ("Seguros: RC, accidentes personales, flota, vehículos de clientes", "PEND", "Aseguradoras (por escrito, con descripción exacta de la actividad)"),
    ("Gastronomía: habilitación, manipuladores, agua", "PEND", "Municipio / autoridad bromatológica"),
    ("Fuego y prevención de incendios", "Prohibición informada en prensa (EXTW, dic-2025); vigencia PEND", "Manejo del Fuego provincial; COE local"),
    ("Ambiente: huellas, vados, cursos de agua, fauna", "PEND", "Autoridad ambiental provincial"),
    ("Uso del suelo y actividad comercial en área rural", "PEND", "Municipio / Catastro"),
    ("Acceso a propiedades de terceros y comunidades", "Requiere acuerdos escritos (CONF Dossier)", "Titulares / comunidades"),
    ("Laboral: guías, cocineros, ART", "PEND", "Contador / asesor laboral"),
    ("Comunicaciones y evacuación", "PEND; medir cobertura (D21)", "Operaciones; servicios de emergencia locales"),
    ("Operación invernal", "Sin circuito invernal aprobado (EXT)", "Prefactibilidad específica"),
    ("Menores y animales (Chivero)", "PEND", "Asesor legal; veterinario"),
], [6, 6, 5], size=7.5)
P("Ninguna de estas obligaciones se da por confirmada: requieren consulta profesional u oficial por escrito.", i=True)

# 12 Implementación
H("12. Plan de implementación (Etapa 0 y Etapa 1)")
T(["ID", "Etapa", "Tarea", "Responsable", "Plazo", "Entregable"], IMPLEMENTACION, [0.9, 1.3, 7.5, 3, 1.8, 2.5], size=7.5)

# 13 Datos faltantes
H("13. Registro de datos faltantes")
T(["ID", "Tema", "Dato", "Por qué importa", "Cómo obtenerlo", "Crit."], FALTANTES, [0.9, 1.8, 5, 3.3, 4.3, 1.4], size=7.5)
H("Discrepancias detectadas", 2)
T(["ID", "Tema", "Problema", "Resolución propuesta", "Estado"], [(d[0], d[1], d[2], d[4], d[5]) for d in DISCREPANCIAS], [0.9, 2.6, 6, 6, 1.5], size=7.5)

# 14 Recomendación
H("14. Recomendación ejecutiva de inversión y próximos pasos")
P("Veredicto: el proyecto tiene POTENCIAL, NO VIABILIDAD DEMOSTRADA.", b=True)
B("GO a Etapa 0 (validación), con presupuesto cotizado y tope fijado por el titular, limitado a estudios legales y de agrimensura, auditoría GPX, inspección Ola 1, consultas regulatorias, seguros y entrevistas de mercado.", "1.")
B("NO-GO, por ahora, a vehículos, obras en Vaquero o Chivero, equipamiento invernal y lodge.", "2.")
B("Gate crítico previo a cualquier otra inversión: título, mensura y situación territorial (R01/D01/D02).", "3.")
B("Modelo inicial: D (aliados habilitados + vehículos de clientes). Productos piloto: P02 Campo + Vaquero (con menú alternativo si rige la prohibición de fuego), P01 Bautismo, P07 Tag-along; validación comercial de P08.", "4.")
B("Posicionamiento: campo privado + 4x4 responsable + mesa de campo. No competir de frente en travesías regionales que ya ofrecen terceros.", "5.")
H("Decisiones que debe tomar el titular", 2)
for i, d in enumerate([
    "Aprobar la Etapa 0 y su tope de gasto.",
    "Hacer el relevamiento de puntos de interés con fotos (protocolo §4 ter) y entregar la hoja 'Geometría GPX'.",
    "Encargar estudio de títulos y mensura.",
    "Definir si operará en forma directa (requisitos de habilitación) o mediante aliados.",
    "Aportar el inventario real de infraestructura, animales y personal disponible.",
    "Fijar los umbrales de los gates (NPS, ocupación, MC mínimo, payback máximo).",
    "Fijar la tasa de descuento y el horizonte de inversión.",
    "Decidir la estrategia de marca (topónimo vs. marca propia).",
    "Autorizar contactos institucionales (Municipio, Ministerio de Turismo, comunidades vecinas).",
    "Designar al responsable de operaciones y seguridad.",
], 1):
    B(d, f"D{i}.")
H("Próximas 4 acciones (esta semana)", 2)
B("Hacer el relevamiento de puntos de interés con el GPX base y la planilla 19; en él, determinar si Laguna Pilhue, Aduana Vieja y el Castillo/Grupo el Arco están dentro del campo.")
B("Pedir al escribano/abogado el estado de dominio y al agrimensor el presupuesto de mensura.")
B("Enviar consultas escritas a la Municipalidad de Villa Pehuenia (4x4, gastronomía) y a Manejo del Fuego.")
B("Solicitar 3 cotizaciones de seguros con la descripción exacta de la actividad.")

# Fuentes
H("15. Fuentes")
for t, n, u in FUENTES:
    B(f"{n}" + (f" — {u}" if u else ""), f"[{t}]")
P("Fuentes internas no adjuntas a este análisis y citadas por el Dossier v1: Plano Funcional Maestro v1.3, Catálogo Preliminar, Modelo Operativo Comercial, Modelo Económico-Financiero v1, Plan Maestro de Implementación, Manual de Operaciones v1. Su contenido no fue verificado en v2.", i=True)

doc.save(sys.argv[2]); print("ok")
