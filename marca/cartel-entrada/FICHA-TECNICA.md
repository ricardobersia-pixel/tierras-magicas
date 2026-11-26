# Cartel de entrada — Tierras Mágicas
Ficha técnica para el rotulador o carpintero.

## Medidas
| | |
|---|---|
| Placa | **1200 × 1250 mm**, esquinas redondeadas R30 mm. Sale de una placa estándar de 1220 × 2440 mm. |
| Logo | 1100 mm de ancho × 1144 mm de alto, centrado. Márgenes de 50 mm a los costados y 53 mm arriba y abajo. |
| Altura de la "T" de *Tierras* | 121 mm. Se lee a unos 40 m (regla práctica de 1 cm de letra por cada 3 a 4 m). |
| Trazo más fino | Unos 2 mm en algunos detalles (vapor, humo, hierba). La mayoría de los trazos supera los 3,5 mm. |

## Materiales
- **Placa:** fenólico marino de 18 mm (o multilaminado de exterior), con los cantos sellados. Lijado liso, con 2 o 3 manos de esmalte poliuretánico verde `#203224` (lo más cercano: verde inglés o verde bosque oscuro, mate o semimate). La veta debe quedar **sellada y lisa** para que el vinilo pegue.
- **Vinilo:** corte en **vinilo dorado metalizado de grado exterior** ("cast" o polimérico de larga duración). Pedir que la ficha del fabricante garantice al menos 5 años de uso exterior.
- **Opcional:** laminado transparente UV sobre el vinilo, o barniz compatible aplicado por el rotulador.

## Archivos
- `cartel-120x125-corte-vinilo.svg` / `.pdf` — escala 1:1 en mm. Capa **vinilo-dorado** en negro: es lo que corta la máquina. Capa **contorno-placa** en magenta: solo es una guía, **no se corta en vinilo**. El carpintero puede usarla para el corte de la placa.
- `cartel-120x125-referencia-color.pdf` — referencia de colores del resultado final.
- `maqueta-cartel.png` — maqueta ilustrativa (no es un archivo de producción).

## Antes de producir
1. Hacer una **prueba de corte** de un sector con los detalles más finos (vapor del hot tub y humo de la chimenea) y verificar que se puedan despegar y transferir sin romperse.
2. Aplicar el vinilo con la placa seca y a más de 10 °C. No instalar con helada.
3. Pedir la ficha técnica del vinilo y del esmalte, con la duración garantizada para exterior.

---

# Estructura rústica de troncos (versión elegida)
Estilo del cartel de referencia: dos postes de tronco barnizados, un panel de madera con el borde superior recortado en forma de montaña y la placa del logo atornillada al frente. Ver `maqueta-cartel-troncos.png` y `plano-estructura-troncos.pdf`.

| Elemento | Especificación |
|---|---|
| Postes | 2 troncos de Ø 22–25 cm (ciprés o pino impregnado), descortezados y lijados. 272 cm sobre el suelo + 70–80 cm enterrados en dado de hormigón. Base protegida con brea o asfalto hasta 10 cm sobre el suelo. |
| Panel | 160 × 155 cm + recorte superior de montaña (picos de hasta +30 cm, 185 cm de alto total). Tablas machihembradas de 2" o fenólico de 25 mm revestido. Borde inferior a 80 cm del suelo, por la nieve. Ranura (fresado) perimetral decorativa opcional. |
| Unión panel–postes | Panel encastrado **5 cm** en un rebaje de cada poste, con 4 bulones galvanizados **M10** pasantes (perforación Ø12 a 25 mm del borde, marcada en el archivo CNC). |
| Placa del logo | 120 × 125 cm, fenólico de 18 mm pintado en verde `#203224` con el vinilo dorado (archivo `cartel-120x125-corte-vinilo.pdf`). Fijación al panel con 8 tornillos de acero inoxidable, con arandela y separadores de 5 mm para que ventile y escurra el agua. |
| Terminación de la madera | Protector exterior con filtro UV (tipo impregnante o barniz marino), 3 manos. Repasar cada 1 o 2 años. |
| Ancho total | ≈ 198 cm |

**Por qué la placa va aparte y no el vinilo pegado sobre las tablas:** el vinilo no pega bien sobre la veta ni sobre las juntas del machihembre, y se despega con el hielo. Sobre una placa lisa y sellada dura mucho más. Además, si algún día se daña, se cambia solo la placa y no todo el cartel.

## Archivo CNC del panel (`cnc/`)
- `panel-picos-cnc.dxf` — **archivo para el router CNC** (VCarve, Aspire, Fusion u otro). Unidades en mm, escala 1:1, origen en la esquina inferior izquierda.
- `panel-picos-cnc.svg` — la misma geometría en SVG (mm).
- `panel-picos-plantilla-1a1.pdf` — plantilla en **tamaño real** (1640 × 1881 mm) para imprimir en plotter y cortar a mano con caladora, si no hay CNC.

| Capa | Color | Operación sugerida |
|---|---|---|
| `CORTE_EXTERIOR` | rojo | Corte pasante por fuera de la línea, fresa recta de 6 a 8 mm |
| `RANURA_V_DECORATIVA` | azul | Grabado en V de 90°, 5 a 6 mm de profundidad, a 60 mm del borde |
| `GUIA_PLACA_NO_CORTAR` | gris | Solo es una referencia de dónde va la placa del logo. **No mecanizar.** |
| `PERFORACION_PLACA_D4` | verde | 8 agujeros guía de Ø4 para los tornillos de la placa |
| `PERFORACION_BULON_D12` | magenta | 4 agujeros pasantes de Ø12 para los bulones M10 a los postes |

**Geometría:** panel de 1600 mm de ancho y 1841 mm de alto en el pico mayor. Las puntas de los picos tienen un redondeo de R25 mm y los valles de R12 mm, para que la madera no se astille en las puntas y la fresa pueda entrar en los valles. Las esquinas inferiores quedan a 90° para encastrar en los postes.

**Ojo con el tamaño de la mesa:** el panel (1,60 × 1,84 m) **no entra** en una placa estándar de 1,22 × 2,44 m ni en una mesa CNC de 1,25 m de ancho. Hay dos opciones:
1. Armar primero el panel de tablas machihembradas, encolado y con travesaños atrás, y pasarlo entero por una CNC de mesa grande (1,6 m de ancho o más).
2. Si la CNC es chica, cortar solo el **remate superior** (la franja de los picos) y terminar el resto con escuadra. También se puede imprimir la plantilla 1:1 y cortar con caladora.
