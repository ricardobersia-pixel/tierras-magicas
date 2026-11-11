# Sales de la Cordillera (Sales Gourmet Tierras Mágicas)

App móvil de las cuatro sales de Cabañas Tierras Mágicas. Sigue el mismo esquema que Caza&Pesca Patagonia: app web instalable (PWA) y APK de Android compilado por GitHub Actions. Funciona sin señal y no envía datos a ningún servidor.

| Qué | Dónde |
|---|---|
| App web (PWA) | https://ricardobersia-pixel.github.io/tierras-magicas/sales/ (cuando GitHub Pages esté activado) |
| APK de Android | Releases → `sales-gourmet-v1.0.N` → `SalesTM.apk`. No queda como "latest" para no cambiar el enlace del APK de Caza&Pesca |
| Datos (fórmulas, recetas, guía) | `www/js/datos.js` |
| Cálculos (escalado, compra, costos, lotes, stock) | `www/js/calculos.js`, con tests en `test/sales-gourmet.test.js` |
| Proyecto Android (Capacitor) | `android/` (`ar.tierrasmagicas.salesgourmet`) |

## Funciones

**Para el cliente:**
- **Sales:** las 4 variedades con su etiqueta, para qué sirve cada una, la lista de ingredientes en orden decreciente y la fórmula con granulometría.
- **Recetas:** las 20 del libro de cocina, con buscador y filtro por sal. Se agregaron avisos de seguridad donde hacen falta (ceviche, cerdo, pollo, carne de caza y hongos).
- **Guía de uso:** la del libro, más el porcentaje de sal de cada producto y la recomendación de la OMS.
- **Enlace para QR:** `…/sales/?sal=TM-01` abre directo la ficha de esa sal. Sirve para poner un QR en la etiqueta.

**Taller (producción):**
- **Plan:** kilos por sal y margen de compra. Da los gramos por ingrediente, el total consolidado a comprar, lo que falta según el stock, los frascos por neto y las hojas de etiquetas. Con 5 kg por sal y 5% de margen reproduce la planilla *Compra y Producción 20 kg* (21.000 g a comprar).
- **Lotes:** código automático `TM-01-AAMMDD-NN`, peso objetivo y real, rendimiento, vencimiento por vida útil y responsable. Descuenta los ingredientes del stock. Reemplaza la hoja *Control Producción*.
- **Rótulo de lote:** hoja A4 con los datos que la etiqueta artística no tiene: ingredientes, contenido neto, lote, elaboración, vencimiento, elaborador, RNE y RNPA. Lo que falte sale resaltado para completar. En el APK se guarda como archivo para imprimirlo desde Chrome.
- **Stock:** compras con proveedor y lote del proveedor, y ajustes. Reemplaza la hoja *Inventario*.
- **Costos:** precio por kg de cada ingrediente (los carga el usuario; la app no trae precios), envase por frasco y ganancia. Da el costo por kg, el costo por frasco y el precio sugerido.
- **Datos:** CSV del plan, de los lotes y del stock (abren en Excel), copia de seguridad y restauración, control de que las fórmulas cierren en 100%, y datos del elaborador para el rótulo.

Los datos del taller se guardan solo en el teléfono (`localStorage`). Si se borra la app, se pierden: hay que hacer copias desde **Datos**.

## Análisis de los materiales de origen

### HECHOS verificados

- Las 4 fórmulas cierran en 100% (1.000 g/kg) y el plan de 20 kg cierra en 20.000 g (21.000 g con el 5%). Lo comprueban los tests.
- 20 ingredientes distintos, de los cuales 6 son compuestos sin ficha propia: Sal con Hongos, con Limón, con Mandarina, Ahumada, con Vino Tinto y Mix de Hierbas.

### Observaciones y mejoras propuestas

