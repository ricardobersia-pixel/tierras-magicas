# Auditoría del mensaje de WhatsApp para reservas directas

**Canal auditado:** WhatsApp +54 299 590 3070, la respuesta que recibe quien consulta por una reserva directa.
**Fecha:** 12-nov-2026 · **Fase:** PLC-10 Operación y Mejora · **Perfil líder:** Hospitalidad / Revenue (venta directa)
**Perfiles de apoyo:** Marketing conversacional y Riesgos (derecho del consumidor, seguridad del spa y del lago)

**Pregunta a resolver:** ¿el mensaje actual convierte una consulta en una seña cobrada? Si no, ¿qué hay que cambiar?

**Respuesta corta:** no, en el estado actual no convierte bien. Le pasa el precio de temporada alta al precio de Booking, deja la segunda cabaña con precio "000", contradice las políticas que el dueño cargó en el sistema de reservas y no le hace ninguna pregunta al huésped. Tal como está, es más probable que espante a quien consulta en temporada media o baja, o que lo mande a reservar por Booking, que que termine en una seña.

---

## 1. Fuentes y cómo se distinguió cada cosa

| Tipo | Fuente |
|---|---|
| **HECHO** | El texto del mensaje que pasó el dueño |
| **HECHO** | 29 fotos que pasó el dueño (25 distintas y 4 repetidas) |
| **DATO** | `config.json` del repositorio, cargado con "datos provistos por el dueño (oct-2026)": políticas, tarifas 2026-2027, servicios incluidos y calendario de temporadas |
| **INFERENCIA** | Lo que se concluye cruzando el mensaje con las fotos y los datos. Va marcado como tal |
| **SUPUESTO** | Lo que hay que confirmar. Va marcado **[CONFIRMAR]** |

No hay métricas de conversión (consultas, señas, tiempo de respuesta), así que no se puede cuantificar cuántas reservas se pierden hoy. La sección 7 propone medirlo.

---

## 2. Hallazgos críticos (corregir hoy)

### C1. El precio es el de Booking en temporada alta, sin el descuento directo
- **Mensaje:** "Casa de Montaña hasta 6 Pax: 260000 p/n", sin indicar fechas ni temporada.
- **Dato:** en `config.json`, $260.000 es exactamente el **máximo de Booking/Airbnb en temporada Alta** (viernes y sábado) para la cabaña de 6 personas. La política propia dice "Reservando directo tenés un 10% de descuento sobre las tarifas de Booking y Airbnb".
- **Inferencia:** hoy (12-nov) corre la temporada **Media**, y la tarifa directa de la cabaña de 6 queda entre **$135.000 y $171.000** por noche. El mensaje cotiza entre un **52% y un 93% más caro** que la propia lista de precios. Si el huésped compara con Booking, ve un precio menor y reserva ahí, con comisión para la plataforma.
- **Corrección:** no poner un precio fijo en el primer mensaje. Cotizar según las fechas (ver la tabla de la sección 5).

### C2. La cabaña de 4 personas tiene precio "000 p/n"
- **Hecho:** el precio no está.
- **Inferencia:** para el huésped es descuido, o una invitación a preguntar que muchos no hacen. Además la Ley 24.240 (art. 4, deber de información, y art. 7, la oferta obliga) exige informar el precio de forma clara.
- **Corrección:** sale el número del mensaje y se cotiza según las fechas.

### C3. Las políticas del mensaje contradicen las del sistema

| Tema | Lo que dice el mensaje | Lo que figura en `config.json` (dueño, oct-2026) |
|---|---|---|
| Estadía mínima | "2 noches" | 2 noches en Baja y Media, **3 en Alta y Alta Premium**, **5 del 24 al 31 de diciembre** |
| Seña | "50%" | 50%, salvo **Alta Premium: 100% por adelantado, no reembolsable** |
| Cancelación | No la menciona | 15 días o más antes: se devuelve lo abonado. Menos de 15 días: se pierde lo abonado o se reprograma |
| Descuentos | "mayor a 7 días" | **Baja: 15% desde 4 noches**. Directo: 10% sobre Booking |
| Mascotas | "bajo solicitud" | "mascotas de tamaño mediano" |
| Pagos | Efectivo, moneda extranjera, CBU, Mercado Pago | Transferencia o Mercado Pago **[CONFIRMAR si siguen aceptando efectivo y dólares]** |
| Fumar | No lo menciona | Prohibido dentro de la cabaña |

