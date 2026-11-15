# -*- coding: utf-8 -*-
import sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
sys.path.insert(0, sys.argv[1])
from data import *

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
p = doc.add_paragraph(); r = p.add_run("Plan de Negocios v2 — Análisis integral, portafolio, modelo operativo y estructura económico-financiera"); r.font.size = Pt(14)
P("Versión 2.0 · 15/11/2026 · Documento de trabajo para decisión del titular. Base documental: Dossier IA v1 y Anexo Maestro de Bases y 24 Circuitos v1, más investigación externa citada. No es un estudio de factibilidad ni habilita la operación.", i=True)
P("Complemento obligatorio: libro 'Matrices_y_Modelo_Financiero_Paso_del_Arco_v2.xlsx' (matrices completas, priorización con puntajes editables y modelo financiero con fórmulas).", i=True)

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
B("Inventario de 24 tracks GPX (1.318 km de longitud geométrica sumada) y waypoints con nombres de atractivos (EXT).")
B("Destino con demanda turística probada a nivel destino: 95% de ocupación en fin de año 2025-26 y 89% en una semana de julio 2026, +21 puntos interanuales en invierno (EXTW, prensa regional citando al Ministerio de Turismo). Un resumen de búsqueda atribuye al Observatorio de Turismo de Neuquén 99.753 turistas y 71% de ocupación en plazas en la temporada estival 2024-25: dato a verificar en la fuente oficial.")
B("Borradores de manual operativo (PA-OPS-MAN-001), modelo operativo-comercial, modelo financiero y plan de implementación (EXT; no adjuntos a este análisis).")
H("1.2 Lo que el proyecto no tiene todavía", 2)
B("Acreditación de superficie, límites y título; ningún circuito medido, inspeccionado ni habilitado; ninguna tarifa, costo, capacidad ni demanda propia; ninguna habilitación ni seguro verificado (EXT, Dossier v1 §14–15).")
H("1.3 Hallazgos críticos de este análisis (nuevos respecto de v1)", 2)
B("Las tres bases están a 1,3–2,7 km entre sí (triángulo de ≈155 ha). Un campo de 2.000 ha equivale a un cuadrado de ≈4,5 km de lado. Por lo tanto, los tracks de 70–150 km clasificados como 'candidato núcleo' no pueden ser internos: son regionales o contienen tramos externos. El producto realmente propio será corto/medio día; las travesías largas dependen en gran medida de terceros.", "Escala (INF, cálculo propio).")
B("Lo defendible no son las rutas (muchas son caminos regionales que ya recorren otros operadores, EXTW) sino el acceso exclusivo a un campo privado de montaña + bases + hospitalidad rural. El plan se reorienta a ese activo.", "El activo real (INF).")
B("Existen reclamos y conflictos territoriales de comunidades mapuche documentados en la zona, incluido uno situado en el paraje Paso del Arco (EXTW). No se sabe si afectan al campo. Es el primer gate: sin título y límites claros no se invierte.", "Contexto territorial (EXTW).")
B("La prensa informa que el Decreto 198/2025 (emergencia ígnea) prohibía hacer fuego en todo Neuquén (EXTW, dic-2025). El asado a la estaca, núcleo de la propuesta de Vaquero, puede no ser operable en verano. Se requiere verificar vigencia y excepciones y diseñar un menú sin fuego abierto.", "Fuego vs. asado (EXTW).")
B("Villa Pehuenia implementó en 2025 una capacitación obligatoria para prestadores de excursiones 4x4, con requisitos informados de residencia en Neuquén ≥2 años, edad >21 y licencia para conducir 4x4 y transporte de pasajeros; la provincia tiene un registro de prestadores (Res. 437/2024) (EXTW). Esto condiciona quién puede guiar y favorece aliarse con prestadores ya habilitados.", "Regulación 4x4 (EXTW).")
B("En 2026 hubo denuncias por ingreso ilegal de 4x4 a áreas protegidas y una investigación por maniobras sobre una laguna congelada en Batea Mahuida (EXTW). Riesgo reputacional para el rubro, y a la vez oportunidad: posicionarse como '4x4 responsable en campo privado'.", "Licencia social (EXTW).")
H("1.4 Calidad de datos", 2)
P("Se identificaron 10 discrepancias (hoja 15 del libro). Las más relevantes: km del catálogo vs. Plano Funcional (abierta desde v1); 53 waypoints declarados vs. 47 listados en el anexo; tracks de 70–150 km clasificados como núcleo; derivado recortado de Litrán no generado; XF1 C (el más corto) omitido de la priorización v1.")

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
B("Inicio es la base más cercana a la intersección RP13/RP23 de Litrán (≈5,2 km): candidata natural a recepción y control (INF).")
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
H("5. Priorización de circuitos para inspección")
P("Criterios y pesos (REC, editables en hoja 03): " + "; ".join(f"{k} {d} ({int(w*100)}%)" for k, d, w in CRITERIOS) + ".")
sc = sorted(CIRCUITOS, key=lambda c: -sum(s*w for s, (_, _, w) in zip(c[18], CRITERIOS)))
T(["#", "Código", "Nombre", "km", "Puntaje", "Ola", "Por qué"],
  [(i + 1, c[0], c[1], f"{c[2]:.2f}", f"{sum(s*w for s, (_, _, w) in zip(c[18], CRITERIOS)):.2f}", c[17], c[10][:180] + ("…" if len(c[10]) > 180 else "")) for i, c in enumerate(sc)],
  [0.7, 1.8, 4.5, 1.2, 1.3, 3, 12], size=7)
