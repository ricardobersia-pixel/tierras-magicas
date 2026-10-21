# Cabañas Tierras Mágicas: sistema de reservas directas

Este es el MVP propio (opción A) con las funciones principales de ClimberHost, adaptado a una operación de cabañas en Argentina.

| Módulo | Qué hace | Estado |
|---|---|---|
| Web de reservas | Búsqueda por fechas y huéspedes, precio por temporada, seña %, formulario | ✅ Probado |
| Cobro de seña | Mercado Pago Checkout Pro y webhook que confirma la reserva al aprobarse el pago | ⚠️ Implementado; probar con credenciales de prueba |
| Sincronización Airbnb / Booking | Importa sus calendarios iCal cada 15 min y exporta el calendario propio | ✅ Probado con un iCal local de ejemplo |
| Anti doble reserva | Verificación en una sola transacción al crear la reserva | ✅ Probado |
| Asistente IA en la web | Chat que consulta disponibilidad y precios reales | ⚠️ Implementado; falta probarlo con una clave real |
| Asistente WhatsApp (sin API) | Pegás el mensaje del huésped, la IA redacta la respuesta y la abrís en WhatsApp | ⚠️ Igual que el anterior |
| Panel del dueño (`/admin`) | Calendario de 6 semanas, reservas, reserva manual/bloqueo, tareas de check-in y limpieza, ingresos del mes | ✅ Probado |

Las capturas están en `docs/capturas/`.

## Puesta en marcha local

Requiere Node.js 22 o superior.

```bash
npm install
cp .env.example .env      # completar las claves
npm start                 # sitio: http://localhost:3000 · panel: /admin (usuario: admin)
```

## Qué tenés que completar

1. **`config.json`**: todo lo marcado `[COMPLETAR]`. Incluye nombres de cabañas, capacidad, precio por noche, mínimo de noches, temporadas, políticas, ubicación y tu número de WhatsApp (formato `549` + característica + número, sin espacios).
2. **Fotos**: reemplazar los SVG de `public/img/` por fotos reales y actualizar `foto` en `config.json`.
3. **Airbnb**: Calendario → Disponibilidad → *Conectar calendarios*.
   - Copiar el enlace de **exportación** en `ical_importar.airbnb` de cada cabaña.
   - *Importar calendario* con el enlace que muestra el panel en "Conexión con Airbnb y Booking".
4. **Booking**: Extranet → Tarifas y disponibilidad → *Sincronizar calendarios*. Es el mismo procedimiento con `ical_importar.booking`.
5. **Mercado Pago**: crear una aplicación en <https://www.mercadopago.com.ar/developers/panel>.
   - Primero probar con el *Access Token de prueba* y usuarios de prueba.
   - Después pasar al de producción en `MP_ACCESS_TOKEN`.
6. **IA**: crear una clave en <https://console.anthropic.com> y ponerla en `ANTHROPIC_API_KEY`.

## Publicación (producción)

Hace falta un servidor con disco persistente, porque la base es SQLite en `data/`. Opciones simples: Railway, Render (con disco) o un VPS. Requisitos:
- `BASE_URL` con **https**. Mercado Pago solo envía avisos de pago a URLs https.
- Backup diario de `data/tierras-magicas.db`.
- Dominio propio, por ejemplo `tierrasmagicas.com.ar` (registro en NIC Argentina).

## Riesgos y limitaciones conocidas

- **Sincronización iCal no instantánea**: Airbnb y Booking leen el calendario cada 1 a 3 horas aproximadamente. Hay una ventana de riesgo de doble reserva, igual que en cualquier sistema basado en iCal. Para eliminarla hace falta un channel manager con API oficial; se decide en la fase siguiente.
- **WhatsApp sin API**: la IA redacta y vos enviás. Responder solo, como ClimberHost, requiere WhatsApp Business Platform (API de Meta) y un número dedicado.
- **Seña y saldo**: se cobra solo la seña online; el saldo se cobra en el lugar. Facturación (ARCA/AFIP) no incluida.
- **Reservas web**: sin Mercado Pago (modo demo), una solicitud web retiene las fechas hasta que la confirmás o cancelás desde el panel. Con Mercado Pago, se liberan a los 30 minutos si no se pagó.

## Estructura

```
config.json          datos del negocio y de las cabañas
src/server.js        rutas web, API, panel y webhook
src/reservas.js      disponibilidad, precios, reservas, tareas
src/ical.js          importación/exportación de calendarios
src/mercadopago.js   cobro de la seña
src/asistente.js     asistente IA (Claude) con consulta de disponibilidad
public/              sitio público y panel
```
