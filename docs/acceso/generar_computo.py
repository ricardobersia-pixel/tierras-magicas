"""Planilla de cómputo y presupuesto comparativo del acceso (sin precios: se cargan de cotizaciones)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

wb = Workbook()
H = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1F3326")
IN = PatternFill("solid", fgColor="FFF2CC"); NOTE = Font(italic=True, color="666666")

def cab(ws, fila, cols):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(fila, i, c); cell.font = H; cell.fill = HF
        cell.alignment = Alignment(wrap_text=True, vertical="center")

# ---------- 1. Datos a relevar ----------
d = wb.active; d.title = "1_Relevamiento"
d["A1"] = "DATOS A MEDIR EN OBRA (celdas amarillas). Los valores cargados son SUPUESTOS de cálculo y deben reemplazarse."
d["A1"].font = Font(bold=True)
cab(d, 3, ["Código", "Dato", "Valor", "Unidad", "Estado", "Cómo medir"])
datos = [
    ("FR", "Frente sobre RP 11 (plano municipal, lámina 1/3)", 59.54, "m", "DATO PLANO", "Cota del plano de relevamiento"),
    ("AN", "Portal: luz 3,80 m + 2 pilares de 0,45 m (retirado 1,50 m hacia adentro)", 4.7, "m", "DATO DUEÑO (croquis)", ""),
    ("AT", "Ingreso vehicular: tranquera 5,50 m + pilar de medidores 1,00 m (100×45×150)", 6.5, "m", "DATO DUEÑO", ""),
    ("L1", "Cerca nueva = NT × (6 − AM) + 2 × LW", "=C8*(6-C19)+2*C9", "m", "CALCULADO", "NT, LW y AM más abajo"),
    ("NT", "Tramos de 6 m entre mojones (4 + 2 + 1 según croquis)", 7, "u", "DATO DUEÑO (croquis)", ""),
    ("LW", "Ala diagonal de cada lado del portal (mojón → pilar)", 2.0, "m", "DATO DUEÑO (croquis)", "Confirmar si 2 m es la diagonal o la distancia sobre la línea"),
    ("L2", "Otros tramos de cerca (laterales, si se suman)", 0, "m", "A DEFINIR", ""),
    ("L3", "Cerco de soga del camino interno", 50, "m", "DATO DUEÑO (aprox.)", ""),
    ("LS", "Sendero peatonal portal → cabañas", 30, "m", "SUPUESTO", "Medir el recorrido elegido"),
    ("AB", "Superficie de banquina a usar como estacionamiento", 0, "m²", "A DEFINIR", "Depende del perfil de Vialidad"),
    ("NP", "Pilares del portal", 2, "u", "CONTEO FOTOS", "Verificar"),
    ("NM", "Mojones", 9, "u", "DATO DUEÑO (croquis)", ""),
    ("HP", "Altura de pilar del portal", 3.4, "m", "DATO DUEÑO", ""),
    ("AP", "Lado de pilar del portal", 0.45, "m", "DATO DUEÑO", ""),
    ("HM", "Altura de mojón", 1.5, "m", "DATO DUEÑO", ""),
    ("AM", "Lado de mojón", 0.45, "m", "DATO DUEÑO", ""),
    ("HZ", "Altura de zócalo de piedra (alt. 2)", 0.6, "m", "CRITERIO DE PROYECTO", "Ajustar a la altura de salpicado y nieve"),
    ("SP", "Postes por tramo de 6 m (2 extremos + 1 central ≈ 2,7 m)", 3, "u", "CRITERIO DE PROYECTO", ""),
    ("FP", "Faja de plantación del lado de ADENTRO de la cerca (ancho)", 0.8, "m", "CRITERIO DE PROYECTO", "La banquina queda libre: estacionamiento invernal"),
    ("DP", "Densidad de plantas", 3, "u/m²", "CRITERIO DE PROYECTO", "Ajustar con el vivero"),
]
for i, r in enumerate(datos, 4):
    for j, v in enumerate(r, 1):
        c = d.cell(i, j, v)
    d.cell(i, 3).fill = IN
nombres = {r[0]: f"'1_Relevamiento'!$C${i}" for i, r in enumerate(datos, 4)}
for col, w in zip("ABCDEF", (8, 52, 10, 8, 24, 40)):
    d.column_dimensions[col].width = w

# ---------- 2. Cómputo ----------
c = wb.create_sheet("2_Computo")
cab(c, 1, ["Rubro", "Ítem", "Unidad", "Fórmula / criterio", "A1 Económica", "A2 Patagónico natural", "A3 Premium", "Origen"])
N = nombres
L = f"({N['L1']}+{N['L2']})"
area_pil = f"(4*{N['AP']}*{N['HP']}*{N['NP']})"
area_moj = f"(4*{N['AM']}*{N['HM']}*{N['NM']})"
items = [
    ("Pilares y mojones", "Picado de partes flojas y reparación con mortero", "m²", "10% de la superficie (estimado)", f"=0.1*({area_pil}+{area_moj})", f"=0.1*({area_pil}+{area_moj})", f"=0.1*{area_moj}", "REUTILIZADO: trabajo de recuperación"),
    ("Pilares y mojones", "Pintura mineral/silicato gris piedra (2 manos)", "m²", "caras de pilares y mojones", f"={area_pil}+{area_moj}", f"=4*{N['AP']}*({N['HP']}-{N['HZ']})*{N['NP']}+{area_moj}", f"={area_moj}", "NUEVO"),
    ("Pilares y mojones", "Revestimiento de piedra local (zócalo o completo)", "m²", "A2: zócalo HZ; A3: pilares completos + medidores", "=0", f"=4*{N['AP']}*{N['HZ']}*{N['NP']}+2*(1+0.45)*{N['HZ']}", f"={area_pil}+4*0.5*1.2", "NUEVO / piedra del predio si hay"),
    ("Pilares y mojones", "Remate inclinado (botaguas) en pilares", "u", "solo si la punta está dañada", "=0", "=0", f"={N['NP']}", "NUEVO"),
    ("Portal", "Retiro de la viga existente (podrida)", "u", "", 1, 1, 1, "Mano de obra propia"),
    ("Portal", "Viga nueva rollizo Ø25-30 cm × 6,0 m (luz 3,80 + pilares 0,90 + 0,65 m de vuelo por lado)", "u", "", 1, 1, 1, "NUEVO"),
    ("Portal", "Anclaje de viga a pilares: varilla roscada galvanizada + resina química", "jgo", "2 apoyos", 1, 1, 1, "NUEVO"),
    ("Portal", "Ménsulas metálicas negras bajo la viga", "u", "solo A3", 0, 0, 2, "NUEVO"),
    ("Portones", "Restauración tranquera vehicular (lijado, herrajes, impregnante)", "hoja", "2 hojas", 2, 2, 2, "REUTILIZADO"),
    ("Portones", "Restauración portón peatonal (hoja chica reparada)", "hoja", "2 hojas", 2, 2, 0, "REUTILIZADO"),
    ("Portones", "Portón peatonal nuevo bastidor metálico + madera", "u", "solo A3", 0, 0, 1, "NUEVO"),
    ("Cerca", "Retensado del alambrado (A1) o retiro y reuso de varillas en otro sector (A2/A3, si no hay animales)", "m", "L1+L2", f"={L}", f"={L}", f"={L}", "REUTILIZADO"),
    ("Cerca", "Postes escuadrados 5\"×5\" × 1,85 m (1,15 libre + 0,70 empotrado), punta de diamante", "u", "SP × NT + 4 en las alas", "=0", f"={N['SP']}*{N['NT']}+4", f"={N['SP']}*{N['NT']}+4", "NUEVO"),
    ("Cerca", "Travesaños 2\"×5\" × 5,49 m (18'), una pieza por línea y tramo", "u", "3 × NT", "=0", f"=3*{N['NT']}", f"=3*{N['NT']}", "NUEVO"),
    ("Cerca", "Travesaños 2\"×5\" × 4,88 m para las alas (2 piezas de 2 m c/u)", "u", "3 líneas × 2 alas / 2", "=0", 3, 3, "NUEVO"),
    ("Cerca", "Cajas escopleadas en postes (3 por poste)", "u", "", "=0", f"=3*({N['SP']}*{N['NT']}+4)", f"=3*({N['SP']}*{N['NT']}+4)", "Mano de obra (carpintero o propia con escopladora)"),
    ("Cerca", "Impregnante para madera, superficie a cubrir", "m²", "postes + 3 travesaños, 2 caras visibles", "=0", f"=({N['SP']}*{N['NT']}+4)*4*0.127*1.3+3*{L}*2*(0.127+0.05)", f"=({N['SP']}*{N['NT']}+4)*4*0.127*1.3+3*{L}*2*(0.127+0.05)", "NUEVO"),
    ("Cerca", "Tarugos de madera dura o tirafondos galvanizados (1 por cruce)", "u", "", "=0", f"=3*({N['SP']}*{N['NT']}+4)", f"=3*({N['SP']}*{N['NT']}+4)", "NUEVO"),
    ("Cerca", "Cerco de soga del camino interno: reemplazo por travesaño único", "m", "L3", "=0", f"={N['L3']}", f"={N['L3']}", "NUEVO; postes existentes se reusan"),
    ("Cerca", "Pirca baja de piedra seca a los lados del ingreso", "m", "2 tramos de 3 m (criterio)", "=0", "=0", 6, "NUEVO"),
    ("Señalética", "Placa metálica en pilar", "u", "", 1, 0, 0, "NUEVO"),
    ("Señalética", "Tabla tallada colgante con botaguas", "u", "", 0, 1, 0, "NUEVO"),
    ("Señalética", "Panel con el logo existente, marco y botaguas", "u", "", 0, 0, 1, "NUEVO (diseño ya hecho)"),
    ("Señalética", "Placa 'Ingreso / Recepción' en tranquera vehicular", "u", "", 1, 1, 1, "NUEVO"),
    ("Iluminación solar", "Proyector solar con panel separado sobre la viga, hacia el cartel (2700-3000 K)", "u", "", 0, 2, 2, "NUEVO"),
    ("Iluminación solar", "Aplique solar en pilar del portal, luz hacia abajo, panel separado", "u", "", 0, 2, 2, "NUEVO"),
    ("Iluminación solar", "Placa 'Ingreso' iluminada por la luminaria pública existente", "—", "sin equipo", 0, 0, 0, "EXISTENTE"),
    ("Iluminación solar", "Balizas solares bajas en el sendero peatonal (cada ≈ 4 m)", "u", "LS / 4", 0, f"=ROUNDUP({N['LS']}/4,0)", f"=ROUNDUP({N['LS']}/4,0)", "NUEVO"),
    ("Iluminación solar", "Reemplazo de luces solares existentes de luz fría por 2700-3000 K", "u", "relevar cuántas hay", 0, 4, 6, "SUPUESTO"),
    ("Paisajismo", "Faja de plantación", "m²", "L × FP", f"=0.3*{L}*{N['FP']}", f"={L}*{N['FP']}", f"={L}*{N['FP']}*1.5", "—"),
    ("Paisajismo", "Plantas nativas (mezcla, envase 1-3 L)", "u", "m² × DP", f"=ROUND(0.3*{L}*{N['FP']}*{N['DP']},0)", f"=ROUND({L}*{N['FP']}*{N['DP']},0)", f"=ROUND({L}*{N['FP']}*1.5*{N['DP']},0)", "NUEVO"),
    ("Paisajismo", "Pantalla vegetal entre tina y ruta: arbustos nativos 1,2-1,8 m (calafate, michay, palo piche)", "u", "≈ 12 m de pantalla, 1 cada 1 m (SUPUESTO)", 0, 12, 12, "NUEVO"),
    ("Paisajismo", "Cobertura de chip de corteza o grava local 5 cm", "m³", "m² × 0,05", f"=0.05*0.3*{L}*{N['FP']}", f"=0.05*{L}*{N['FP']}", f"=0.05*{L}*{N['FP']}*1.5", "NUEVO / del predio"),
    ("Paisajismo", "Extensión del riego por goteo existente", "m", "", f"=0.3*{L}", f"={L}", f"={L}*1.5", "REUTILIZADO + ampliación"),
    ("Banquina", "Relleno y nivelación de banquina con ripio, pendiente hacia la cuneta (con permiso de Vialidad)", "m²", "AB", 0, f"={N['AB']}", f"={N['AB']}", "A DEFINIR"),
    ("Sendero", "Sendero peatonal portal → cabañas, 1,2 m de ancho: excavación 10 cm + ripio/grava", "m²", "LS × 1,2", 0, f"={N['LS']}*1.2", f"={N['LS']}*1.2", "NUEVO"),
    ("Sendero", "Borde de rollizo o durmiente a ambos lados", "m", "2 × LS", 0, f"=2*{N['LS']}", f"=2*{N['LS']}", "NUEVO / rollizos sueltos del predio"),
    ("Sendero", "Escalones de durmiente donde la pendiente supere ≈ 10 %", "u", "a definir en obra", 0, 6, 6, "SUPUESTO"),
    ("Limpieza", "Retiro de ladrillos, ramas, piezas sueltas; perfilado de borde", "gl", "", 1, 1, 1, "Mano de obra propia"),
]
for i, it in enumerate(items, 2):
    for j, v in enumerate(it, 1):
        c.cell(i, j, v)
for col, w in zip("ABCDEFGH", (18, 58, 7, 36, 14, 18, 14, 34)):
    c.column_dimensions[col].width = w
fin_items = 1 + len(items)

# ---------- 3. Presupuesto ----------
p = wb.create_sheet("3_Presupuesto")
p["A1"] = "Cargar el precio unitario de la MEJOR de 3 cotizaciones por ítem (columna D). Sin precios no hay total: no se inventan valores."
p["A1"].font = Font(bold=True)
cab(p, 3, ["Rubro", "Ítem", "Unidad", "Precio unitario (ARS)", "Proveedor / fecha", "Subtotal A1", "Subtotal A2", "Subtotal A3"])
for k in range(len(items)):
    r = 4 + k; s = 2 + k
    p.cell(r, 1, f"='2_Computo'!A{s}"); p.cell(r, 2, f"='2_Computo'!B{s}"); p.cell(r, 3, f"='2_Computo'!C{s}")
    p.cell(r, 4).fill = IN; p.cell(r, 5).fill = IN
    for j, col in enumerate("EFG"):
        p.cell(r, 6 + j, f"=IF(D{r}=\"\",\"\",D{r}*'2_Computo'!{col}{s})")
fin = 3 + len(items)
p.cell(fin + 1, 2, "MATERIALES (suma)").font = Font(bold=True)
for j, col in enumerate("FGH"):
    p.cell(fin + 1, 6 + j, f"=SUM({col}4:{col}{fin})")
extra = [("Mano de obra propia (jornales × valor jornal)", 8, 20, 30),
         ("Mano de obra contratada: albañil/pircador", 0, 6, 15),
         ("Electricista matriculado (jornales, solo plan B a 12 V)", 0, 0, 0),
         ("Herramientas, alquileres, fletes (% de materiales)", None, None, None),
         ("Imprevistos 10 % (% de materiales + MO)", None, None, None)]
p.cell(fin + 3, 1, "JORNALES ESTIMADOS (SUPUESTO de anteproyecto, corregir con quien ejecute)").font = Font(bold=True)
p.cell(fin + 4, 2, "Valor jornal propio (ARS)"); p.cell(fin + 4, 4).fill = IN
p.cell(fin + 5, 2, "Valor jornal albañil/pircador (ARS)"); p.cell(fin + 5, 4).fill = IN
p.cell(fin + 6, 2, "Valor jornal electricista (ARS)"); p.cell(fin + 6, 4).fill = IN
p.cell(fin + 7, 2, "% herramientas y fletes"); p.cell(fin + 7, 4, 0.08); p.cell(fin + 7, 4).fill = IN
base = fin + 9
cab(p, base, ["", "Concepto", "", "", "", "A1", "A2", "A3"])
for i, (txt, a1, a2, a3) in enumerate(extra[:3]):
    r = base + 1 + i; p.cell(r, 2, txt)
    for j, v in enumerate((a1, a2, a3)):
        p.cell(r, 6 + j, f"={v}*$D${fin + 4 + i}")
r = base + 4; p.cell(r, 2, extra[3][0])
for j, col in enumerate("FGH"):
    p.cell(r, 6 + j, f"={col}{fin + 1}*$D${fin + 7}")
r = base + 5; p.cell(r, 2, extra[4][0])
for j, col in enumerate("FGH"):
    p.cell(r, 6 + j, f"=0.1*({col}{fin + 1}+SUM({col}{base + 1}:{col}{base + 3}))")
r = base + 6; p.cell(r, 2, "TOTAL ESTIMADO").font = Font(bold=True)
for j, col in enumerate("FGH"):
    p.cell(r, 6 + j, f"={col}{fin + 1}+SUM({col}{base + 1}:{col}{base + 5})").font = Font(bold=True)
p.cell(r + 2, 2, "Jornales: 6-10 (A1), 15-25 (A2), 30-50 (A3) en total; repartidos arriba como hipótesis.").font = NOTE
for col, w in zip("ABCDEFGH", (18, 58, 7, 18, 24, 16, 16, 16)):
    p.column_dimensions[col].width = w

# ---------- 4. Quién hace qué ----------
q = wb.create_sheet("4_Quien_ejecuta")
cab(q, 1, ["Trabajo", "Mano de obra propia", "Requiere profesional", "Por qué"])
filas = [
    ("Limpieza, retiro de ladrillos y ramas", "Sí", "No", ""),
    ("Lijado e impregnante de portones", "Sí", "No", ""),
    ("Picado y pintura de pilares y mojones", "Sí", "No", "Usar EPP; probar la pintura en un mojón antes"),
    ("Retensado de alambrado", "Sí", "No", ""),
    ("Postes y travesaños de la cerca", "Sí (con ayudante)", "No", "Hormigonar o apisonar postes; verificar profundidad"),
    ("Plantación y riego por goteo", "Sí", "Consulta a vivero de nativas", "Elección de especies según microclima"),
    ("Zócalo de piedra / pircas", "No recomendado", "Albañil o pircador", "Terminación visible: la calidad define el resultado"),
    ("Anclaje de viga y colgado del cartel", "No", "Verificación de un profesional (arquitecto/ingeniero)", "Carga de viento y nieve sobre el cartel"),
    ("Luces solares y balizas del sendero", "Sí", "No", "Panel sin sombra, inclinado 55-60°, batería apta para frío"),
    ("Instalación eléctrica (solo si el cartel pasa a 12 V)", "No", "Electricista matriculado", "Seguridad y normativa"),
    ("Sendero peatonal", "Sí", "No", "Escalones donde la pendiente lo pida"),
    ("Cualquier trabajo sobre el pilar de medidores", "No", "Consulta previa a la distribuidora eléctrica", "No obstruir lectura ni acceso a medidores"),
]
for i, f in enumerate(filas, 2):
    for j, v in enumerate(f, 1):
        q.cell(i, j, v)
for col, w in zip("ABCD", (46, 20, 42, 52)):
    q.column_dimensions[col].width = w

wb.save("computo_presupuesto_acceso.xlsx")
print("ok")