H("Plan de inspección por olas (REC)", 2)
B("022 XX Circuito campo (primero), 013 XLeña, 019 XVilla Unión Corto, 002 XBLDMR, 006 XDomingo Junio, 007 XF1 C. Objetivo: obtener 2–3 circuitos internos aptos para el piloto.", "Ola 1 — campo:")
B("003 XCP y 024 XXMoquehue–L. Vallejos–V. Unión: no por su producto, sino porque sus waypoints ('Punto límite campo', 'Quincho', 'Puesto Vaquero', 'Entrada campo mecánico', 'Grupo el Arco') resuelven límites, bases y conexiones. Además, leer timestamps de todos los GPX (estacionalidad).", "Ola 1 — gabinete:")
B("004, 008, segmentos internos de 003; derivar circuitos de jornada completa.", "Ola 2:")
B("012, 023, 010, 017, 009, 021, 005: primero gabinete legal/ambiental/titularidad; campo solo con autorizaciones.", "Ola 3:")
B("001, 011, 014, 015, 016, 018, 020: traslados, internacionales o destinos de terceros; sin inspección propia en el corto plazo.", "Ola 4:")
P("Diferencia con v1: se incorpora XF1 C (8,21 km) y se baja XLaguna El Arco–Vallejos de 'Alta' a gabinete prioritario + campo en Ola 3, porque depende de terceros, compite con oferta existente y tiene exposición ambiental.")

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
    "Entregar los 24 GPX originales y la hoja 'Geometría GPX' del Plano Funcional.",
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
B("Subir los GPX originales para el recálculo con método único y la extracción de waypoints clave.")
B("Pedir al escribano/abogado el estado de dominio y al agrimensor el presupuesto de mensura.")
B("Enviar consultas escritas a la Municipalidad de Villa Pehuenia (4x4, gastronomía) y a Manejo del Fuego.")
B("Solicitar 3 cotizaciones de seguros con la descripción exacta de la actividad.")

# Fuentes
H("15. Fuentes")
for t, n, u in FUENTES:
    B(f"{n}" + (f" — {u}" if u else ""), f"[{t}]")
P("Fuentes internas no adjuntas a este análisis y citadas por el Dossier v1: Plano Funcional Maestro v1.3, Catálogo Preliminar, Modelo Operativo Comercial, Modelo Económico-Financiero v1, Plan Maestro de Implementación, Manual de Operaciones v1. Su contenido no fue verificado en v2.", i=True)

doc.save(sys.argv[2]); print("ok")