**Riesgo:** si alguien reserva el 28 de diciembre por 2 noches con el 50%, el mensaje lo autorizó y la política no. Eso termina en un reclamo, una reseña negativa o una devolución. Informar la política de cancelación **antes** de cobrar es obligatorio (Ley 24.240, art. 4).

### C4. "Acceso exclusivo a Costa Lago Moquehue a 100 metros"
- **Dato:** `config.json` dice "Estamos a 100 metros del lago, con vista al lago, **pero no sobre la costa**", y la pregunta frecuente responde "No" a "¿Están sobre la costa?".
- **Riesgo:** "exclusivo" promete algo que no se puede garantizar si el acceso es público o compartido. **[CONFIRMAR si el acceso es privado.]** Si no lo es, poner "a 100 m del lago, con vista al lago".

### C5. No dice que el spa y los equipos están incluidos
- **Dato:** la tina caliente, el sauna, los kayaks, el stand up, el airtrack y la isla flotante están **incluidos en la tarifa**.
- **Hecho:** el mensaje los enumera pero no dice que no tienen costo, y ni menciona el airtrack ni la isla flotante (que sí aparecen en la foto aérea).
- **Inferencia:** es el mayor diferencial del complejo frente a la competencia de Villa Pehuenia y Moquehue, y queda escondido. Es lo que justifica el precio.

### C6. Hay dos versiones del mensaje en uso, y no coinciden
El dueño pasó una segunda versión. Es igual a la primera salvo en tres datos:

| Dato | Versión 1 | Versión 2 | Referencia directa (`config.json`, Booking − 10%) |
|---|---|---|---|
| Casa para 6 | $260.000/noche | **$250.000/noche** | Alta: $189.000–$234.000 · Media: $135.000–$171.000 |
| Casa para 4 | "000" | **$210.000/noche** | Alta: $144.000–$171.000 · Media: $99.000–$126.000 |
| Dirección | Ruta 11, Km 12 | **Ruta 11, Km 12,5** | **Confirmado por el dueño: Km 8,2. Las dos versiones están mal** |

**Inferencias sobre la versión 2:**
- **Casa para 6 a $250.000:** sigue por encima del precio directo de Alta ($234.000) y apenas un 4% por debajo del máximo de Booking en Alta ($260.000). En temporada Media cotiza entre un 46% y un 85% más caro que la lista propia.
- **Casa para 4 a $210.000: es el problema más grave.** Es **más cara que la tarifa de Booking en Alta** (máximo $190.000, un 10,5% más) y coincide con el **mínimo de Alta Premium** en Booking. En temporada Media cotiza entre un 67% y un 112% por encima del precio directo. Quien compare con Booking va a reservar ahí.
- **Relación entre las dos casas:** en el mensaje la de 4 cuesta el 84% de la de 6. En la lista de tarifas es alrededor del 73%. La casa chica queda cara en proporción, justo para el segmento de parejas y familias chicas, que es el que más compara precios.
- **Dos versiones circulando:** a dos huéspedes que consultan lo mismo se les pueden cotizar $260.000 o $250.000, con dos direcciones distintas. Eso resta credibilidad y le complica a recepción saber cuál cotización tiene que respetar.

**Confirmado por el dueño (12-nov):** se usan las dos versiones a la vez.

**Corrección (implementada):** se dan de baja las dos versiones. Las respuestas se arman en el panel, en **Operación → Responder consulta de reserva**, con el cuadro tarifario de **Tarifas** (ver la sección 9).

---

## 3. Hallazgos importantes

