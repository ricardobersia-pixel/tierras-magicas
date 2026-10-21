const $ = (s) => document.querySelector(s);
const pesos = (n) => "$" + Number(n).toLocaleString("es-AR");
const fechaLarga = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short" });
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

let info;
let busqueda;
let eleccion;

async function iniciar() {
  info = await fetch("/api/info").then((r) => r.json());
  const n = info.negocio;
  document.title = `${n.nombre} · Reservá directo`;
  document.querySelectorAll("[data-negocio]").forEach((el) => (el.textContent = n[el.dataset.negocio] || ""));
  const wa = `https://wa.me/${n.whatsapp}?text=${encodeURIComponent("Hola! Quería consultar por las cabañas.")}`;
  $("#btn-wa-header").href = wa;
  $("#btn-wa-pie").href = wa;
  $("#link-ig").href = `https://instagram.com/${n.instagram}`;
  $("#servicios").innerHTML = n.servicios.map((s) => `<li>${esc(s)}</li>`).join("");
  $("#politicas").innerHTML = n.politicas.map((s) => `<li>${esc(s)}</li>`).join("");
  $("#horarios").textContent = `Check-in desde las ${n.check_in} · Check-out hasta las ${n.check_out}`;
  $("#nota-pago").textContent = info.pagoOnline
    ? `Pagás ahora el ${n.sena_porcentaje}% con Mercado Pago y el saldo al llegar.`
    : `Te contactamos por WhatsApp para coordinar la seña (${n.sena_porcentaje}%).`;
  $("#btn-pagar").textContent = info.pagoOnline ? "Pagar seña con Mercado Pago" : "Solicitar reserva";

  $("#grilla-cabanas").innerHTML = info.cabanas
    .map(
      (c) => `<article class="cabana">
        <img src="${esc(c.foto)}" alt="${esc(c.nombre)}" loading="lazy">
        <div class="cabana-cuerpo">
          <h3>${esc(c.nombre)}</h3>
          <p>${esc(c.descripcion)}</p>
          <p class="meta">Hasta ${c.capacidad} personas · mínimo ${c.minimo_noches} noches</p>
          <p class="precio">desde <strong>${pesos(c.precio_noche)}</strong> / noche</p>
        </div>
      </article>`
    )
    .join("");

  const f = $("#buscador");
  const manana = sumar(info.hoy, 1);
  f.checkin.min = info.hoy;
  f.checkout.min = manana;
  f.checkin.addEventListener("change", () => {
    f.checkout.min = sumar(f.checkin.value, 1);
    if (!f.checkout.value || f.checkout.value <= f.checkin.value) f.checkout.value = sumar(f.checkin.value, 2);
  });

  // Enlaces del asistente: /?checkin=...&checkout=...&huespedes=...#reservar
  const q = new URLSearchParams(location.search);
  if (q.get("checkin") && q.get("checkout")) {
    f.checkin.value = q.get("checkin");
    f.checkout.value = q.get("checkout");
    f.huespedes.value = q.get("huespedes") || 2;
    buscar();
  }
}

function sumar(iso, dias) {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + dias);
  return d.toISOString().slice(0, 10);
}

async function buscar() {
  const f = $("#buscador");
  const params = new URLSearchParams({ checkin: f.checkin.value, checkout: f.checkout.value, huespedes: f.huespedes.value });
  busqueda = await fetch("/api/disponibilidad?" + params).then((r) => r.json());
  const seccion = $("#reservar");
  seccion.hidden = false;
  $("#form-reserva").hidden = true;
  if (busqueda.error) {
    $("#resumen-busqueda").textContent = busqueda.error;
    $("#resultados").innerHTML = "";
  } else {
    $("#resumen-busqueda").textContent = `${fechaLarga(busqueda.checkin)} → ${fechaLarga(busqueda.checkout)} · ${busqueda.noches} noches · ${busqueda.huespedes} huéspedes`;
    const libres = busqueda.cabanas.filter((c) => c.disponible);
    $("#resultados").innerHTML = busqueda.cabanas.length
      ? busqueda.cabanas
          .map(
            (c) => `<div class="resultado ${c.disponible ? "" : "no-disp"}">
              <div><h3>${esc(c.nombre)}</h3><p class="meta">Hasta ${c.capacidad} personas</p></div>
              ${
                c.disponible
                  ? `<div class="monto"><strong>${pesos(c.total)}</strong><span>seña ${pesos(c.sena)}</span></div>
                     <button class="boton" data-elegir="${esc(c.id)}">Reservar</button>`
                  : `<div class="monto"><span>No disponible (${esc(c.motivo)})</span></div>`
              }
            </div>`
          )
          .join("") + (libres.length ? "" : `<p>No hay cabañas libres para esas fechas. <a href="${$("#btn-wa-header").href}">Consultanos por WhatsApp</a> por fechas alternativas.</p>`)
      : `<p>No tenemos cabañas para ${busqueda.huespedes} personas. Escribinos por WhatsApp.</p>`;
  }
  seccion.scrollIntoView({ behavior: "smooth" });
}

