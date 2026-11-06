# Cabañas Tierras Mágicas: sistema de reservas directas

Este es el MVP propio (opción A) con las funciones principales de ClimberHost, adaptado a una operación de cabañas en Argentina.

| Módulo | Qué hace | Estado |
|---|---|---|
| Web de reservas | Búsqueda por fechas y huéspedes, precio por temporada y cantidad de personas (temporada alta en USD, cobrada en pesos), seña 50% o pago total, transferencia o Mercado Pago | ✅ Probado |
| Cobro de seña | Mercado Pago Checkout Pro y webhook que confirma la reserva al aprobarse el pago | ⚠️ Implementado; probar con credenciales de prueba |
| Sincronización Airbnb / Booking | Importa sus calendarios iCal cada 15 min y exporta el calendario propio | ✅ Probado con un iCal local de ejemplo |
| Anti doble reserva | Verificación en una sola transacción al crear la reserva | ✅ Probado |
| Asistente IA en la web | Chat que consulta disponibilidad y precios reales | ⚠️ Implementado; falta probarlo con una clave real |
| Asistente WhatsApp (sin API) | Pegás el mensaje del huésped, la IA redacta la respuesta y la abrís en WhatsApp | ⚠️ Igual que el anterior |
| Pronóstico de pesca (`/pesca`) | Tabla solunar propia (períodos mayores y menores, fase lunar, sol), mejores días con enlace a reservar, instalable como app (PWA) y disponible sin señal. El asistente IA la consulta | ✅ Probado (horarios dentro de ±1 min de la biblioteca SunCalc) |
| App Pesca Patagonia (`pesca-patagonia/`) | Tabla solunar independiente, instalable (PWA y APK de Android), presentada por Tierras Mágicas. Ver [pesca-patagonia/README.md](pesca-patagonia/README.md) | ⚠️ Web probada; el APK lo compila GitHub Actions |
| Panel (`/admin`) | Calendario de 6 semanas, reservas, reserva manual/bloqueo, tareas de check-in y limpieza, ingresos del mes | ✅ Probado |
| Usuarios y roles | Ingreso con email y contraseña. Roles: dueño, recepción y limpieza. Registro de actividad por usuario | ✅ Probado |
| Finanzas y métricas (`/admin` → Finanzas) | Cobros con fecha y medio, gastos fijos/variables (con mensuales que se repiten), montos de Airbnb/Booking, ocupación, ADR, RevPAR, costo por noche, ocupación de equilibrio, flujo de caja de 12 meses, saldos por cobrar y reporte CSV para el contador | ✅ Probado |
| Tarifas y temporadas (`/admin` → Tarifas) | Editar precios por temporada y cabaña, temporadas, calendario, descuento directo y dormi, con validación y vista previa. Lo guardado reemplaza a `config.json` | ✅ Probado |
| Calendario mensual (`/admin` → Calendario) | Mapa de asientos por cabaña y dormi: libre/ocupado con el apellido; al tocar o pasar el mouse, los datos de la reserva (canal, pagos, contacto). Limpieza y mantenimiento ven solo la ocupación | ✅ Probado |
| Turnos (`/admin` → Turnos) | Jacuzzi, sauna, kayaks, tablas de stand up y cualquier equipo con turnos, por horario y cupo | ✅ Probado |
| Unidades de alquiler (`/admin` → Unidades) | Cabañas, dormi y equipos (kayak, stand up, sauna, jacuzzi, bicicleta, bote a motor u otro) con hasta 5 fotos cada una; incluido o con precio, con o sin turnos. Las cabañas nuevas entran en reservas, calendario, tarifas y sincronización; las fotos se ven en la web | ✅ Probado |
| Respuestas para clientes | Preguntas frecuentes con buscador, copiar y enviar por WhatsApp; el dueño las edita (son las mismas de la web) | ✅ Probado |
| Estadísticas e informes PDF | 12 meses: ocupación, ingresos, ADR, canales, cabañas, anticipación, día de llegada, turnos. Informe mensual y de estadísticas en PDF (en la app se abre para guardar o compartir) | ✅ Probado (PDF en el teléfono: falta probar) |
| App del panel (TM Panel) | El panel instalable en el teléfono: app web (Android y iPhone) y APK de Android. Ver [panel-app/README.md](panel-app/README.md) | ⚠️ App web probada; APK compilado por GitHub Actions, falta probarlo en un teléfono. Incluye **TM Panel Prueba**, que funciona sin servidor |

Las capturas están en `docs/capturas/`.

## Puesta en marcha local

Requiere Node.js 22 o superior.

```bash
npm install
cp .env.example .env      # completar las claves
npm start                 # sitio: http://localhost:3000 · panel: /admin (email DUENO_EMAIL + ADMIN_PASSWORD)
```

## Verificación