| # | Hallazgo | Evidencia | Corrección |
|---|---|---|---|
| I1 | Un solo bloque de unos 2.500 caracteres. En el celular son 4 o 5 pantallas | Hecho | Partirlo en 3 mensajes cortos que respondan a lo que el huésped va preguntando |
| I2 | No le pregunta nada al huésped. No hay próximo paso | Hecho | Abrir con: fechas, cantidad de personas y si viaja con mascota |
| I3 | "Anafe a gas" cuando las fotos muestran **cocina con horno** en las dos cabañas | Fotos (Conometal en la de 4; cocina con horno en la de 6) | Poner "cocina a gas con horno" |
| I4 | "Heladera con freezer" para todas las cabañas | La de 4 tiene un frigobar SLAM bajo mesada | **[CONFIRMAR si tiene congelador]**. Si no, poner "heladera" en esa cabaña |
| I5 | Falta el **dormi** para 4 personas más ($20.000 por persona por noche) | Dato | Ofrecerlo cuando el grupo supera la capacidad. Es una venta adicional que hoy se pierde |
| I6 | El sector de fuegos aparece sin aclarar que **la leña no está incluida** | Dato | Aclararlo para evitar sorpresas al llegar |
| I7 | Faltan las amenities y los básicos de cocina (shampoo, secador, café, té, aceite) | Dato | Mencionarlos en una línea. Se perciben como valor agregado |
| I8 | Termina con "Booking" y "Google" como contacto | Hecho | **Sacar Booking.** Mandar a reservar por una plataforma con comisión desde el canal directo va en contra del negocio. Google se usa después de la estadía, para pedir la reseña |
| I9 | Repite el número de teléfono dentro del mismo chat de WhatsApp | Hecho | Sacarlo. Poner el link de Google Maps |
| I10 | Spa: "espuma y batas solo verano", sin horarios ni turnos | Dato: cuando hay mucha demanda se usan turnos | Aclarar "con turno cuando el complejo está completo" |
| I11 | Kayaks y stand up sin la condición de seguridad | Dato: chaleco obligatorio y deslinde firmado | No hace falta en el primer mensaje. Va en la confirmación y en la bienvenida |
| I12 | "Alquiler por día" cuando se cobra por noche | Hecho | Decir "por noche" |
| I13 | No hay link a la web de reservas, aunque el sistema ya la tiene | Repositorio | Cuando esté publicada (ver `docs/PUBLICAR-RAILWAY.md`), sumar un link con las fechas ya cargadas **[CONFIRMAR si está en línea]** |

## 4. Forma, ortografía y marca

- **Errores:** "La cabañas esta" → "La cabaña está"; "Dec" → "Deck"; "Sofa" → "Sofá"; "Moneda Extranjera"; "escocesa.y"; "gmail.com y"; "Magicas" → "Mágicas"; "Neuquen" → "Neuquén"; "Pic-nic" → "picnic".
- **Marca inconsistente:** dice "Cabañas" en el título y "Casa de Montaña" en el resto, mientras el sistema usa "Cabaña 1, 2 y 3". Conviene elegir uno. Sugerencia: **"Casa de Montaña para 6" y "Casa de Montaña para 4"**.
- **Capacidad poco clara:** "2, 4 y hasta 6 Pax" confunde. Mejor "hasta 6 personas".
- **Ducha:** las fotos muestran una **columna de hidromasaje** con jets. Se entiende mejor y vende más que "ducha escocesa".

## 5. Fotos: auditoría

### Qué se ve en cada unidad (inferencia por estilo)

| Unidad | Fotos | Lo que muestran |
|---|---|---|
| **Casa de 6** (planta única, paredes amarillas y grises) | Cocina completa, living-comedor con estufa a pellet, dormitorio matrimonial con respaldo iluminado, dormitorio con cama nido, baño con bañera e hidromasaje | Concuerdan con el mensaje. El living tiene futón y sillón de pallet (dos sofás cama) |
| **Casa de 4** (dúplex, paredes texturadas grises, escalera) | Cocina Conometal con frigobar, living con sillas de tronco y TV, baño con columna de hidromasaje, cama individual arriba | Concuerdan con el mensaje (matrimonial, individual en planta alta y un sofá cama) |
| **Áreas comunes** | Jacuzzi en deck con vista otoñal, galería con hamaca, parrilla, disco y chulengo, vista aérea con kayaks, SUP e inflables, sauna | Concuerdan con "Servicios Outdoor" y "Sector de fuegos" |

### Riesgo: posibles fotos generadas o muy retocadas
**INFERENCIA, no confirmada.** Tres imágenes tienen rasgos típicos de imágenes generadas o editadas con IA: saturación extrema, texturas de pasto y de piedra uniformes y luz poco natural.
1. **Exterior de la casa blanca** (hamaca-columpio, parrilla tipo Weber, mesa de picnic y hamaca).
2. **Sauna** con un pico rocoso de fondo, un relieve que no se parece al paisaje boscoso de Moquehue y El Verde.
3. **Vista aérea del lago** con el airtrack, el trampolín y las embarcaciones.

