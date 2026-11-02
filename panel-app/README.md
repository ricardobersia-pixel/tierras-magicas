# TM Panel (app del equipo)

El panel de Tierras Mágicas (`/admin`) como app de teléfono, para dueño, recepción y limpieza. La app **no guarda datos**: abre el panel publicado en el servidor. Por eso, antes de instalarla, el sitio tiene que estar publicado con `https` (ver [docs/PUBLICAR-RAILWAY.md](../docs/PUBLICAR-RAILWAY.md)).

Hay dos formas de instalarla. Las dos usan los mismos usuarios y contraseñas del panel.

## Para probar sin servidor: TM Panel Prueba

Una app aparte (se instala junto a TM Panel) con el panel completo **dentro del teléfono**: no necesita Railway ni internet.

- **Descargar:** Releases → la versión más nueva de **TM Panel Prueba** → `TMPanelPrueba.apk`.
- **Ingresar:** tocá uno de los usuarios de prueba (dueño, recepción o limpieza). Contraseña: `tierras1234`.
- Trae reservas de ejemplo para ver el calendario y las tareas. **Restablecer** (arriba) borra todo y vuelve al inicio.
- Usa la misma lógica de reservas, precios, permisos y usuarios que el servidor (`src/`), con una base SQLite guardada en el teléfono.
- No incluye lo que necesita servidor: sincronización con Airbnb/Booking, asistente IA, Mercado Pago. Los datos no se comparten entre teléfonos.

Se arma con `node prueba/construir.mjs` (deja la app en `www-prueba/`); GitHub Actions la compila junto con TM Panel.

## Opción 1: app web instalable (Android y iPhone, sin APK)

1. Abrí en el teléfono `https://TU-DIRECCION/admin` e ingresá.
2. **Android (Chrome):** menú ⋮ → **Instalar app** (o **Agregar a la pantalla principal**).
3. **iPhone (Safari):** botón compartir → **Agregar a inicio**.

Queda el ícono **TM Panel** y se abre a pantalla completa. Se actualiza sola con cada cambio del sitio.

## Opción 2: APK de Android

**Descargar:** https://github.com/ricardobersia-pixel/tierras-magicas/releases → la versión más nueva de **TM Panel** → `TMPanel.apk`. Abrí el enlace desde el teléfono.

**Instalar y abrir:**
1. Tocá `TMPanel.apk` descargado. Si el teléfono lo pide, permití "Instalar apps de esta fuente".
2. La primera vez, la app pide la **dirección del panel**: la de Railway, por ejemplo `tierras-magicas-production.up.railway.app`. Queda guardada.
3. Ingresá con tu email y contraseña del panel.

Si no puede abrir el panel, la app dice el motivo (sin internet, dirección que no existe en Railway, servidor caído, certificado) y qué hacer, con **Reintentar** y **Cambiar la dirección**. Los enlaces de WhatsApp se abren con la app de WhatsApp.

**Cómo se publica:** GitHub Actions (`.github/workflows/panel-app.yml`) compila el APK en cada cambio de `panel-app/`. Lo publica en **Releases** al unir a `main` o al ejecutar **Actions → TM Panel (APK) → Run workflow** (fuera de `main` queda como versión de prueba).

**Opcional:** la variable del repositorio `TM_PANEL_URL` (Settings → Secrets and variables → Actions → Variables) deja fijada la dirección y la app ya no la pide. Solo se aceptan direcciones `https://*.up.railway.app`: para un dominio propio hay que agregarlo en `allowNavigation` de `capacitor.config.json`.

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
| Pantalla de dirección (primera vez) | `panel-app/www/index.html` y `www/panel.js` |
| Dominios que la app puede abrir | `panel-app/capacitor.config.json` (`allowNavigation`) |
| Pantalla si no abre el panel, con el motivo | `panel-app/www/sin-conexion.html` y `www/motivo.js`; el código de error lo pasa `MainActivity.java` |