```bash
npm run lint   # ESLint
npm test       # tests de precios, reservas y pronóstico de pesca (usan una base temporal)
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
6. **Pesca**: confirmar `negocio.coordenadas` en `config.json` (latitud y longitud del pin de Google Maps).
7. **IA**: crear una clave en <https://console.anthropic.com> y ponerla en `ANTHROPIC_API_KEY`.

## Tarifas y temporadas

Se cargan en `config.json` a partir del *Calendario Tarifario 2026-2027* y del *Plan de Tarifas*:

- `temporadas`: Baja, Media, Alta y Alta Premium, cada una con su mínimo de noches, seña y política. La temporada más alta de la estadía define la seña (100% anticipado si toca Alta Premium) y la política.
- `calendario`: tramos con fecha exacta para 2026 y 2027 (feriados y eventos incluidos). Fin de Año exige 5 noches. Fuera del calendario se usa `negocio.temporada_sin_calendario`. **Hay que cargar 2028** antes de abrir reservas para ese año.
- `cabanas[].tarifas`: rango mínimo–máximo por noche de Booking/Airbnb. Domingo a jueves se cobra el mínimo y viernes y sábado el máximo, menos `negocio.precio_directo_descuento` (10%) por venta directa. En Baja, 15% más de descuento desde 4 noches.
- Los tramos marcados `[CONFIRMAR]` no figuraban en el calendario y se completaron con la temporada de la tabla de costos.

## Finanzas

Solo el dueño ve la pestaña **Finanzas**; recepción puede registrar cobros (botón **Cobrar** en cada reserva).

- **Caja:** lo que entró (cobros) y salió (gastos) en el mes. Confirmar una solicitud web registra la seña como cobro; Mercado Pago la registra solo.
- **Ingresos del mes (devengados):** lo que corresponde a las noches del mes, prorrateado por noche.
- **Airbnb/Booking:** las plataformas solo envían fechas. Cada reserva importada queda en un registro permanente donde se carga el neto depositado y la comisión (se toma como cobro el día de ingreso). Los bloqueos de Airbnb ("Not available") no se registran; los de Booking se marcan como "No es reserva".
- **Métricas:** ocupación, ADR (ingreso por noche vendida), RevPAR (por noche disponible), costo por noche = gastos fijos ÷ noches disponibles + variables por noche vendida, y ocupación de equilibrio.
- **Reporte para el contador:** CSV del mes (resumen, cobros, gastos y canales). La factura electrónica (ARCA) queda para una etapa posterior.

## Integraciones

- **Airbnb y Booking:** por calendario iCal, cada 15 minutos. Los enlaces se cargan en el panel → **Ajustes**. Para sincronización instantánea (sin ventana de doble reserva) hace falta un channel manager con conexión oficial.
- **WhatsApp:** enlaces directos desde reservas, respuestas y el asistente. Responder desde el panel requiere WhatsApp Business Platform (API de Meta, número dedicado y negocio verificado).
- **Instagram:** las reservas que llegan por Instagram se cargan con ese canal para medirlas. Recibir los mensajes en el panel requiere la API de Instagram de Meta (cuenta profesional vinculada a una página de Facebook).

## Usuarios y permisos

El primer arranque crea al dueño con `DUENO_EMAIL` y `ADMIN_PASSWORD`. Desde el panel, en **Usuarios**, el dueño suma al resto con email y contraseña inicial (mínimo 10 caracteres).

| Puede… | Dueño | Recepción | Limpieza |
|---|:-:|:-:|:-:|
| Ver calendario de ocupación | ✅ | ✅ | ✅ (sin datos de huéspedes; igual Mantenimiento) |
| Marcar tareas hechas | ✅ | ✅ | Solo limpieza |
| Ver reservas, crear/confirmar/cancelar/reprogramar, bloquear fechas | ✅ | ✅ | — |
| Sincronizar Airbnb/Booking y usar el asistente de WhatsApp | ✅ | ✅ | — |
| Ver ingresos del mes y enlaces iCal | ✅ | — | — |
| Crear usuarios, cambiar roles, dar de baja, asignar contraseñas | ✅ | — | — |
| Ver la actividad reciente (quién hizo qué) | ✅ | — | — |

- Cada uno puede cambiar su contraseña con **Mi contraseña**. Si alguien la olvida, el dueño le asigna una nueva.
- Al desactivar un usuario, cambiarle el rol o asignarle contraseña, se cierran sus sesiones abiertas.
- Siempre queda al menos un dueño activo.
- Sesiones de 14 días en cookie `HttpOnly`; las contraseñas se guardan con `scrypt`. Máximo 5 intentos de ingreso por minuto por IP.

## Publicación (producción)

Guía paso a paso para Railway: [docs/PUBLICAR-RAILWAY.md](docs/PUBLICAR-RAILWAY.md). Hace falta un servidor con disco persistente (`DATA_DIR`), porque la base es SQLite. Requisitos:
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
