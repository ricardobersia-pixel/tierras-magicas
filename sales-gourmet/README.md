# Sales de la Cordillera (app para huéspedes)

Recetario de las Sales Gourmet Tierras Mágicas, que se regalan a los huéspedes en **sobres doypack de 25 g**, sin fecha ni plazo de consumo. La producción es artesanal y **las sales no se venden**. La app es instalable en el navegador (PWA) y también como APK de Android. Funciona sin señal.

**La app no contiene fórmulas ni proporciones.** La producción está en otra app, [TM Sales](../taller-sales/README.md). El repositorio es público: no agregar acá porcentajes, gramos por kilo ni granulometrías. Un test lo controla.

| Qué | Dónde |
|---|---|
| App web | https://ricardobersia-pixel.github.io/tierras-magicas/sales/ (con GitHub Pages activado) |
| Enlace para QR | `…/sales/?sal=TM-01` abre la ficha de esa sal |
| APK de Android | Releases → `sales-gourmet-v1.0.N` → `SalesTM.apk` |
| Sales, recetas y guía | `www/js/datos.js` |
| Fotos de las recetas | `www/img/recetas/` (ver abajo) |
| Etiquetas corregidas | `etiquetas/` |

## Qué tiene

- **Sales:** cada variedad con su etiqueta, para qué sirve y qué contiene. Los ingredientes van en orden alfabético y sin cantidades, para informar a quien tenga alergias sin revelar la fórmula.
- **Recetas:** 20 recetas, 5 por sal, con buscador y filtro. Cada una tiene porciones, tiempo, ingredientes con cantidades, pasos, consejo y aviso de seguridad cuando corresponde.
- **Guía de uso:** la del libro de cocina, más una nota sobre el consumo de sal.

## Recetas revisadas

Se ajustaron a lo que dice cada etiqueta ("Ideal para…"). El libro original tenía superposiciones: por ejemplo, salmón en Bosque Andino, cuando el pescado es de Lago & Trucha.

| Sal | Recetas |
|---|---|
| Caza Patagónica | Bife de chorizo al fogón · Ciervo asado con papas rústicas · Estofado de jabalí con hongos de pino · Hongos de pino salteados · Papas crocantes al horno con romero |
| Bosque Andino | Risotto de hongos · Huevos de campo revueltos con ciboulette · Ñoquis con manteca de hierbas · Vegetales de estación asados · Focaccia de hierbas |
| Lago & Trucha | Trucha a la parrilla con manteca cítrica · Ceviche de trucha · Pechuga de pollo grillada al limón · Langostinos patagónicos a la plancha · Vegetales a la parrilla con eneldo |
| Reserva del Fogón | Asado de tira a la parrilla · Cordero patagónico a la cruz · Bondiola de cerdo al horno · Vegetales al rescoldo · Papas al rescoldo con manteca y queso |

Los avisos de seguridad siguen las temperaturas internas del USDA FSIS. Para el pescado crudo, se sigue el congelado previo que indica la FDA (−20 °C durante 7 días).

**Conviene validar en la cocina:** las cantidades de sal y los tiempos. Son razonables, pero no se probaron con estas sales.

## Ilustraciones de las recetas

Cada receta tiene una ilustración vectorial propia (`www/img/recetas/<id>.svg`, 800 × 600):

- **Estilo:** gráfico uniforme, con textura de acuarela y el color de la sal de fondo.
- **Origen:** dibujadas en código con `ilustraciones/generar.py`. No son fotos ni salen de IA generativa.
- **Peso:** de 6 a 40 KB cada una, y funcionan sin conexión.

Para ajustar un plato, editá su composición en `generar.py` (funciones `r_<plato>`) y regenerá:

```bash
python3 sales-gourmet/ilustraciones/generar.py
```

Si una ilustración falta, la app muestra el bloque con el color de la sal.

## Etiquetas (`etiquetas/`)

Hojas A4 listas para imprimir al 100%: `etiquetas_A4_surtidas.pdf` (6 de cada sal) y una hoja por variedad (`etiquetas_A4_TM-0N.pdf`, 24 iguales). Se regeneran con:

```bash
node sales-gourmet/etiquetas/generar.cjs   # desde la raíz; también actualiza www/img/etiqueta-tm-0N.jpg
```

Correcciones respecto del PDF original:

| Antes | Ahora |
|---|---|
| "Villa Pehuenia Moquehue" y "Patagonia Argentina" deformados (texto generado por IA) | Texto tipográfico real: "Villa Pehuenia – Moquehue" y "Patagonia Argentina" |
| Ícono de trigo tachado ("sin TACC") en Caza Patagónica y Bosque Andino | Quitado: no corresponde sin certificación |
| El pie decía 28 etiquetas (4 × 7) de 6 × 4 cm, que no entran en el A4 | 24 etiquetas (4 × 6) de 4,8 × 4,4 cm, con medidas exactas |
| Sin aclaración del destino ni contenido | "Producción artesanal · Obsequio de la casa · 25 g" |
| Textos de la imagen rasterizados | Textos vectoriales (Cinzel, Great Vibes y Lato, licencia OFL) |

Los dibujos se extrajeron de las etiquetas originales, a unos 300 ppi en el tamaño impreso. Para una imprenta conviene vectorizarlos.

La etiqueta de 4,8 × 4,4 cm va en el frente del sobre. El rótulo del dorso (ingredientes, 25 g y lote, sin fechas) lo genera el TM Sales.

## Desarrollo local

```bash
cd sales-gourmet
npm install
python3 -m http.server -d www 8080   # http://localhost:8080
npm run apk                          # requiere Android SDK y JDK 21
```

Desde la raíz: `npm test` y `npm run lint`.

**Firma propia del APK:** secretos `SG_KEYSTORE_BASE64`, `SG_KEYSTORE_PASSWORD`, `SG_KEY_ALIAS` y `SG_KEY_PASSWORD`. El procedimiento es el de [Caza&Pesca](../pesca-patagonia/README.md).