| # | Material | Observación | Propuesta |
|---|---|---|---|
| 1 | Etiquetas | El pie dice "28 etiquetas (4 × 7), 6,0 × 4,0 cm", pero la hoja tiene **24 (4 × 6)** de unos **4,8 × 4,5 cm**. Cuatro etiquetas de 6 cm no entran en los 21 cm del A4. | Corregir el pie o el diseño antes de pedir la imprenta. La app calcula con 24 por hoja. |
| 2 | Etiquetas | No tienen los datos obligatorios del rótulo de alimentos (Código Alimentario Argentino, cap. V): lista de ingredientes, contenido neto, lote, vencimiento, elaborador, RNE y RNPA. | Etiqueta trasera o el rótulo de lote que genera la app. |
| 3 | Etiquetas | El texto generado por IA tiene errores: "Moquehue" aparece deformado y "Patagonia Argentina" ilegible a ese tamaño. | Rehacer los textos chicos con tipografía real. |
| 4 | Etiquetas | Caza Patagónica y Bosque Andino muestran un ícono de trigo tachado, que se lee como "sin gluten / Sin TACC". | Quitarlo hasta tener la certificación Sin TACC: sin ella es una declaración no autorizada. |
| 5 | Formulaciones | Los 6 ingredientes compuestos no tienen ficha. | Cargar sus fórmulas. Sin ellas, la lista de ingredientes del rótulo queda incompleta y no hay trazabilidad completa. |
| 6 | Formulaciones | HIPÓTESIS a verificar: la Sal con Vino Tinto podría aportar sulfitos, que se declaran desde 10 mg/kg. | Pedir ficha técnica al proveedor o hacer un análisis. |
| 7 | Compra 20 kg | El 5% se aplica como "× 1,05". Si la merma real es del 5% sobre lo comprado, hace falta "÷ 0,95". La diferencia es de 0,26%. | Medir el rendimiento real con los lotes y ajustar el margen. |
| 8 | Compra 20 kg | No hay precios, envase, neto por frasco ni vida útil. | Se cargan en la app. No se inventaron valores. |
| 9 | Libro de cocina | Las imágenes son de 512 px (≈ 65 ppi). | Para imprimir se necesitan alrededor de 300 ppi: regenerar en alta resolución. |
| 10 | Libro de cocina | La página 5 arrastra el final de la página de Bosque Andino (focaccia) y tiene otro estilo de texto e íconos. | Rearmar esa página. |
| 11 | Libro de cocina | El ceviche no advierte sobre parásitos del pescado crudo, tema importante con la trucha. Las carnes no indican temperatura interna. | La app agrega los avisos (referencia: USDA FSIS y FDA). Sumarlos al libro. |
| 12 | Guía de uso | "1/2 a 1 cucharadita por porción" de un producto con 65 a 80% de sal puede superar en una sola comida los 5 g diarios de la OMS (INFERENCIA: falta pesar una cucharadita de cada sal). | Pesar una cucharadita de cada sal y, si se confirma, bajar a "1/4 a 1/2". |
| 13 | Posicionamiento | La etiqueta de Bosque Andino dice "huevos, pastas, vegetales", pero el libro le asigna salmón. Se superpone con Lago & Trucha. | Unificar el mensaje. |
| 14 | Regulatorio | Para vender hacen falta RNE (establecimiento) y RNPA (producto) ante la bromatología provincial. Además, hay que confirmar si la Ley 27.642 de etiquetado frontal (sello "Exceso en sodio") alcanza a un condimento a base de sal. | Consultar con un bromatólogo antes de vender. Es el gate para pasar a la venta. |

### Gate para pasar a venta

1. RNE y RNPA, con rótulo completo (puntos 2, 5 y 14).
2. Etiqueta corregida (puntos 1, 3 y 4).
3. Vida útil definida: con ensayo o con el criterio del bromatólogo.
4. Costos cargados en la app y precio validado.

## Desarrollo local

```bash
cd sales-gourmet
npm install
python3 -m http.server -d www 8080   # app web en http://localhost:8080
npm run sync                         # copia www/ al proyecto Android
npm run apk                          # requiere Android SDK y JDK 21
```

Desde la raíz del repositorio: `npm test` y `npm run lint`.

## Firma propia del APK

Es el mismo procedimiento que en [Caza&Pesca](../pesca-patagonia/README.md), con estos secretos:

- `SG_KEYSTORE_BASE64`
- `SG_KEYSTORE_PASSWORD`
- `SG_KEY_ALIAS`
- `SG_KEY_PASSWORD`

Sin ellos, cada APK se firma con una clave de depuración y para actualizar hay que desinstalar la versión anterior. Al desinstalar se borran los datos del taller.