Además, la foto del jacuzzi bajo los árboles con la sombrilla y otra del living con sillas negras (de menor resolución) muestran mobiliario distinto al de las demás.

**Por qué importa:** la Ley 24.240, art. 8, establece que lo que se publicita obliga al oferente. Booking y Google también exigen fotos reales. Si el huésped llega y no encuentra lo que vio, el riesgo es un reclamo o una reseña de 1 estrella.
**Acción:** **[CONFIRMAR]** qué fotos son reales y sin alterar. Si alguna es una recreación, reemplazarla por una foto real o rotularla como "imagen ilustrativa".

### Selección recomendada para WhatsApp (máximo 4 o 5 por envío)
- **Primer mensaje:** 1 foto, el jacuzzi en el deck con vista otoñal. Es la que más vende.
- **Casa de 6:** el living-comedor con la estufa encendida, el dormitorio matrimonial con el respaldo iluminado, el baño con hidromasaje y la cocina.
- **Casa de 4:** el living con las sillas de tronco y la TV, la cocina con la escalera y el baño con columna de hidromasaje.
- **Entorno:** la galería con hamaca y parrilla al atardecer, y la vista aérea del lago (solo si se confirma que es real).

---

## 6. Mensajes rediseñados (listos para WhatsApp Business)

Convención: `*texto*` = negrita en WhatsApp. Lo que va entre `[ ]` lo completa quien responde.

### M0. Mensaje de bienvenida automático (WhatsApp Business → Herramientas → Mensaje de bienvenida)
```
¡Hola! 👋 Gracias por escribir a *Tierras Mágicas*, casas de montaña en Moquehue (El Verde), a 18 km de Villa Pehuenia.

Para pasarte disponibilidad y precio exacto, contanos:
1️⃣ Fecha de llegada y de salida
2️⃣ Cuántas personas son
3️⃣ Si viajan con mascota

Te respondemos enseguida 🌲
```
Adjuntar **1 foto**: el jacuzzi en el deck.

### M1. Cotización (cuando ya se tienen las fechas y la cantidad de personas)
```
¡Gracias, [Nombre]! Para el [día] [fecha] al [día] [fecha] ([N] noches, [N] personas) tenemos disponible:

🏡 *Casa de Montaña para [6/4]*
💰 *$[total]* en total ([N] noches) · precio directo, 10% menos que en Booking

✅ *Incluido sin costo extra:*
• Tina caliente (jacuzzi) para 6 y sauna
• Kayaks, stand up, airtrack e isla flotante en el lago
• Calefacción a pellets, Starlink y Smart TV con DirecTV
• Sábanas, toallas, frazadas, amenities y básicos de cocina

📍 A 100 m del lago, con vista a la cordillera.

¿Te mando fotos de la casa y cómo reservar?
```
Adjuntar 4 fotos de la casa cotizada.

**Reglas para armar la cotización (temporadas 2026-2027, precio directo = Booking − 10%):**

| Temporada | Casa para 6 · dom a jue | Casa para 6 · vie y sáb | Casa para 4 · dom a jue | Casa para 4 · vie y sáb | Mínimo de noches | Seña |
|---|---|---|---|---|---|---|
| Baja | $99.000 | $121.500 | $72.000 | $90.000 | 2 | 50% · 15% de descuento desde 4 noches |
| Media | $135.000 | $171.000 | $99.000 | $126.000 | 2 | 50% |
| Alta | $189.000 | $234.000 | $144.000 | $171.000 | 3 | 50% |
| Alta Premium | $252.000 | $306.000 | $189.000 | $225.000 | 3 (5 del 24 al 31 de dic) | 100%, no reembolsable |

*Cálculo propio a partir de `config.json`. **[CONFIRMAR]** con el dueño antes de usarlo. La temporada de cada fecha está en el calendario del panel (`/admin` → Tarifas). Si la web está publicada, el sistema hace este cálculo solo.*

**Si el grupo supera la capacidad:**
```
Si son más de [6/4], tenemos el *dormi*: una cabañita aparte para hasta 4 personas más, a $20.000 por persona por noche (usan el baño de la casa). Es uno solo, así que conviene reservarlo ya.
```