$("#buscador").addEventListener("submit", (e) => {
  e.preventDefault();
  buscar();
});

$("#resultados").addEventListener("click", (e) => {
  const id = e.target.dataset?.elegir;
  if (!id) return;
  eleccion = busqueda.cabanas.find((c) => c.id === id);
  $("#detalle-eleccion").innerHTML = `<strong>${esc(eleccion.nombre)}</strong> · ${fechaLarga(busqueda.checkin)} → ${fechaLarga(busqueda.checkout)} · Total ${pesos(eleccion.total)} · Seña ${pesos(eleccion.sena)} · Saldo al ingresar ${pesos(eleccion.saldo)}`;
  const form = $("#form-reserva");
  form.hidden = false;
  form.scrollIntoView({ behavior: "smooth" });
  form.nombre.focus({ preventScroll: true });
});

$("#form-reserva").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  const btn = $("#btn-pagar");
  btn.disabled = true;
  $("#error-reserva").textContent = "";
  try {
    const res = await fetch("/api/reservas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cabanaId: eleccion.id, checkin: busqueda.checkin, checkout: busqueda.checkout, huespedes: busqueda.huespedes,
        nombre: f.nombre.value, email: f.email.value, telefono: f.telefono.value, notas: f.notas.value,
      }),
    }).then((r) => r.json());
    if (res.error) throw new Error(res.error);
    location.href = res.pagarEn;
  } catch (err) {
    $("#error-reserva").textContent = err.message;
    btn.disabled = false;
  }
});

// ---------- Chat ----------
const historial = [];

function pintarMensaje(rol, texto) {
  const div = document.createElement("div");
  div.className = `msj ${rol}`;
  // Texto plano con enlaces clickeables
  div.innerHTML = esc(texto).replace(/https?:\/\/[^\s)]+/g, (u) => `<a href="${u}" target="_blank" rel="noopener">${u.includes("wa.me") ? "WhatsApp" : "Abrir enlace"}</a>`).replace(/\n/g, "<br>");
  $("#chat-mensajes").append(div);
  $("#chat-mensajes").scrollTop = 1e9;
  return div;
}

$("#chat-abrir").addEventListener("click", () => {
  $("#chat").hidden = false;
  $("#chat-abrir").hidden = true;
  if (!historial.length) pintarMensaje("assistant", `¡Hola! Soy el asistente de ${info?.negocio.nombre || "las cabañas"}. Decime fechas y cantidad de personas y te cuento disponibilidad y precios.`);
  $("#chat-input").focus();
});
$("#chat-cerrar").addEventListener("click", () => {
  $("#chat").hidden = true;
  $("#chat-abrir").hidden = false;
});

$("#chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("#chat-input");
  const texto = input.value.trim();
  if (!texto) return;
  input.value = "";
  pintarMensaje("user", texto);
  historial.push({ role: "user", content: texto });
  const escribiendo = pintarMensaje("assistant escribiendo", "Escribiendo…");
  try {
    const { respuesta } = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensajes: historial }),
    }).then((r) => r.json());
    escribiendo.remove();
    pintarMensaje("assistant", respuesta);
    historial.push({ role: "assistant", content: respuesta });
  } catch {
    escribiendo.textContent = "No pude conectarme. Probá de nuevo o escribinos por WhatsApp.";
  }
});

iniciar();
