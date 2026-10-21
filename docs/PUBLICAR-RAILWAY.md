# Publicar Tierras Mágicas en Railway

Se puede hacer desde el celular, en el navegador (Chrome o Safari). Si alguna pantalla se ve cortada, activá **"Ver versión de escritorio"** en el menú del navegador.

Railway cambia su interfaz cada tanto. Si un botón tiene otro nombre, buscá el más parecido o mandá una captura.

## 1. Crear la cuenta
1. Entrá a **https://railway.com** y tocá **Login** → **Login with GitHub**.
2. Autorizá a Railway con tu cuenta **ricardobersia-pixel**.
3. Elegí un plan. El de prueba alcanza para empezar; para dejarlo fijo hace falta el plan **Hobby**. Revisá el precio vigente en https://railway.com/pricing antes de cargar la tarjeta.

## 2. Crear el proyecto desde GitHub
1. Tocá **New Project** → **Deploy from GitHub repo**.
2. Si no aparece `tierras-magicas`, tocá **Configure GitHub App** y dale acceso a ese repositorio.
3. Elegí **ricardobersia-pixel/tierras-magicas**. Railway empieza a instalarlo solo.

## 3. Disco permanente (¡importante!)
Sin esto, **las reservas se borran** cada vez que se actualiza el sitio.
1. Dentro del proyecto, tocá el servicio **tierras-magicas**.
2. Buscá **Volumes** (o tocá con el botón derecho / mantené apretado el servicio → **Attach Volume**).
3. En **Mount path** escribí: `/data`

## 4. Dirección web
1. En el servicio, entrá a **Settings** → **Networking** → **Generate Domain**.
2. Si pide un puerto, poné `3000`.
3. Copiá la dirección que te da (algo como `tierras-magicas-production.up.railway.app`).

## 5. Variables (configuración secreta)
En el servicio, entrá a **Variables** → **New Variable** y cargá una por una:

| Nombre | Valor |
|---|---|
| `DATA_DIR` | `/data` |
| `BASE_URL` | `https://` + la dirección del paso 4 (sin barra al final) |
| `ADMIN_PASSWORD` | una contraseña larga que solo vos sepas (para entrar al panel) |
| `PORT` | `3000` |

Más adelante, cuando los tengas:

| Nombre | Valor |
|---|---|
| `MP_ACCESS_TOKEN` | Access Token de Mercado Pago (primero el de prueba) |
| `ANTHROPIC_API_KEY` | Clave de la API de Claude (para el chat con IA) |

Al guardar variables, Railway reinicia el sitio solo.

## 6. Probar
1. Abrí `https://TU-DIRECCION` → tiene que aparecer el sitio de Tierras Mágicas.
2. Abrí `https://TU-DIRECCION/admin` → usuario `admin`, contraseña la de `ADMIN_PASSWORD`.
3. Hacé una reserva de prueba por transferencia y verificá que aparezca en el panel. Después cancelala desde el panel.

## Cómo se actualiza
Cada cambio que se sube a GitHub (por ejemplo, cuando Claude modifica precios o textos) Railway lo publica solo en uno o dos minutos. Las reservas quedan guardadas en el disco `/data`.

## Respaldo
Una vez por semana, desde Railway → servicio → **Volumes**, conviene hacer un backup (si la opción está disponible en tu plan) o pedirle a Claude que agregue una exportación de reservas.
