# Auditoría del Welcome Book: Tierras Mágicas (v1)

**Documento auditado:** `Welcome_Tierras_Magicas.pdf`, 21 páginas, formato móvil 280 × 595 pt, hecho en Canva (metadato de título: `MODELO 1.pdf`, 28/08/2026).
**Contra qué se comparó:** `config.json` del sistema de reservas (datos que carga el dueño), los links que tiene el PDF y fuentes públicas.
**Fecha:** 11/11/2026 · **Fase:** PLC-10 Operación y Mejora · **Perfil líder:** Hospitalidad (con Documentación y Riesgos)

Cada hallazgo está marcado como:
- **HECHO:** se ve en el PDF o en el sistema.
- **INFERENCIA:** es una deducción razonada, sin confirmar.
- **CONFIRMAR:** lo tiene que verificar el dueño.

---

## 1. Resumen ejecutivo

El Welcome Book tiene una buena base. Usa la identidad verde de la marca, la navegación por íconos, links a Google Maps en cada comercio y lugar, links de WhatsApp para avisar la llegada y la salida, y un link directo a la reseña de Google.

Antes de volver a enviarlo hay que resolver **6 problemas críticos**:

| # | Problema | Riesgo |
|---|---|---|
| C1 | La ubicación no coincide: el PDF dice "RP 11 **Km 8**" y el sistema dice "a **18 km** de Villa Pehuenia". Además hay **dos links distintos** de Google Maps para la propiedad | El huésped se pierde y hay reclamos al llegar |
| C2 | Jacuzzi y sauna: el PDF dice "turno siempre, 1 h de uso" y el sistema dice "turno solo con alta demanda, jacuzzi 2 h" | Hay conflictos entre huéspedes y promesas incumplidas |
| C3 | Mascotas: el PDF dice "gatos y perros pequeños o medianos" y el sistema dice "mascotas de tamaño mediano" | Se puede rechazar a un huésped después de haberlo aceptado |
| C4 | Los teléfonos de emergencia y servicios no tienen link `tel:` y varios no pudieron verificarse (ver §4) | Si un número está mal, la seguridad del huésped queda en riesgo |
| C5 | Quedó texto de plantilla en la página 12 (Los Radales): "Proporciona información sobre el restaurante o recomienda algún plato tipi" | Se ve poco profesional |
| C6 | Faltan contenidos de seguridad: kayak/SUP (el chaleco es obligatorio y se firma un deslinde), monóxido de carbono, fuego en temporada de incendios y uso de la calefacción a pellets | Responsabilidad civil y seguridad de los huéspedes |

---

## 2. Hallazgos por página

