# TM Panel (app del equipo)

El panel de Tierras Mágicas (`/admin`) como app de teléfono, para dueño, recepción y limpieza. La app **no guarda datos**: abre el panel publicado en el servidor. Por eso, antes de instalarla, el sitio tiene que estar publicado con `https` (ver [docs/PUBLICAR-RAILWAY.md](../docs/PUBLICAR-RAILWAY.md)).

Hay dos formas de instalarla. Las dos usan los mismos usuarios y contraseñas del panel.

## Opción 1: app web instalable (Android y iPhone, sin APK)

1. Abrí en el teléfono `https://TU-DIRECCION/admin` e ingresá.
2. **Android (Chrome):** menú ⋮ → **Instalar app** (o **Agregar a la pantalla principal**).
3. **iPhone (Safari):** botón compartir → **Agregar a inicio**.

Queda el ícono **TM Panel** y se abre a pantalla completa. Se actualiza sola con cada cambio del sitio.

## Opción 2: APK de Android

Lo compila GitHub Actions (`.github/workflows/panel-app.yml`).

**Una sola vez, configurar la dirección del panel:**
GitHub → repositorio → **Settings** → **Secrets and variables** → **Actions** → pestaña **Variables** → **New repository variable**:

| Nombre | Valor |
|---|---|
| `TM_PANEL_URL` | `https://` + la dirección de Railway, sin `/admin` (ej. `https://tierras-magicas-production.up.railway.app`) |

Después, en **Actions** → **TM Panel (APK)** → **Run workflow**. Sin esa variable el flujo termina con un aviso y no compila.

**Descargar e instalar:**
- Desde la ejecución terminada, sección **Artifacts** → `TMPanel-1.0.N` (es un .zip con `TMPanel.apk` adentro).
- Al unir a `main` también se publica en **Releases** (etiqueta `tm-panel-v1.0.N`).
- En el teléfono: abrir `TMPanel.apk` y permitir "Instalar apps de esta fuente".

Si cambia la dirección del servidor, hay que actualizar `TM_PANEL_URL` y volver a compilar.

### Firma propia (recomendado antes de repartirlo al equipo)

Sin firma propia, cada compilación firma distinto: para actualizar hay que desinstalar la versión anterior (y volver a ingresar). Para evitarlo:

```bash
keytool -genkeypair -v -keystore tm-panel.jks -alias tm-panel -keyalg RSA -keysize 2048 -validity 10000
base64 -w0 tm-panel.jks > tm-panel.jks.txt
```

Guardá `tm-panel.jks` en un lugar seguro y creá estos secretos en GitHub (**Secrets** → **New repository secret**): `TM_KEYSTORE_BASE64` (contenido de `tm-panel.jks.txt`), `TM_KEYSTORE_PASSWORD`, `TM_KEY_ALIAS` (`tm-panel`) y `TM_KEY_PASSWORD`.

## Cómo funciona

| Qué | Dónde |
|---|---|
| Ícono, nombre y colores de la app web | `public/panel.webmanifest`, `public/img/icono-panel*` |
| Aviso sin conexión (web) | `public/sw.js` y `public/sin-conexion.html`. Los datos del panel nunca se guardan en el teléfono |
| Proyecto Android (Capacitor 8) | `panel-app/android/` |
| Dirección que abre el APK | `panel-app/capacitor.config.json` (`server.url`), la fija `configurar.mjs` al compilar |
| Pantalla si el servidor no responde | `panel-app/www/sin-conexion.html` |

En el APK, los enlaces a WhatsApp y al sitio se abren con las apps del teléfono.