### M2. Cómo reservar (cuando el huésped dice que sí)
```
¡Genial! Para reservar:

💳 *Seña del [50/100]%: $[seña]*. El resto, al llegar.
Con la seña el precio queda congelado.

Podés pagar por:
• Transferencia: alias *kooran* · titular Ricardo Félix Bersia (BPN)
• Mercado Pago: [link de pago]

📋 *Antes de pagar, tené en cuenta:*
• Check-in desde las 15 h · check-out hasta las 10 h
• Cancelación con 15 días o más de anticipación: te devolvemos lo abonado. Con menos de 15 días se pierde la seña, o podés reprogramar para otra fecha. [En Alta Premium: no reembolsable]
• Mascotas de tamaño mediano, avisándonos antes 🐕
• No se fuma dentro de la casa
• La leña para el fogón, los asadores y el horno no está incluida; la pedís aparte

Mandanos el comprobante con tu nombre completo y DNI, y te confirmamos al momento ✅
```
Después del pago, usar la plantilla **"Confirmación"** que ya está en el panel (`/admin` → Operación).

### Respuestas rápidas (WhatsApp Business → Respuestas rápidas)

| Atajo | Texto |
|---|---|
| `/spa` | La tina caliente (jacuzzi, hasta 40 °C, para 6 personas) y el sauna para 6 con aceites esenciales están **incluidos en la tarifa**. Cuando el complejo está completo se usan por turnos que coordinamos por acá. En verano sumamos espuma y batas. |
| `/lago` | Estamos a 100 m del lago Moquehue, con vista a la cordillera. Kayaks, stand up, airtrack e isla flotante están incluidos. El chaleco es obligatorio y se firma un deslinde antes del primer uso. |
| `/fuegos` | Zona de fuegos con fogón, asadores a la estaca, disco, horno de leña envolvente, ahumador, chulengos y parrillas. La leña no está incluida: la pedís aparte por acá. |
| `/casa6` | Casa de Montaña para 6: cocina comedor con cocina a gas y horno, heladera con freezer y microondas; living con 2 sofás cama y estufa a pellets; dormitorio matrimonial; dormitorio con cama nido; baño con bañera y columna de hidromasaje; galería con hamaca paraguaya. |
| `/casa4` | Casa de Montaña para 4 (dúplex): cocina comedor con cocina a gas y horno, heladera [CONFIRMAR freezer] y microondas; living con sofá cama; dormitorio matrimonial; cama individual en planta alta; baño con columna de hidromasaje; mesa de picnic y hamaca. |
| `/dormi` | Para grupos más grandes: dormi para hasta 4 personas, $20.000 por persona por noche, con el baño de la casa alquilada. Hay uno solo. |
| `/mascotas` | Sí, aceptamos mascotas de tamaño mediano. Avisanos al reservar. |
| `/llegar` | Ruta Provincial 11, km 8,2, paraje El Verde, Moquehue (Neuquén), a 18 km de Villa Pehuenia. Mapa: https://maps.app.goo.gl/xB1kfnN3jGQaRKtX9 |
| `/cancelar` | Con 15 días o más de anticipación te devolvemos lo abonado. Con menos de 15 días se pierde lo abonado o podés reprogramar. En Alta Premium (fines de semana largos, vacaciones de invierno y Fin de Año) el pago no es reembolsable. |

---

## 7. Riesgos y supuestos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Las tarifas de `config.json` cambiaron desde oct-2026 | Cotizar mal | El dueño confirma la tabla de la sección 6 |
| Fotos generadas o retocadas | Reclamo y reseñas negativas | Confirmar cuáles son reales o reemplazarlas |
| "Acceso exclusivo" al lago | Publicidad engañosa | Confirmar o cambiar la redacción |
| Cotizar a mano | Errores de temporada o de mínimo de noches | Publicar la web y que el sistema cotice; mientras tanto, usar la tabla |
| Datos bancarios en un mensaje | Fraude con números falsos que se hacen pasar por el complejo | Mandar el alias solo desde el número oficial y pedir el comprobante con nombre y DNI |

## 8. Gate y próximos pasos

**Gate para pasar a operación:** el dueño confirma los puntos **[CONFIRMAR]**: tarifas, acceso al lago, freezer de la casa de 4, efectivo y dólares, fotos reales y si la web está en línea.

