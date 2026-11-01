# Pesca Patagonia

Tabla solunar de pesca para la Patagonia, presentada por Cabañas Tierras Mágicas. Es una app separada del sitio de reservas. Los cálculos se hacen en el teléfono y funcionan sin señal, y no envía datos a ningún servidor.

| Qué | Dónde |
|---|---|
| App web instalable (PWA) | https://ricardobersia-pixel.github.io/tierras-magicas/ (cuando GitHub Pages esté activado) |
| APK de Android | https://github.com/ricardobersia-pixel/tierras-magicas/releases/latest/download/PescaPatagonia.apk |
| Código de la app | `www/` (HTML, CSS y JS sin compilación) |
| Motor de cálculo | `www/js/solunar.js` (lo comparte con el servidor de Tierras Mágicas) |
| Lugares y patrocinador | `www/js/lugares.js` |
| Proyecto Android (Capacitor) | `android/` |

## Funciones

- Lugares de Neuquén, Río Negro, Chubut, Santa Cruz y Tierra del Fuego, o la ubicación del GPS.
- Puntaje por día de 0 a 100, fase lunar, salida y puesta del sol.
- Períodos mayores (2 h) y menores (1 h) en una línea de 24 h.
- Los 3 mejores días del período.
- Recuerda el último lugar elegido.
- Modo oscuro según el teléfono.
- Bloque "Presentado por Cabañas Tierras Mágicas", con WhatsApp e Instagram.

## Cómo se instala

**Android (APK):**
1. Abrí desde el teléfono el enlace del APK de la tabla.
2. Tocá el archivo descargado.
3. Si el teléfono lo pide, permití "Instalar apps de esta fuente" para el navegador o el administrador de archivos.

**Android o iPhone (app web):**
- Abrí la dirección de la app web.
- En Chrome: menú ⋮ → **Instalar app** o **Agregar a la pantalla principal**.
- En Safari: botón compartir → **Agregar a inicio**.

## Cómo se publica

Lo hace solo GitHub Actions (`.github/workflows/pesca-patagonia.yml`):

- Cada cambio en `pesca-patagonia/` compila el APK. Se descarga desde la ejecución, en la sección *Artifacts*.
- Al unir a `main`:
  - El APK se publica en **Releases**.
  - La app web se publica en **GitHub Pages**.

### Activar GitHub Pages (una sola vez)

En GitHub: repositorio → **Settings** → **Pages** → **Build and deployment** → **Source: GitHub Actions**.

### Firma propia del APK (recomendado antes de repartirlo)

Sin firma propia, el APK se firma con una clave de depuración distinta en cada compilación. Para instalar una versión nueva hay que desinstalar la anterior, y se pierden el lugar y la ubicación guardados.

Para que las actualizaciones se instalen encima:

1. Crear la clave una sola vez, en una computadora con Java, y guardarla en un lugar seguro. Si se pierde, no se pueden publicar actualizaciones con la misma firma.
   ```bash
   keytool -genkeypair -v -keystore pesca-patagonia.jks -alias pesca-patagonia -keyalg RSA -keysize 2048 -validity 10000
   base64 -w0 pesca-patagonia.jks > pesca-patagonia.jks.txt
   ```
2. En GitHub: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**. Crear estos secretos:
   - `PP_KEYSTORE_BASE64`: el contenido de `pesca-patagonia.jks.txt`
   - `PP_KEYSTORE_PASSWORD`: la contraseña del almacén
   - `PP_KEY_ALIAS`: `pesca-patagonia`
   - `PP_KEY_PASSWORD`: la contraseña de la clave

## Desarrollo local

```bash
cd pesca-patagonia
npm install
python3 -m http.server -d www 8080   # app web en http://localhost:8080
npm run sync                         # copia www/ al proyecto Android
npm run apk                          # requiere Android SDK y JDK 21
```

Las coordenadas de los lugares son aproximadas (centro de la localidad). Un error de unos kilómetros cambia los horarios menos de un minuto.
