const $ = (s) => document.querySelector(s);
const pesos = (n) => "$" + Number(n).toLocaleString("es-AR");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const corta = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "short" });
const soloDigitos = (t) => String(t || "").replace(/\D/g, "");

function sumar(iso, dias) {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + dias);
  return d.toISOString().slice(0, 10);
}

async function api(ruta, opciones = {}) {
  const res = await fetch(ruta, { headers: { "Content-Type": "application/json" }, ...opciones });
  const datos = await res.json();
  if (!res.ok) throw new Error(datos.error || "Error");
  return datos;
}

let datos;
let desde = null;

async function cargar() {
  datos = await api("/api/admin/resumen" + (desde ? `?desde=${desde}` : ""));
  desde = datos.desde;
  const nombreCab = Object.fromEntries(datos.cabanas.map((c) => [c.id, c.nombre]));

  // KPIs
  const proximas = datos.reservas.filter((r) => r.estado === "confirmada");
  const pendientes = datos.reservas.filter((r) => r.estado === "pendiente_pago");
  const sinIcal = datos.cabanas.filter((c) => !Object.values(c.ical_configurado).some(Boolean)).length;
  $("#kpis").innerHTML = `
    <div class="kpi"><span>Reservas confirmadas próximas</span><strong>${proximas.length}</strong></div>
    <div class="kpi"><span>Pendientes de pago</span><strong>${pendientes.length}</strong></div>
    <div class="kpi"><span>Ingresos directos del mes (${datos.ingresosMes.n})</span><strong>${pesos(datos.ingresosMes.total)}</strong></div>
    <div class="kpi"><span>Tareas próximas</span><strong>${datos.tareas.length}</strong></div>
    ${!datos.pagoOnline ? `<div class="kpi alerta"><span>Mercado Pago</span><strong>No configurado (modo demo)</strong></div>` : ""}
    ${!datos.iaActiva ? `<div class="kpi alerta"><span>Asistente IA</span><strong>Sin clave de API</strong></div>` : ""}
    ${sinIcal ? `<div class="kpi alerta"><span>Calendarios Airbnb/Booking</span><strong>${sinIcal} cabaña(s) sin conectar</strong></div>` : ""}`;

  // Calendario
  const dias = Array.from({ length: 42 }, (_, i) => sumar(desde, i));
  const cab = dias
    .map((d) => {
      const dow = new Date(d + "T12:00:00Z").getUTCDay();
      return `<th class="${dow === 0 || dow === 6 ? "finde" : ""} ${d === datos.hoy ? "hoy" : ""}" title="${d}">${Number(d.slice(8))}${d.endsWith("-01") ? "<br>" + corta(d).split(" ")[1] : ""}</th>`;
    })
    .join("");
  const filas = datos.cabanas
    .map((c) => {
      const ocup = [
        ...datos.reservas.filter((r) => r.cabana_id === c.id && r.estado !== "cancelada").map((r) => ({
          desde: r.checkin, hasta: r.checkout, clase: r.estado === "confirmada" ? "web" : "pendiente", titulo: `${r.nombre} · ${r.id}`,
        })),
        ...datos.bloqueos.filter((b) => b.cabana_id === c.id).map((b) => ({ desde: b.desde, hasta: b.hasta, clase: b.origen, titulo: `${b.origen}: ${b.resumen || ""}` })),
      ];
      const celdas = dias
        .map((d) => {
          const o = ocup.find((o) => d >= o.desde && d < o.hasta);
          return o ? `<td class="${o.clase}" title="${esc(o.titulo)}"></td>` : "<td></td>";
        })
        .join("");
      return `<tr><th class="cab">${esc(c.nombre)}</th>${celdas}</tr>`;
    })
    .join("");
  $("#calendario").innerHTML = `<thead><tr><th class="cab"></th>${cab}</tr></thead><tbody>${filas}</tbody>`;

  // Tareas
  $("#tareas").innerHTML =
    datos.tareas
      .map(
        (t) => `<li class="${t.fecha < datos.hoy ? "vencida" : ""}"><input type="checkbox" data-tarea="${t.id}" aria-label="Marcar hecha">
        <div><strong>${corta(t.fecha)} · ${esc(t.tipo)}</strong> — ${esc(nombreCab[t.cabana_id])}<br>${esc(t.descripcion)}</div></li>`
      )
      .join("") || "<li>Sin tareas pendientes 🎉</li>";

  // Reservas
  $("#reservas").innerHTML =
    `<thead><tr><th>Código</th><th>Cabaña</th><th>Ingreso</th><th>Salida</th><th>Huésped</th><th>Pers.</th><th>Total</th><th>Seña</th><th>Estado</th><th></th></tr></thead><tbody>` +
    (datos.reservas
      .filter((r) => r.estado !== "cancelada")
      .map(
        (r) => `<tr>
        <td>${esc(r.id)}</td><td>${esc(nombreCab[r.cabana_id])}</td><td>${corta(r.checkin)}</td><td>${corta(r.checkout)}</td>
        <td>${esc(r.nombre)}${r.telefono ? ` · <a href="https://wa.me/${soloDigitos(r.telefono)}" target="_blank">WA</a>` : ""}${r.notas ? ` <span title="${esc(r.notas)}">📝</span>` : ""}</td>
        <td>${r.huespedes}</td><td>${pesos(r.total)}</td><td>${pesos(r.sena)}</td>
        <td><span class="estado ${r.estado}">${r.estado === "confirmada" ? "Confirmada" : "Pendiente"}</span></td>
        <td>${r.estado === "pendiente_pago" ? `<button data-accion="confirmar" data-id="${r.id}">Confirmar</button>` : ""}<button data-accion="reprogramar" data-id="${r.id}">Reprogramar</button><button data-accion="cancelar" data-id="${r.id}">Cancelar</button></td>
      </tr>`
      )
      .join("") || `<tr><td colspan="10">Sin reservas próximas</td></tr>`) +
    "</tbody>";

  // Selector de cabañas
  if (!$("#sel-cabana").options.length) $("#sel-cabana").innerHTML = datos.cabanas.map((c) => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("");

  // iCal
  $("#ical").innerHTML = datos.cabanas
    .map(
      (c) => `<div class="ical-item"><strong>${esc(c.nombre)}</strong>
      <span>Importando: <span class="chip ${c.ical_configurado.airbnb ? "on" : ""}">Airbnb ${c.ical_configurado.airbnb ? "✓" : "—"}</span>
      <span class="chip ${c.ical_configurado.booking ? "on" : ""}">Booking ${c.ical_configurado.booking ? "✓" : "—"}</span></span>
      <span>Enlace para pegar en Airbnb/Booking:</span><code>${esc(c.ical_exportar)}</code></div>`
    )
    .join("");
  $("#sync").innerHTML =
    datos.sync.map((s) => `<li class="${s.ok ? "" : "mal"}">${esc(s.fecha)} · ${esc(nombreCab[s.cabana_id])} · ${esc(s.origen)}: ${esc(s.mensaje)}</li>`).join("") ||
    "<li>Todavía no hay sincronizaciones (faltan los enlaces iCal en config.json).</li>";
}

// Navegación del calendario
$("#cal-ant").onclick = () => { desde = sumar(desde, -14); cargar(); };
$("#cal-sig").onclick = () => { desde = sumar(desde, 14); cargar(); };
$("#cal-hoy").onclick = () => { desde = null; cargar(); };

$("#tareas").addEventListener("change", async (e) => {
  if (!e.target.dataset.tarea) return;
  await api(`/api/admin/tareas/${e.target.dataset.tarea}/hecha`, { method: "POST" });
  cargar();
});

$("#reservas").addEventListener("click", async (e) => {
  const { accion, id } = e.target.dataset;
  if (!accion) return;
  if (accion === "reprogramar") {
    const r = datos.reservas.find((x) => x.id === id);
    const checkin = prompt(`Nueva fecha de ingreso para ${r.nombre} (AAAA-MM-DD):`, r.checkin);
    if (!checkin) return;
    const checkout = prompt("Nueva fecha de salida (AAAA-MM-DD):", sumar(checkin, Math.round((new Date(r.checkout) - new Date(r.checkin)) / 86400000)));
    if (!checkout) return;
    const cabanaId = prompt(`Cabaña (${datos.cabanas.map((c) => c.id).join(", ")}):`, r.cabana_id);
    if (!cabanaId) return;
    try {
      const nueva = await api(`/api/admin/reservas/${id}/reprogramar`, { method: "POST", body: JSON.stringify({ checkin, checkout, cabanaId }) });
      alert(nueva.diferencia > 0
        ? `Reprogramada. Diferencia a cobrar: ${pesos(nueva.diferencia)}. Nuevo saldo al llegar: ${pesos(nueva.total - nueva.sena)}.`
        : "Reprogramada sin diferencia: se mantiene lo abonado.");
    } catch (err) {
      alert(err.message);
    }
    return cargar();
  }
  if (accion === "cancelar" && !confirm(`¿Cancelar la reserva ${id}? Se liberan las fechas.`)) return;
  await api(`/api/admin/reservas/${id}/${accion}`, { method: "POST" });
  cargar();
});

$("#btn-sync").onclick = async (e) => {
  e.target.disabled = true;
  e.target.textContent = "Sincronizando…";
  try { await api("/api/admin/sincronizar", { method: "POST" }); } finally {
    e.target.disabled = false;
    e.target.textContent = "Sincronizar Airbnb/Booking";
    cargar();
  }
};

$("#sel-tipo").onchange = (e) => ($("#campos-reserva").hidden = e.target.value !== "reserva");

$("#form-manual").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  $("#error-manual").textContent = "";
  try {
    if (f.tipo.value === "bloqueo") {
      await api("/api/admin/bloqueos", { method: "POST", body: JSON.stringify({ cabanaId: f.cabanaId.value, desde: f.desde.value, hasta: f.hasta.value, resumen: f.notas.value }) });
    } else {
      await api("/api/admin/reservas", {
        method: "POST",
        body: JSON.stringify({ cabanaId: f.cabanaId.value, checkin: f.desde.value, checkout: f.hasta.value, huespedes: f.huespedes.value, nombre: f.nombre.value, telefono: f.telefono.value, notas: f.notas.value }),
      });
    }
    f.reset();
    cargar();
  } catch (err) {
    $("#error-manual").textContent = err.message;
  }
});

$("#form-borrador").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  const btn = f.querySelector("button");
  btn.disabled = true;
  btn.textContent = "Redactando…";
  try {
    const { respuesta } = await api("/api/admin/borrador", { method: "POST", body: JSON.stringify({ mensajes: [{ role: "user", content: f.mensaje.value }] }) });
    $("#borrador").hidden = false;
    $("#borrador-texto").value = respuesta;
    actualizarLinkWa();
  } catch (err) {
    alert(err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Redactar respuesta";
  }
});

function actualizarLinkWa() {
  const tel = soloDigitos($("#form-borrador").telefono.value);
  $("#btn-enviar-wa").href = `https://wa.me/${tel}?text=${encodeURIComponent($("#borrador-texto").value)}`;
}
$("#borrador-texto").addEventListener("input", actualizarLinkWa);
$("#form-borrador").telefono.addEventListener("input", actualizarLinkWa);
$("#btn-copiar").onclick = () => navigator.clipboard.writeText($("#borrador-texto").value);

cargar();