| Paso | Responsable | Entregable |
|---|---|---|
| 1. Confirmar los datos marcados | Dueño | Respuesta punto por punto |
| 2. Cargar M0 como bienvenida automática y las respuestas rápidas | Recepción | WhatsApp Business configurado |
| 3. Reemplazar las fotos dudosas | Dueño | Set de fotos reales |
| 4. Medir durante 4 semanas | Recepción | Planilla con: consultas, cotizaciones enviadas, señas cobradas, tiempo hasta la primera respuesta y motivo de pérdida |
| 5. Comparar la tasa consulta → seña con la línea base | Revenue | Ajuste de los mensajes |

**Indicadores a seguir** (no hay línea base; se fija con las primeras 4 semanas): conversión de consulta a seña, tiempo hasta la primera respuesta, porcentaje de reservas directas sobre el total y ventas del dormi.

---

## 9. Implementado: respuestas desde el panel con el cuadro tarifario

**Decisión del dueño:** manejar las respuestas con el cuadro tarifario de TM Panel Prueba.

**Dónde está:** panel → **Operación → Responder consulta de reserva**. Funciona en TM Panel Prueba, en TM Panel y en el panel web. Lo pueden usar el dueño y recepción.

| Paso | Botón | Qué arma |
|---|---|---|
| 1 | Bienvenida (pedir datos) | Pide fechas, cantidad de personas y si viajan con mascota |
| 2 | Cotizar | Para las fechas cargadas: qué cabañas están libres, el total de cada una, la temporada y la seña. El mensaje lista solo las disponibles y junta las cabañas iguales ("Cabaña 1 o Cabaña 2") |
| 3 | Cómo reservar (por cabaña) | Total, seña (50%, o 100% en Alta Premium), alias para transferir, check-in y check-out, cancelación y la regla propia de la temporada, mascotas, no fumar y leña aparte |

Después se toca **Copiar** o **Abrir en WhatsApp**. Si se carga el número del huésped, se abre directo su chat.

**Reglas que aplica solo:** el precio de cada noche según su temporada; de domingo a jueves usa el mínimo del rango y viernes y sábado el máximo; descuenta el 10% de venta directa; respeta el mínimo de noches (2, 3 o 5 en Fin de Año); cobra la seña de la temporada más alta de la estadía; aplica el 15% de descuento de temporada Baja desde 4 noches; suma el dormi si el grupo supera la capacidad; no ofrece una cabaña ocupada.

**Para cambiar precios:** se editan en **Tarifas** y las cotizaciones siguientes los usan. Ya no hay precios escritos en ningún mensaje.

**Ojo con TM Panel Prueba:** guarda los datos solo en ese teléfono. Si se cambian las tarifas ahí, no pasan a otros teléfonos ni al panel publicado. Para que todo el equipo cotice igual, el panel tiene que estar publicado (`docs/PUBLICAR-RAILWAY.md`) y todos tienen que usar TM Panel.

**Otros cambios:** dirección Ruta 11 km 8,2 en "Cómo llegar"; distribución de la Cabaña 3 tomada del mensaje de WhatsApp.

---

## 10. Datos confirmados por el dueño (12-nov-2026)

| Tema | Confirmado | Aplicado en |
|---|---|---|
| Lago (C4) | A unos 50 m, por un sendero entre bosque de ñires. Se saca "acceso exclusivo" | Cotización, "Cómo llegar", pregunta frecuente, página de pesca y app Caza&Pesca |
| Cabaña 3 | Heladera con freezer | Descripción de la cabaña |
| Pagos | Se cobra en pesos argentinos. Huéspedes del exterior pueden pagar en efectivo en dólares o pesos chilenos, a la cotización del día del BCRA | "Cómo reservar" (para el saldo al llegar), políticas, pregunta frecuente y asistente IA |
| Fotos | Son reales, con mejora de calidad de imagen y sin alterar el contenido | Se cierra el riesgo de fotos de la sección 5. Se recomienda no agregar ni quitar elementos en futuras ediciones |
| Cabañas 1 y 2 | Son idénticas | La cotización las muestra juntas ("Cabaña 1 o Cabaña 2") |
| Dirección | Ruta Provincial 11 km 8,2, confirmada con la empresa del asfalto | "Cómo llegar" |
| Distancia a Villa Pehuenia | Google Maps: 15 km, unos 20 minutos en auto (captura del dueño, saliendo desde el complejo) | Ubicación y "Cómo llegar". El mensaje original decía 18 km |
| Conectividad | Wifi mesh en todo el complejo con internet satelital Starlink de alta velocidad | Servicios, pregunta frecuente "¿Tienen wifi?" y cotización |