| Pág. | Sección | Hallazgo | Tipo | Corrección |
|---|---|---|---|---|
| 1 | Portada | Dice "Haz clic en los íconos" en tuteo; el resto del libro usa voseo | HECHO | "Tocá un ícono" |
| 1 | Portada | Las etiquetas "INSTRUCCIONES DE DIRECCIÓN" y "ANÁLISIS" son traducciones literales | HECHO | "Cómo llegar" y "Tu opinión" |
| 1 | Portada | El botón "Contacto" hace una llamada (`tel:`). Muchos huéspedes prefieren escribir por WhatsApp | HECHO | Que lleve a la pág. de Contacto o abra WhatsApp |
| 2–21 | Barra de íconos | **Los 12 íconos del encabezado no tienen link en ninguna página interior** (0 links internos). Solo la portada tiene 12 links internos | HECHO | Vincular cada ícono a su página y agregar "⌂ Inicio" |
| 2 | Bienvenida | El texto es bueno. Falta presentar a los anfitriones y decir qué incluye la estadía | HECHO | Agregar "Qué incluye tu estadía" (tina, sauna, kayaks, SUP, airtrack, isla flotante, pellets, Starlink) |
| 3 | Check-in | El pedido de avisar el horario de llegada **está escrito dos veces** con casi las mismas palabras | HECHO | Dejarlo una sola vez y agregar cómo es la recepción (quién recibe, llaves, estacionamiento) |
| 3 | Check-in | No está el procedimiento de llegada: quién entrega las llaves y qué pasa si llegás después de las 21 h | HECHO (no figura) | Completar (CONFIRMAR el procedimiento real) |
| 4 | Check-out | Está bien. Falta una lista corta de salida (basura, vajilla, estufas, llaves) | HECHO | Agregar una checklist de 5 ítems |
| 5 | Ubicación | Muestra la foto de stock de un teléfono con **un mapa de Nueva York** | HECHO | Reemplazarla por una foto del acceso o un mapa real |
| 5 | Ubicación | Dice "RP 11 **Km 8**". El sistema dice "a **18 km** de Villa Pehuenia". Los directorios ubican el paraje El Verde en el Km 7,3–7,5 de la RP 11 | HECHO (conflicto) + INFERENCIA (lo más probable es que "18 km" esté mal o se mida desde otro punto) | CONFIRMAR el kilometraje y unificar |
| 5 | Ubicación | El link del PDF es `maps.app.goo.gl/i2TjF3py2UejgSnt6` y el del sistema es `maps.app.goo.gl/xB1kfnN3jGQaRKtX9` | HECHO | Usar **un solo** link oficial |
| 5 | Ubicación | El Plus Code `3PX5+HJ` y las coordenadas GPS (-38.901, -71.290) **coinciden entre sí** (decodificados dan -38.9011, -71.2909) | HECHO (verificado con cálculo) | Dejarlo como está. Se actualizó `config.json`, que tenía -38.92, -71.28 aproximados |
| 5 | Ubicación | Faltan el estado del camino (ripio), la nieve y las cadenas en invierno, y la señal de celular | HECHO (no figura) | Agregar "Antes de viajar" |
| 6 | Reglas | Dice "Respetá los horarios de silencio", **pero no dice cuáles son** | HECHO | Indicar el horario (CONFIRMAR, p. ej. 23:00–08:00) |
| 6 | Reglas | Las reglas del sauna y el jacuzzi contradicen la pág. 8 y el sistema (ver C2) | HECHO | Unificar |
| 6 | Reglas | Faltan las reglas de equipos acuáticos, fuego, menores y capacidad máxima | HECHO | Agregar |
| 7 | Wi-Fi | La contraseña publicada es **débil y predecible** (siglas de la marca + números consecutivos; no se reproduce acá). El PDF circula por WhatsApp y puede reenviarse | HECHO + INFERENCIA | Cambiarla por una robusta y rotarla por temporada. Aclarar que es Starlink satelital |
| 8 | FAQ | Dice "jacuzzi 5 h y sauna 3 h para calentar, 1 h de uso". El sistema tiene turnos de jacuzzi de **120 min** (10–23 h) y de sauna de 60 min (10–22 h) | HECHO (conflicto) | CONFIRMAR la duración real del turno y unificar |
| 8 | FAQ | Mascotas (ver C3) | HECHO | Unificar con la política del sistema |
| 9 | FAQ | **La página está numerada "8" otra vez** (debería ser 9) | HECHO | Renumerar |
| 9 | FAQ | Dice "Te recomendamos seguir las indicaciones indicadas" (redundante) | HECHO | Reescribir |
| 10–11 | Comercios | Hay errores de acentos: "Verduleria", "Polleria", "Alimentos Vegetarianos y Vegano" | HECHO | "Verdulería", "Pollería", "Alimentos vegetarianos y veganos" |
| 10–11 | Comercios | No hay horarios ni medios de pago. Es clave en temporada baja | HECHO | Agregar "Horarios reducidos en temporada baja: consultá antes de ir" |
| 12 | Comer | **Quedó texto de plantilla** en Los Radales (ver C5) | HECHO | Reemplazarlo por una descripción real |
| 13 | Comer | "Comidas en hora feliz" (La Familia) no se entiende. "Maddy Té y Restó- Especialidad…" tiene errores de espaciado y mayúsculas | HECHO | Reescribir |
| 14 | Comer | Los textos de Drumlin y Mandra están **copiados en primera persona del comercio** ("En nuestro bar podés…", "nuestras cervezas") | HECHO | Reescribirlos en tercera persona. Además, "primer BrewPub de Villa Pehuenia" es una afirmación de ese comercio sin verificar |
| 14 | Comer | "Cerveceria" sin tilde | HECHO | "Cervecería" |
| 15–16 | Lugares | Algunos nombres hay que verificarlos ("Circuito de las 5 Lagunas", "Mirador del Ciprés") | CONFIRMAR | Revisar contra la Oficina de Turismo |
| 15–16 | Lugares | No hay distancias, tiempos ni dificultad | HECHO | Agregar km o tiempo aproximado desde la cabaña |
| 17 | Movilidad | "**Ol**nformación turística" tiene un error de tipeo | HECHO | "Información turística" |
| 17 | Movilidad | **Ningún teléfono tiene link** `tel:` ni WhatsApp | HECHO (0 links) | Vincular todos |
| 17 | Movilidad | "Taxi Moquehue +54 9 2942 555-028" usa el prefijo 555, típico de números ficticios | INFERENCIA | CONFIRMAR antes de publicar |
| 18 | Contacto | Los números de emergencia no tienen link `tel:`. No figura el **911** ni la ubicación del Hospital Villa Pehuenia | HECHO | Ver §4 |
| 18 | Contacto | No figuran el email ni el teléfono alternativo, que sí están en el sistema | HECHO | Agregarlos |
| 19 | Combustible | **La página no tiene ningún link**, aunque dice "📍 Cómo llegar" cuatro veces | HECHO | Vincular |
| 19 | Combustible | El título "Estación de Servicios y Talleres" está repetido. Los formatos de teléfono no son uniformes (+54 299 / +54 2942 sin el 9) | HECHO | Unificar el formato `+54 9 2942 …` (CONFIRMAR cuáles son fijos) |
| 20 | Opinión | El texto "**Si disfrutaste** tu estadía, te invitamos a compartir…" pide reseña solo a los huéspedes conformes (*review gating*), una práctica que Google desalienta | INFERENCIA con fuentes (§5) | Pedir la reseña a todos: "Contanos cómo fue tu estadía" |
| 20 | Opinión | Las 5 estrellas son decorativas y parecen un formulario | HECHO | Convertirlas en un botón con link o quitarlas |
| 21 | Cierre | Usa una **foto de stock** de una persona que no es del equipo | HECHO | Usar una foto real de los anfitriones o de las cabañas |
| 21 | Cierre | Dice "Síguenos" en tuteo (el resto usa voseo) y escribe "Tierras Magicas" sin tilde | HECHO | "Seguinos" y "Tierras Mágicas" |

