# Taller TM (producción de las sales, uso interno)

App para producir las Sales Tierras Mágicas que se regalan a los huéspedes: plan de compra, lotes, rótulos, stock y costo de cada obsequio. Es una app separada del recetario de los huéspedes. Funciona sin señal y se instala como APK de Android. No se publica en GitHub Pages.

## Las fórmulas no están en el código

El repositorio es público, así que la app **no trae las fórmulas**:

1. Guardá el archivo de fórmulas (`Formulas_Taller_TM_PRIVADO.json`) en un lugar privado, por ejemplo tu Google Drive. **No lo subas al repositorio.**
2. En el teléfono: **Datos → Cargar fórmulas**. Quedan guardadas solo en ese teléfono.
3. **Datos → Quitar del teléfono** las borra, por ejemplo antes de prestar el teléfono.

El archivo tiene este formato, y la app controla que cada fórmula sume 100%:

```json
{ "app": "taller-tm", "tipo": "formulas", "sales": [
  { "codigo": "TM-01", "nombre": "…", "formula": [ { "ingrediente": "…", "pct": 0, "tipo": "…", "granulometria": "…" } ] } ] }
```

Los tests usan fórmulas ficticias (`test/taller-sales.test.js`). Otro test verifica que el código no contenga fórmulas.

## Funciones

- **Plan:**
  - Kilos por sal y margen de compra.
  - Gramos por ingrediente, total consolidado a comprar y lo que falta según el stock.
  - Sobres doypack de 25 g por lote y hojas de etiquetas: 5 kg rinden 200 sobres y 9 hojas de 24.
  - Con 5 kg por sal y 5% de margen reproduce la planilla de 20 kg (21 kg a comprar).
- **Lotes:**
  - Código `TM-01-AAMMDD-NN` (trazabilidad interna), peso objetivo y real, rendimiento, sobres y responsable.
  - Descuenta los ingredientes del stock.
- **Rótulo de lote:** hoja A4 con un rótulo por sobre, para el dorso. **Sin fechas ni plazo de consumo.** Lleva:
  - nombre, ingredientes en orden alfabético y sin cantidades (para alergias), contenido (25 g) y lote;
  - "Producción artesanal · Obsequio para nuestros huéspedes" (editable en Datos).
- **Stock:** compras con proveedor y lote del proveedor, y ajustes.
- **Costos:** precio por kg de cada ingrediente (los carga el usuario) y costo del sobre con etiquetas. Da el costo de cada sobre obsequiado.
- **Datos:** carga de fórmulas, CSV para Excel, copia de seguridad (incluye las fórmulas: guardala en privado) y restauración.

## Instalación

- **APK:** se publica en Releases como `taller-sales-v1.0.N` → `TallerTM.apk`.
- **El APK no incluye las fórmulas:** se cargan desde el archivo privado.
- **Firma propia:** secretos `TS_KEYSTORE_BASE64`, `TS_KEYSTORE_PASSWORD`, `TS_KEY_ALIAS` y `TS_KEY_PASSWORD`. El procedimiento es el de [Caza&Pesca](../pesca-patagonia/README.md).
- **Datos:** quedan en el teléfono. Desinstalar la app o cambiar la firma los borra, así que hay que hacer copias desde **Datos**.

## Desarrollo local

```bash
cd taller-sales
npm install
python3 -m http.server -d www 8081   # http://localhost:8081
npm run apk                          # requiere Android SDK y JDK 21
```