---

## 3. Diseño y usabilidad

| Aspecto | Estado actual | Recomendación |
|---|---|---|
| Tipografías | Mezcla de 4 o más familias (Montserrat, Arial, una display y una script) | Usar 2: una display para títulos y una sans para el texto |
| Texto justificado | Genera "ríos" de espacios en pantallas angostas | Alinear a la izquierda |
| Tamaño de letra | En las págs. 12–14 y 17 queda por debajo de unos 9 pt efectivos | Mínimo 11 pt para el texto |
| Contraste | El verde #4A7A0F sobre crema #E8E2D8 es aceptable para títulos. El texto chico en verde claro (pág. 18) queda bajo | Usar texto oscuro y reservar el verde para títulos |
| Navegación | Hay 12 íconos sin link en cada página interior | Vincularlos y agregar "Inicio" |
| Metadatos del PDF | El título es "MODELO 1.pdf" | Al exportar, ponerle de título "Welcome Book · Tierras Mágicas" |
| Peso | Pesa 4,4 MB y se puede reenviar por WhatsApp | Está bien. Exportar con imágenes comprimidas |
| Lenguaje | Mezcla voseo y tuteo | Usar voseo rioplatense en todo el libro |

---

## 4. Teléfonos: estado de verificación

**HECHO:** los números nacionales de Argentina son 101 (policía), 100 (bomberos) y 107 (emergencias médicas).

**NO VERIFICADO:** ninguno de los números locales del PDF pudo confirmarse en una fuente oficial durante esta auditoría. Un directorio turístico público ([interpatagonia](https://www.interpatagonia.com/villapehuenia/serviciosvarios.html)) muestra otros números:

| Servicio | Número en el PDF | Número en interpatagonia (sin confirmar) |
|---|---|---|
| Comisaría | +54 9 2942 647210 | +54 2942 498002 (Comisaría 47) |
| Defensa Civil | +54 9 2942 664068 | +54 2942 469061 |
| Municipalidad | — | 02942-498044 (guía de trámites municipal) |
| Hospital Pehuenia | +54 9 2942 498091 | La dirección figura como Michay s/n |

**Acción obligatoria:** antes de reimprimir, llamar a cada número de emergencia y de servicio. Registrar la fecha de verificación en el pie de la página ("Verificado: mm/aaaa").

---

## 5. Fuentes externas consultadas

- Directorio de servicios de Villa Pehuenia/Moquehue: <https://www.interpatagonia.com/villapehuenia/serviciosvarios.html>
- Guía de trámites de alojamiento de la Municipalidad de Villa Pehuenia (teléfono municipal): <https://www.villapehuenia.gob.ar/images/turismo/documentacion-habilitaciones/Guia_de_Tramites_Servicios_Turisticos_NUEVO_Alojamiento.pdf>
- Ubicación del paraje El Verde (RP 11 Km 7,3–7,5) según directorios de alojamiento: <https://www.interpatagonia.com/villapehuenia/alojamientos.html>
- *Review gating* y la política de Google: <https://www.seroundtable.com/google-removes-maps-review-gating-policy-34002.html>, <https://www.reviewtrackers.com/?p=28814>. **Advertencia:** la redacción oficial de Google cambió en 2022 y estas fuentes son de terceros. Lo más seguro es pedir la reseña a todos los huéspedes por igual.

---

## 6. Decisiones que tiene que tomar el dueño (gate para publicar la v2)

| # | Decisión | Opciones |
|---|---|---|
| D1 | Kilometraje y link oficial de Maps | Km 8 o 18 km. Link `i2Tj…` o `xB1k…` |
| D2 | Política de jacuzzi y sauna | Turno siempre o solo con demanda. Duración de 1 h o 2 h |
| D3 | Política de mascotas | Tamaños y especies aceptadas |
| D4 | Horario de silencio | p. ej. 23:00–08:00 |
| D5 | Procedimiento de llegada | Recepción en persona, caja de llaves o llegada tarde |
| D6 | Nueva contraseña de Wi-Fi | — |
| D7 | Teléfonos verificados | Llamado de verificación, con fecha |

**Gate:** la v2 se publica cuando D1 a D7 están resueltas y en la versión borrador no queda ninguna marca ⚠️.
**Siguiente acción:** el dueño completa D1 a D7, se cargan los datos en Canva (o en la versión web) y se exporta la v2.
