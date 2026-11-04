import { Pdf } from "/pdf.js";
import { barras, barrasH, tablaDatos } from "/graficos.js";

const $ = (s) => document.querySelector(s);
const pesos = (n) => (Number(n) < 0 ? "-$" : "$") + Math.abs(Number(n)).toLocaleString("es-AR");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const corta = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "short" });
const soloDigitos = (t) => String(t || "").replace(/\D/g, "");

function sumar(iso, dias) {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + dias);
  return d.toISOString().slice(0, 10);
}

const NOMBRE_ROL = { dueno: "Dueño", recepcion: "Recepción", limpieza: "Limpieza", mantenimiento: "Mantenimiento" };
// De dónde llegó una reserva directa (Booking y Airbnb entran por su calendario)
const CANALES = { web: "Web", whatsapp: "WhatsApp", instagram: "Instagram", facebook: "Facebook", telefono: "Teléfono", email: "Email", presencial: "Presencial", otro: "Otro" };

async function api(ruta, opciones = {}) {
  const res = await fetch(ruta, { headers: { "Content-Type": "application/json" }, ...opciones });
  if (res.status === 401) {
    location.href = "/ingresar";
    throw new Error("Sesión terminada");
  }
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
  const { rol } = datos.usuario;
  $("#quien").textContent = `${datos.usuario.nombre} · ${NOMBRE_ROL[rol]}`;
  document.querySelectorAll("[data-roles]").forEach((el) => (el.hidden = !el.dataset.roles.split(" ").includes(rol)));
  // Si la pestaña que estaba abierta no corresponde al rol, vuelve a Operación
  if ($(`#vistas [data-ir="${document.body.dataset.vista}"]`)?.hidden) mostrarVista("operacion");
  if (!$("#tarea-cabana").options.length) {
    $("#tarea-cabana").innerHTML = `<option value="">General (todo el complejo)</option>` + datos.cabanas.map((c) => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("");
    $("#sel-canal").innerHTML = Object.entries(CANALES).filter(([k]) => k !== "web").map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
  }
  if (rol === "limpieza" || rol === "mantenimiento") return cargarLimpieza(nombreCab);

  // KPIs
  const proximas = datos.reservas.filter((r) => r.estado === "confirmada");
  const pendientes = datos.reservas.filter((r) => r.estado === "pendiente_pago");
  const sinIcal = datos.cabanas.filter((c) => !Object.values(c.ical_configurado).some(Boolean)).length;
  $("#kpis").innerHTML = `
    <div class="kpi"><span>Reservas confirmadas próximas</span><strong>${proximas.length}</strong></div>
    <div class="kpi"><span>Pendientes de pago</span><strong>${pendientes.length}</strong></div>
    ${datos.ingresosMes ? `<div class="kpi"><span>Ingresos directos del mes (${datos.ingresosMes.n})</span><strong>${pesos(datos.ingresosMes.total)}</strong></div>` : ""}
    <div class="kpi"><span>Tareas próximas</span><strong>${datos.tareas.length}</strong></div>
    ${!datos.pagoOnline ? `<div class="kpi alerta"><span>Mercado Pago</span><strong>No configurado (modo demo)</strong></div>` : ""}
    ${!datos.iaActiva ? `<div class="kpi alerta"><span>Asistente IA</span><strong>Sin clave de API</strong></div>` : ""}
    ${sinIcal ? `<div class="kpi alerta"><span>Calendarios Airbnb/Booking</span><strong>${sinIcal} cabaña(s) sin conectar</strong></div>` : ""}`;

  // Calendario
  pintarCalendario((c) => [
    ...datos.reservas.filter((r) => (c.id === DORMI.id ? r.adicionales > 0 : r.cabana_id === c.id) && r.estado !== "cancelada").map((r) => ({
      desde: r.checkin, hasta: r.checkout, clase: r.estado === "confirmada" ? "web" : "pendiente", titulo: `${r.nombre} · ${r.id}`,
    })),
    ...datos.bloqueos.filter((b) => b.cabana_id === c.id).map((b) => ({ desde: b.desde, hasta: b.hasta, clase: b.origen, titulo: `${b.origen}: ${b.resumen || ""}` })),
  ]);
  pintarTareas(nombreCab);

  // Reservas
  $("#reservas").innerHTML =
    `<thead><tr><th>Código</th><th>Cabaña</th><th>Ingreso</th><th>Salida</th><th>Huésped</th><th>Pers.</th><th>Total</th><th>Pagado</th><th>Estado</th><th></th></tr></thead><tbody>` +
    (datos.reservas
      .filter((r) => r.estado !== "cancelada")
      .map(
        (r) => `<tr>
        <td>${esc(r.id)}</td><td>${esc(nombreCab[r.cabana_id])}</td><td>${corta(r.checkin)}</td><td>${corta(r.checkout)}</td>
        <td>${esc(r.nombre)}${r.telefono ? ` · <a href="https://wa.me/${soloDigitos(r.telefono)}" target="_blank">WA</a>` : ""}${r.notas ? ` <span title="${esc(r.notas)}">📝</span>` : ""}</td>
        <td>${r.huespedes}${r.adicionales ? ` <small>(${r.adicionales} en dormi)</small>` : ""}</td><td>${pesos(r.total)}</td><td>${pesos(r.pagado)}${r.total > r.pagado ? ` <small>· debe ${pesos(r.total - r.pagado)}</small>` : ""}</td>
        <td><span class="estado ${r.estado}">${r.estado === "confirmada" ? "Confirmada" : "Pendiente"}</span></td>
        <td>${r.estado === "pendiente_pago" ? `<button data-accion="confirmar" data-id="${r.id}">Confirmar</button>` : ""}${r.estado === "confirmada" && r.total > r.pagado ? `<button data-accion="cobrar" data-id="${r.id}">Cobrar</button>` : ""}<button data-accion="reprogramar" data-id="${r.id}">Reprogramar</button><button data-accion="cancelar" data-id="${r.id}">Cancelar</button></td>
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
      ${c.ical_exportar ? `<span>Enlace para pegar en Airbnb/Booking:</span><code>${esc(c.ical_exportar)}</code>` : ""}</div>`
    )
    .join("");
  $("#sync").innerHTML =
    datos.sync.map((s) => `<li class="${s.ok ? "" : "mal"}">${esc(s.fecha)} · ${esc(nombreCab[s.cabana_id])} · ${esc(s.origen)}: ${esc(s.mensaje)}</li>`).join("") ||
    "<li>Todavía no hay sincronizaciones (faltan los enlaces iCal en config.json).</li>";

  if (rol === "dueno") cargarUsuarios();
}

// El dormi (personas adicionales de cualquier cabaña) se muestra como una fila más del calendario
const DORMI = { id: "__dormi", nombre: "Dormi (adicionales)" };

function pintarCalendario(ocupacionDe) {
  const dias = Array.from({ length: 42 }, (_, i) => sumar(desde, i));
  const cab = dias
    .map((d) => {
      const dow = new Date(d + "T12:00:00Z").getUTCDay();
      return `<th class="${dow === 0 || dow === 6 ? "finde" : ""} ${d === datos.hoy ? "hoy" : ""}" title="${d}">${Number(d.slice(8))}${d.endsWith("-01") ? "<br>" + corta(d).split(" ")[1] : ""}</th>`;
    })
    .join("");
  const filas = [...datos.cabanas, DORMI]
    .map((c) => {
      const ocup = ocupacionDe(c);
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
}

function pintarTareas(nombreCab) {
  $("#tareas").innerHTML =
    datos.tareas
      .map(
        (t) => `<li class="${t.fecha < datos.hoy ? "vencida" : ""}"><input type="checkbox" data-tarea="${t.id}" aria-label="Marcar hecha">
        <div><strong>${corta(t.fecha)} · ${esc(t.tipo)}</strong> — ${esc(nombreCab[t.cabana_id] || "General")}<br>${esc(t.descripcion)}</div></li>`
      )
      .join("") || "<li>Sin tareas pendientes 🎉</li>";
}

// Limpieza: ocupación sin datos de huéspedes + sus tareas
function cargarLimpieza(nombreCab) {
  pintarCalendario((c) => (c.id === DORMI.id ? datos.dormi : datos.ocupacion.filter((o) => o.cabana_id === c.id)).map((o) => ({ ...o, clase: "web", titulo: `Ocupada hasta el ${corta(o.hasta)}` })));
  pintarTareas(nombreCab);
}

async function cargarUsuarios() {
  const { usuarios, auditoria } = await api("/api/admin/usuarios");
  $("#usuarios").innerHTML = usuarios
    .map(
      (u) => `<li class="${u.activo ? "" : "inactivo"}"><div><strong>${esc(u.nombre)}</strong>${u.id === datos.usuario.id ? " (vos)" : ""}<br><span>${esc(u.email)}</span></div>
      <div><select data-rol-de="${u.id}" aria-label="Rol de ${esc(u.nombre)}">${Object.entries(NOMBRE_ROL).map(([k, v]) => `<option value="${k}" ${k === u.rol ? "selected" : ""}>${v}</option>`).join("")}</select>
      <button data-u="${u.id}" data-accion="clave">Nueva contraseña</button>
      <button data-u="${u.id}" data-accion="${u.activo ? "desactivar" : "activar"}">${u.activo ? "Desactivar" : "Activar"}</button></div></li>`
    )
    .join("");
  $("#auditoria").innerHTML =
    `<thead><tr><th>Fecha (UTC)</th><th>Usuario</th><th>Acción</th><th>Detalle</th></tr></thead><tbody>` +
    (auditoria.map((a) => `<tr><td>${esc(a.fecha)}</td><td>${esc(a.usuario)}</td><td>${esc(a.accion)}</td><td>${esc(a.detalle)}</td></tr>`).join("") ||
      `<tr><td colspan="4">Sin actividad todavía</td></tr>`) +
    "</tbody>";
}

async function cambiarUsuario(id, cambios) {
  try {
    await api(`/api/admin/usuarios/${id}`, { method: "POST", body: JSON.stringify(cambios) });
  } catch (err) {
    alert(err.message);
  }
  cargarUsuarios();
}

$("#usuarios").addEventListener("change", (e) => {
  if (e.target.dataset.rolDe) cambiarUsuario(e.target.dataset.rolDe, { rol: e.target.value });
});

$("#usuarios").addEventListener("click", (e) => {
  const { u, accion } = e.target.dataset;
  if (!u) return;
  if (accion === "clave") {
    const clave = prompt("Nueva contraseña (mín. 10 caracteres). Se cierran sus sesiones abiertas:");
    if (clave) cambiarUsuario(u, { clave });
  } else if (accion === "desactivar") {
    if (confirm("¿Desactivar este usuario? No va a poder ingresar al panel.")) cambiarUsuario(u, { activo: false });
  } else if (accion === "activar") {
    cambiarUsuario(u, { activo: true });
  }
});

$("#form-usuario").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  $("#error-usuario").textContent = "";
  try {
    await api("/api/admin/usuarios", { method: "POST", body: JSON.stringify({ nombre: f.nombre.value, rol: f.rol.value, email: f.email.value, clave: f.clave.value }) });
    f.reset();
    cargarUsuarios();
  } catch (err) {
    $("#error-usuario").textContent = err.message;
  }
});

$("#btn-salir").onclick = async () => {
  await api("/api/salir", { method: "POST" }).catch(() => {});
  location.href = "/ingresar";
};

$("#btn-clave").onclick = async () => {
  const actual = prompt("Contraseña actual:");
  if (!actual) return;
  const nueva = prompt("Nueva contraseña (mín. 10 caracteres):");
  if (!nueva) return;
  try {
    await api("/api/admin/clave", { method: "POST", body: JSON.stringify({ actual, nueva }) });
    alert("Contraseña actualizada.");
  } catch (err) {
    alert(err.message);
  }
};

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
  if (accion === "cobrar") {
    const r = datos.reservas.find((x) => x.id === id);
    await cobrar({ id: r.id, nombre: r.nombre, saldo: r.total - r.pagado, pagado: r.pagado });
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
        body: JSON.stringify({ cabanaId: f.cabanaId.value, checkin: f.desde.value, checkout: f.hasta.value, huespedes: f.huespedes.value, nombre: f.nombre.value, telefono: f.telefono.value, notas: f.notas.value, canal: f.canal.value, email: f.email.value }),
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


// ---------- Cobros (dueño y recepción) ----------

const MEDIOS = { efectivo: "Efectivo", transferencia: "Transferencia", mercadopago: "Mercado Pago", plataforma: "Plataforma" };
const CONCEPTOS = { sena: "Seña", saldo: "Saldo", total: "Pago total", extra: "Extra", ota: "Airbnb/Booking", otro: "Otro" };

async function cobrar({ id, nombre, saldo, pagado }) {
  const monto = prompt(`Cobro de ${nombre} (${id}). Monto a registrar:`, String(saldo));
  if (!monto) return;
  const medio = prompt("Medio de pago: efectivo, transferencia o mercadopago", "efectivo");
  if (!medio) return;
  try {
    await api("/api/admin/pagos", {
      method: "POST",
      body: JSON.stringify({ reservaId: id, monto: Number(String(monto).replace(/\D/g, "")), medio: medio.trim().toLowerCase().replace(/\s/g, ""), concepto: pagado ? "saldo" : "sena" }),
    });
  } catch (err) {
    alert(err.message);
  }
}

// ---------- Pestañas del dueño ----------

function mostrarVista(vista) {
  document.body.dataset.vista = vista;
  document.querySelectorAll("#vistas button").forEach((b) => b.classList.toggle("activa", b.dataset.ir === vista));
  try { localStorage.setItem("tm-vista", vista); } catch {}
  if (vista === "finanzas") cargarFinanzas();
  if (vista === "tarifas" && !tarifas) cargarTarifas();
  if (vista === "calendario") cargarMapa();
  if (vista === "turnos") cargarTurnos();
  if (vista === "respuestas") cargarRespuestas();
  if (vista === "estadisticas") cargarEstadisticas();
  if (vista === "ajustes") cargarAjustesPanel();
}
$("#vistas").addEventListener("click", (e) => e.target.dataset.ir && mostrarVista(e.target.dataset.ir));

// ---------- Finanzas ----------

const porc = (n) => (n == null ? "—" : `${String(n).replace(".", ",")}%`);
const mesActual = () => hoyLocal().slice(0, 7);
const nombreMes = (m) => new Date(m + "-15T12:00:00Z").toLocaleDateString("es-AR", { month: "short", year: "2-digit", timeZone: "UTC" });
let finanzas;

async function cargarFinanzas() {
  const mes = $("#fin-mes").value || mesActual();
  $("#fin-mes").value = mes;
  finanzas = await api(`/api/admin/finanzas?mes=${mes}`);
  const { resumen: r, flujo } = finanzas;
  const m = r.metricas;
  const kpi = (titulo, valor, nota = "", clase = "") => `<div class="kpi ${clase}"><span>${titulo}</span><strong>${valor}</strong>${nota ? `<small>${nota}</small>` : ""}</div>`;
  $("#fin-kpis").innerHTML =
    kpi("Cobrado (caja)", pesos(r.caja.cobros)) +
    kpi("Gastos", pesos(r.caja.gastos), `fijos ${pesos(m.gastos_fijos)} · variables ${pesos(m.gastos_variables)}`) +
    kpi("Resultado de caja", pesos(r.caja.neto), "", r.caja.neto >= 0 ? "bien" : "mal") +
    kpi("Ingresos del mes", pesos(m.ingresos_devengados), "por las noches del mes") +
    kpi("Ocupación", porc(m.ocupacion), `${m.noches_vendidas} de ${m.noches_disponibles} noches`) +
    kpi("Tarifa promedio (ADR)", pesos(m.adr), "ingreso por noche vendida") +
    kpi("RevPAR", pesos(m.revpar), "ingreso por noche disponible") +
    kpi("Costo por noche", pesos(m.costo_noche), "fijos ÷ noches disponibles + variables por noche vendida") +
    kpi("Ocupación de equilibrio", porc(m.ocupacion_equilibrio), m.ocupacion_equilibrio == null ? "faltan ventas o la tarifa no cubre el costo variable" : "para cubrir los gastos fijos con la tarifa promedio",
      m.ocupacion_equilibrio != null && m.ocupacion >= m.ocupacion_equilibrio ? "bien" : "mal");
  $("#fin-nota").textContent = m.otas_sin_monto ? `Hay ${m.otas_sin_monto} reserva(s) de Airbnb/Booking sin monto cargado: cuentan en la ocupación pero no en los ingresos.` : "";

  $("#fin-cabanas").innerHTML = `<thead><tr><th>Cabaña</th><th class="num">Noches</th><th class="num">Ocupación</th><th class="num">Ingresos</th></tr></thead><tbody>` +
    r.por_cabana.map((c) => `<tr><td>${esc(c.cabana)}</td><td class="num">${c.noches}</td><td class="num">${porc(c.ocupacion)}</td><td class="num">${pesos(c.ingresos)}</td></tr>`).join("") + "</tbody>";
  $("#fin-canales").innerHTML = `<thead><tr><th>Canal</th><th class="num">Noches</th><th class="num">Ingresos</th><th class="num">Comisiones</th></tr></thead><tbody>` +
    (r.por_canal.map((c) => `<tr><td>${esc(c.canal)}</td><td class="num">${c.noches}</td><td class="num">${pesos(c.ingresos)}</td><td class="num">${c.comisiones ? pesos(c.comisiones) : "—"}</td></tr>`).join("") ||
      `<tr><td colspan="4">Sin estadías en el mes</td></tr>`) + "</tbody>";

  const maximo = Math.max(1, ...flujo.map((f) => Math.abs(f.neto)));
  $("#fin-flujo").innerHTML = `<thead><tr><th>Mes</th><th class="num">Cobros</th><th class="num">Gastos</th><th class="num">Neto</th><th></th><th class="num">Acumulado</th></tr></thead><tbody>` +
    flujo.map((f) => `<tr><td>${nombreMes(f.mes)}</td><td class="num">${pesos(f.cobros)}</td><td class="num">${pesos(f.gastos)}</td><td class="num">${pesos(f.neto)}</td>
      <td><span class="barra-flujo ${f.neto < 0 ? "neg" : ""}" style="width:${Math.round((Math.abs(f.neto) / maximo) * 80)}px"></span></td><td class="num">${pesos(f.acumulado)}</td></tr>`).join("") + "</tbody>";

  $("#fin-por-cobrar").innerHTML = finanzas.por_cobrar.map((x) => `<li><span><strong>${esc(x.nombre)}</strong> · ${esc(x.cabana)} · ${corta(x.checkin)} → ${corta(x.checkout)}<br><small>Pagado ${pesos(x.pagado)} de ${pesos(x.total)}</small></span>
    <span><strong>${pesos(x.saldo)}</strong> <button data-cobrar="${esc(x.id)}">Cobrar</button></span></li>`).join("") || "<li>No hay saldos pendientes 🎉</li>";

  $("#fin-cobros").innerHTML = `<thead><tr><th>Fecha</th><th>Concepto</th><th>Medio</th><th>Reserva</th><th class="num">Monto</th><th></th></tr></thead><tbody>` +
    (r.cobros.map((p) => `<tr><td>${corta(p.fecha)}</td><td>${CONCEPTOS[p.concepto] || esc(p.concepto)}${p.nota ? ` <small>${esc(p.nota)}</small>` : ""}</td><td>${MEDIOS[p.medio] || esc(p.medio)}</td>
      <td>${p.reserva_id ? `${esc(p.reserva_id)} <small>${esc(p.huesped || "")}</small>` : ""}</td><td class="num">${pesos(p.monto)}</td>
      <td>${p.ota_id ? "" : `<button class="chico-link" data-borrar-cobro="${p.id}">Borrar</button>`}</td></tr>`).join("") || `<tr><td colspan="6">Sin cobros en el mes</td></tr>`) +
    `<tr class="total"><td colspan="4">Total</td><td class="num">${pesos(r.caja.cobros)}</td><td></td></tr></tbody>`;

  $("#fin-gastos").innerHTML = `<thead><tr><th>Fecha</th><th>Categoría</th><th>Concepto</th><th>Tipo</th><th class="num">Monto</th><th></th></tr></thead><tbody>` +
    (r.gastos.map((g) => `<tr><td>${g.mensual ? "Mensual" : corta(g.fecha)}</td><td>${esc(g.categoria)}</td><td>${esc(g.concepto)}${g.mensual ? ` <small>desde ${esc(g.fecha.slice(0, 7))}${g.hasta ? ` hasta ${esc(g.hasta)}` : ""}</small>` : ""}</td>
      <td>${g.tipo === "fijo" ? "Fijo" : "Variable"}</td><td class="num">${pesos(g.monto)}</td>
      <td>${g.mensual && !g.hasta ? `<button class="chico-link" data-baja-gasto="${g.id}">Dar de baja</button>` : ""}<button class="chico-link" data-borrar-gasto="${g.id}">Borrar</button></td></tr>`).join("") ||
      `<tr><td colspan="6">Sin gastos en el mes</td></tr>`) +
    `<tr class="total"><td colspan="4">Total</td><td class="num">${pesos(r.caja.gastos)}</td><td></td></tr></tbody>`;

  $("#fin-otas").innerHTML = `<thead><tr><th>Plataforma</th><th>Cabaña</th><th>Fechas</th><th>Neto depositado</th><th>Comisión</th><th></th></tr></thead><tbody>` +
    (r.otas.map((o) => `<tr data-ota="${o.id}"><td>${o.origen === "airbnb" ? "Airbnb" : "Booking"}${o.cancelada === 2 ? " <small>(no es reserva)</small>" : ""}</td><td>${esc(o.cabana)}</td>
      <td>${corta(o.desde)} → ${corta(o.hasta)}${o.monto_neto == null && o.cancelada !== 2 ? ' <span class="sin-monto">sin monto</span>' : ""}</td>
      <td><input type="number" min="1" name="neto" value="${o.monto_neto ?? ""}" inputmode="numeric" aria-label="Neto"></td>
      <td><input type="number" min="0" name="comision" value="${o.comision ?? ""}" inputmode="numeric" aria-label="Comisión"></td>
      <td><button class="chico-link" data-guardar-ota>Guardar</button>${o.cancelada === 2 ? "" : '<button class="chico-link" data-no-reserva>No es reserva</button>'}</td></tr>`).join("") ||
      `<tr><td colspan="6">Sin reservas de Airbnb/Booking en el mes</td></tr>`) + "</tbody>";

  // Formularios: categorías, medios y fechas por defecto
  if (!$("#sel-categoria").options.length) {
    $("#sel-categoria").innerHTML = finanzas.categorias.map((c) => `<option>${esc(c)}</option>`).join("");
    document.querySelectorAll(".sel-medio").forEach((s) => (s.innerHTML = finanzas.medios.filter((m) => m !== "plataforma").map((m) => `<option value="${m}">${MEDIOS[m]}</option>`).join("")));
  }
  const hoy = hoyLocal();
  for (const f of [$("#form-gasto"), $("#form-ingreso-extra")]) if (!f.fecha.value) f.fecha.value = hoy.startsWith(mes) ? hoy : `${mes}-01`;
}

$("#fin-mes").addEventListener("change", () => {
  $("#form-gasto").fecha.value = "";
  $("#form-ingreso-extra").fecha.value = "";
  $("#reporte").hidden = true;
  cargarFinanzas();
});

async function enviar(form, ruta, cuerpo, error) {
  $(error).textContent = "";
  try {
    await api(ruta, { method: "POST", body: JSON.stringify(cuerpo) });
    form.reset();
    cargarFinanzas();
  } catch (err) {
    $(error).textContent = err.message;
  }
}

$("#form-gasto").addEventListener("submit", (e) => {
  e.preventDefault();
  const f = e.target;
  enviar(f, "/api/admin/gastos", { fecha: f.fecha.value, categoria: f.categoria.value, concepto: f.concepto.value, monto: Number(f.monto.value), tipo: f.tipo.value, mensual: f.mensual.checked }, "#error-gasto");
});

$("#form-ingreso-extra").addEventListener("submit", (e) => {
  e.preventDefault();
  const f = e.target;
  enviar(f, "/api/admin/pagos", { fecha: f.fecha.value, concepto: f.concepto.value, medio: f.medio.value, monto: Number(f.monto.value), nota: f.nota.value }, "#error-ingreso");
});

document.querySelector('[data-vista="finanzas"]').parentElement.addEventListener("click", async (e) => {
  const d = e.target.dataset;
  try {
    if (d.cobrar) {
      const x = finanzas.por_cobrar.find((p) => p.id === d.cobrar);
      await cobrar({ id: x.id, nombre: x.nombre, saldo: x.saldo, pagado: x.pagado });
    } else if (d.borrarCobro) {
      if (!confirm("¿Borrar este cobro?")) return;
      await api(`/api/admin/pagos/${d.borrarCobro}`, { method: "DELETE" });
    } else if (d.borrarGasto) {
      if (!confirm("¿Borrar este gasto? Si es mensual, desaparece de todos los meses (para dejar de repetirlo usá «Dar de baja»).")) return;
      await api(`/api/admin/gastos/${d.borrarGasto}`, { method: "DELETE" });
    } else if (d.bajaGasto) {
      const hasta = prompt("Último mes en que se paga este gasto (AAAA-MM):", $("#fin-mes").value);
      if (!hasta) return;
      await api(`/api/admin/gastos/${d.bajaGasto}/baja`, { method: "POST", body: JSON.stringify({ hasta }) });
    } else if ("guardarOta" in d || "noReserva" in d) {
      const fila = e.target.closest("tr");
      const cuerpo = "noReserva" in d ? { noEsReserva: true } : { montoNeto: fila.querySelector("[name=neto]").value, comision: fila.querySelector("[name=comision]").value };
      await api(`/api/admin/ota/${fila.dataset.ota}`, { method: "POST", body: JSON.stringify(cuerpo) });
    } else return;
    cargarFinanzas();
  } catch (err) {
    alert(err.message);
  }
});

let reporteCsv;
$("#btn-reporte").onclick = async () => {
  reporteCsv = await api(`/api/admin/finanzas/reporte?mes=${$("#fin-mes").value}`);
  $("#reporte").hidden = false;
  $("#reporte-texto").value = reporteCsv.csv.replace(/^\uFEFF/, "");
};
$("#btn-descargar").onclick = () => guardarArchivo(reporteCsv.nombre, "text/csv", new TextEncoder().encode(reporteCsv.csv));
$("#btn-copiar-reporte").onclick = () => navigator.clipboard.writeText($("#reporte-texto").value).then(() => alert("Reporte copiado."));

// ---------- Tarifas y temporadas ----------

let tarifas;
let anioTramos = null; // año que muestra el calendario de temporadas ("todos" o AAAA)
const num = (v) => (v === "" ? "" : Number(v));

async function cargarTarifas() {
  tarifas = await api("/api/admin/tarifas");
  pintarTarifas();
}

function pintarTarifas() {
  const t = tarifas;
  $("#error-tarifas").textContent = "";
  $("#tar-estado").textContent = t.personalizadas ? `Usando tarifas editadas en el panel (última actualización: ${t.actualizado} UTC).` : "Usando las tarifas originales (config.json).";
  $("#tar-descuento").value = t.precio_directo_descuento;
  $("#tar-dormi-plazas").value = t.dormi.plazas;
  $("#tar-dormi-precio").value = t.dormi.precio_persona_noche;
  const ids = Object.keys(t.temporadas).sort((a, b) => t.temporadas[a].orden - t.temporadas[b].orden);

  $("#tar-temporadas").innerHTML = `<thead><tr><th>Nombre</th><th>Orden</th><th>Mín. noches</th><th>Seña %</th><th>Desc. desde noches</th><th>Desc. %</th><th>Política</th><th></th></tr></thead><tbody>` +
    ids.map((id) => {
      const x = t.temporadas[id];
      return `<tr data-temporada="${esc(id)}"><td><input data-c="nombre" value="${esc(x.nombre)}"></td><td><input type="number" data-c="orden" value="${x.orden}"></td>
        <td><input type="number" min="1" data-c="minimo_noches" value="${x.minimo_noches}"></td><td><input type="number" min="1" max="100" data-c="sena_porcentaje" value="${x.sena_porcentaje}"></td>
        <td><input type="number" min="1" data-c="desde_noches" value="${x.descuento?.desde_noches ?? ""}"></td><td><input type="number" min="0" max="90" data-c="porcentaje" value="${x.descuento?.porcentaje ?? ""}"></td>
        <td><textarea rows="2" data-c="politica">${esc(x.politica || "")}</textarea></td><td><button class="chico-link" data-quitar-temporada="${esc(id)}">Quitar</button></td></tr>`;
    }).join("") + "</tbody>";

  const directo = (n) => Math.round((n * (1 - (Number($("#tar-descuento").value) || 0) / 100)) / 1000) * 1000;
  $("#tar-nota-precios").textContent = `Mínimo: noches de domingo a jueves. Máximo: viernes y sábado. La web cobra ${t.precio_directo_descuento}% menos.`;
  $("#tar-precios").innerHTML = `<thead><tr><th>Cabaña</th>${ids.map((id) => `<th>${esc(t.temporadas[id].nombre)}</th>`).join("")}</tr></thead><tbody>` +
    datos.cabanas.map((c) => `<tr data-cabana="${esc(c.id)}"><td>${esc(c.nombre)}</td>${ids.map((id) => {
      const r = t.tarifas[c.id]?.[id] || {};
      return `<td><input type="number" min="1" data-t="${esc(id)}" data-m="min" value="${r.min ?? ""}" aria-label="Mínimo"><br><input type="number" min="1" data-t="${esc(id)}" data-m="max" value="${r.max ?? ""}" aria-label="Máximo">
        <br><small>web ${r.min ? pesos(directo(r.min)) : "—"} · ${r.max ? pesos(directo(r.max)) : "—"}</small></td>`;
    }).join("")}</tr>`).join("") + "</tbody>";

  const anios = [...new Set(t.calendario.map((x) => x.desde.slice(0, 4)))].sort();
  const elegido = anioTramos || (anios.includes(new Date().getFullYear() + "") ? new Date().getFullYear() + "" : anios[0]);
  $("#tar-anio").innerHTML = ["todos", ...anios].map((a) => `<option value="${a}" ${a === elegido ? "selected" : ""}>${a === "todos" ? "Todos" : a}</option>`).join("");
  const opciones = (sel) => ids.map((id) => `<option value="${esc(id)}" ${id === sel ? "selected" : ""}>${esc(t.temporadas[id].nombre)}</option>`).join("");
  $("#tar-calendario").innerHTML = `<thead><tr><th>Desde</th><th>Hasta</th><th>Temporada</th><th>Mín. noches</th><th>Motivo</th><th></th></tr></thead><tbody>` +
    t.calendario.map((x, i) => (elegido !== "todos" && !x.desde.startsWith(elegido) && !x.hasta.startsWith(elegido) ? "" :
      `<tr data-tramo="${i}"><td><input type="date" data-c="desde" value="${x.desde}"></td><td><input type="date" data-c="hasta" value="${x.hasta}"></td>
       <td><select data-c="temporada">${opciones(x.temporada)}</select></td><td><input type="number" min="1" data-c="minimo_noches" value="${x.minimo_noches ?? ""}" placeholder="temporada"></td>
       <td><input data-c="motivo" value="${esc(x.motivo || "")}"></td><td><button class="chico-link" data-quitar-tramo="${i}">Quitar</button></td></tr>`)).join("") + "</tbody>";

  if (!$("#previa-cabana").options.length) $("#previa-cabana").innerHTML = datos.cabanas.map((c) => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("");
}

// Pasa lo editado en pantalla al objeto tarifas (sin guardar)
function leerTarifas() {
  const t = tarifas;
  t.precio_directo_descuento = num($("#tar-descuento").value);
  t.dormi = { plazas: num($("#tar-dormi-plazas").value), precio_persona_noche: num($("#tar-dormi-precio").value) };
  document.querySelectorAll("#tar-temporadas tr[data-temporada]").forEach((fila) => {
    const x = t.temporadas[fila.dataset.temporada];
    const v = (c) => fila.querySelector(`[data-c="${c}"]`).value;
    Object.assign(x, { nombre: v("nombre"), orden: num(v("orden")), minimo_noches: num(v("minimo_noches")), sena_porcentaje: num(v("sena_porcentaje")), politica: v("politica") });
    x.descuento = v("desde_noches") || v("porcentaje") ? { desde_noches: num(v("desde_noches")), porcentaje: num(v("porcentaje")) } : undefined;
  });
  document.querySelectorAll("#tar-precios tr[data-cabana]").forEach((fila) => {
    const c = (t.tarifas[fila.dataset.cabana] = t.tarifas[fila.dataset.cabana] || {});
    fila.querySelectorAll("input").forEach((i) => ((c[i.dataset.t] = c[i.dataset.t] || {})[i.dataset.m] = num(i.value)));
  });
  document.querySelectorAll("#tar-calendario tr[data-tramo]").forEach((fila) => {
    const x = t.calendario[Number(fila.dataset.tramo)];
    const v = (c) => fila.querySelector(`[data-c="${c}"]`).value;
    Object.assign(x, { desde: v("desde"), hasta: v("hasta"), temporada: v("temporada"), motivo: v("motivo") });
    if (v("minimo_noches")) x.minimo_noches = num(v("minimo_noches"));
    else delete x.minimo_noches;
  });
  return t;
}

const sinPersonalizadas = ({ precio_directo_descuento, dormi, temporadas, calendario, tarifas: precios }) => ({ precio_directo_descuento, dormi, temporadas, calendario, tarifas: precios });

$("#tar-anio").onchange = () => {
  leerTarifas();
  anioTramos = $("#tar-anio").value;
  pintarTarifas();
};
$("#btn-agregar-tramo").onclick = () => {
  leerTarifas();
  const ultimo = [...tarifas.calendario].sort((a, b) => (a.hasta < b.hasta ? 1 : -1))[0];
  const desde = ultimo ? sumar(ultimo.hasta, 1) : new Date().toISOString().slice(0, 10);
  tarifas.calendario.push({ desde, hasta: desde, temporada: Object.keys(tarifas.temporadas)[0], motivo: "" });
  anioTramos = desde.slice(0, 4);
  pintarTarifas();
};
$("#btn-agregar-temporada").onclick = () => {
  const nombre = prompt("Nombre de la nueva temporada:");
  if (!nombre) return;
  leerTarifas();
  const id = nombre.toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || `t${Date.now()}`;
  if (tarifas.temporadas[id]) return alert("Ya existe una temporada con ese nombre.");
  tarifas.temporadas[id] = { nombre, orden: Object.keys(tarifas.temporadas).length + 1, minimo_noches: 2, sena_porcentaje: 50, politica: "" };
  pintarTarifas();
};
document.querySelector('[data-vista="tarifas"]').parentElement.addEventListener("click", (e) => {
  const d = e.target.dataset;
  if (d.quitarTramo !== undefined) {
    leerTarifas();
    tarifas.calendario.splice(Number(d.quitarTramo), 1);
    pintarTarifas();
  } else if (d.quitarTemporada) {
    leerTarifas();
    if (tarifas.calendario.some((x) => x.temporada === d.quitarTemporada)) return alert("Esa temporada se usa en el calendario: cambiá esos tramos primero.");
    delete tarifas.temporadas[d.quitarTemporada];
    for (const c of Object.values(tarifas.tarifas)) delete c[d.quitarTemporada];
    pintarTarifas();
  }
});
$("#btn-guardar-tarifas").onclick = async () => {
  $("#error-tarifas").textContent = "";
  try {
    tarifas = await api("/api/admin/tarifas", { method: "POST", body: JSON.stringify(sinPersonalizadas(leerTarifas())) });
    pintarTarifas();
    alert("Tarifas guardadas. Ya se usan en la web, el asistente y las reservas nuevas.");
  } catch (err) {
    $("#error-tarifas").textContent = err.message;
    $("#error-tarifas").scrollIntoView({ block: "center" });
  }
};
$("#btn-descartar-tarifas").onclick = () => confirm("¿Descartar los cambios sin guardar?") && cargarTarifas();
$("#btn-restablecer-tarifas").onclick = async () => {
  if (!confirm("¿Volver a las tarifas y el calendario originales? Se pierden los cambios hechos en el panel.")) return;
  tarifas = await api("/api/admin/tarifas/restablecer", { method: "POST" });
  pintarTarifas();
};
$("#form-previa").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  try {
    const c = await api("/api/admin/tarifas/cotizar", {
      method: "POST",
      body: JSON.stringify({ cabanaId: f.cabanaId.value, checkin: f.checkin.value, checkout: f.checkout.value, huespedes: f.huespedes.value, tarifas: sinPersonalizadas(leerTarifas()) }),
    });
    const temporadas = Object.entries(c.noches_por_temporada).map(([id, n]) => `${n} ${tarifas.temporadas[id]?.nombre || id}`).join(", ");
    $("#previa-resultado").innerHTML = `<strong>${pesos(c.total)}</strong> por ${c.noches} noches (${esc(temporadas)}) · rige ${esc(c.temporada_nombre)}, mínimo ${c.minimo_noches} noches · ` +
      `${c.sena >= c.total ? "pago total anticipado" : `seña ${c.sena_porcentaje}%: ${pesos(c.sena)}`}${c.adicionales ? ` · incluye ${c.adicionales} en el dormi (${pesos(c.total_adicionales)})` : ""}`;
  } catch (err) {
    $("#previa-resultado").textContent = err.message;
  }
});


// ---------- Fechas en la hora de Argentina (no en UTC) ----------
function hoyLocal() {
  return datos?.hoy || new Date().toLocaleDateString("en-CA", { timeZone: "America/Argentina/Buenos_Aires" });
}
const mesMas = (mes, n) => {
  let [a, m] = mes.split("-").map(Number);
  m += n;
  while (m < 1) { m += 12; a--; }
  while (m > 12) { m -= 12; a++; }
  return `${a}-${String(m).padStart(2, "0")}`;
};
const nombreMesLargo = (mes) => new Date(mes + "-15T12:00:00Z").toLocaleDateString("es-AR", { month: "long", year: "numeric", timeZone: "UTC" });
const fechaLarga = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
const nochesEntre = (a, b) => Math.round((new Date(b + "T12:00:00Z") - new Date(a + "T12:00:00Z")) / 864e5);

// ---------- Guardar o compartir archivos (PDF, CSV) ----------
// En la app de Android lo hace el teléfono (TMNativo); en el navegador, una descarga normal.
function guardarArchivo(nombre, tipo, bytes) {
  if (window.TMNativo?.guardarArchivo) {
    let binario = "";
    for (let i = 0; i < bytes.length; i += 0x8000) binario += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    window.TMNativo.guardarArchivo(nombre, tipo, btoa(binario));
    return;
  }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([bytes], { type: tipo }));
  a.download = nombre;
  document.body.append(a);
  a.click();
  setTimeout(() => (URL.revokeObjectURL(a.href), a.remove()), 1000);
}

// ---------- Tareas: reportar un arreglo (todos los roles) ----------
$("#form-tarea").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  $("#error-tarea").textContent = "";
  try {
    await api("/api/admin/tareas", { method: "POST", body: JSON.stringify({ cabanaId: f.cabanaId.value, fecha: f.fecha.value, tipo: f.tipo.value, descripcion: f.descripcion.value }) });
    f.reset();
    cargar();
  } catch (err) {
    $("#error-tarea").textContent = err.message;
  }
});

// ---------- Calendario mensual (mapa de asientos) ----------
let mapaMes = null;
let mapa;
const DIAS_SEMANA = ["L", "M", "M", "J", "V", "S", "D"];
const claseOcupacion = (o) => (o.tipo === "reserva" ? (o.estado === "confirmada" ? "web" : "pendiente") : o.tipo === "bloqueo" ? (o.origen === "manual" ? "manual" : o.origen) : o.tipo);
const etiquetaOcupacion = (o) => {
  if (o.tipo === "reserva") return o.nombre || (o.estado === "confirmada" ? "Ocupada" : "Pendiente");
  if (o.tipo === "airbnb" || o.tipo === "booking") return o.tipo === "airbnb" ? "Airbnb" : "Booking";
  return o.origen === "manual" || !o.origen ? (o.resumen || "Bloqueada") : `Cerrada en ${o.origen === "airbnb" ? "Airbnb" : "Booking"}`;
};

async function cargarMapa() {
  mapaMes = mapaMes || hoyLocal().slice(0, 7);
  mapa = await api(`/api/admin/calendario?mes=${mapaMes}`);
  $("#mapa-titulo").textContent = `Calendario · ${nombreMesLargo(mapaMes)}`;
  $("#mapa-nota").textContent = mapa.con_datos ? "Tocá un día ocupado (o pasá el mouse) para ver la reserva." : "Días ocupados del mes (sin datos de los huéspedes).";
  const [anio, numMes] = mapaMes.split("-").map(Number);
  const dias = new Date(Date.UTC(anio, numMes, 0)).getUTCDate(); // día 0 del mes siguiente = último del mes
  const primerDia = (new Date(mapaMes + "-01T12:00:00Z").getUTCDay() + 6) % 7; // lunes = 0
  $("#mapa").innerHTML = mapa.filas.map((fila, f) => {
    const vendidas = Array.from({ length: dias }, (_, d) => `${mapaMes}-${String(d + 1).padStart(2, "0")}`).filter((dia) => fila.ocupaciones.some((o) => dia >= o.desde && dia < o.hasta)).length;
    const celdas = Array.from({ length: dias }, (_, d) => {
      const dia = `${mapaMes}-${String(d + 1).padStart(2, "0")}`;
      const i = fila.ocupaciones.findIndex((o) => dia >= o.desde && dia < o.hasta);
      const o = fila.ocupaciones[i];
      const clases = ["asiento", dia === mapa.hoy ? "hoy" : "", dia < mapa.hoy ? "pasado" : ""];
      if (!o) return `<div class="${clases.join(" ")}" aria-label="${d + 1}: libre"><span class="num">${d + 1}</span></div>`;
      clases.push("ocupado", claseOcupacion(o), o.desde === dia ? "entra" : "");
      const quien = etiquetaOcupacion(o);
      // En el casillero va el apellido ("Pérez, Juan" → "Pérez"); el nombre completo, en el globo y el detalle
      const corto = o.tipo === "reserva" && o.nombre ? o.nombre.split(",")[0].trim() : quien;
      return `<button class="${clases.join(" ")}" data-fila="${f}" data-oc="${i}" aria-label="${d + 1}: ${esc(quien)}"><span class="num">${d + 1}</span><span class="ocupante">${esc(corto)}</span></button>`;
    });
    return `<div class="mapa-fila"><h3>${esc(fila.nombre)} <small>${vendidas} de ${dias} noches ocupadas${fila.capacidad ? ` · hasta ${fila.capacidad} pers.` : ""}</small></h3>
      <div class="asientos">${DIAS_SEMANA.map((d) => `<span class="dia-semana">${d}</span>`).join("")}${'<div class="asiento vacio"></div>'.repeat(primerDia)}${celdas.join("")}</div></div>`;
  }).join("");
}

function resumenOcupacion(o, fila) {
  const fechas = `${fechaLarga(o.desde)} → ${fechaLarga(o.hasta)} · ${nochesEntre(o.desde, o.hasta)} noches`;
  if (o.tipo === "reserva" && o.nombre) return `<strong>${esc(o.nombre)}</strong><br>${fechas}<br>${o.huespedes} pers.${o.adicionales ? ` (${o.adicionales} en el dormi)` : ""} · ${esc(CANALES[o.canal] || o.canal)}<br>Total ${pesos(o.total)} · pagado ${pesos(o.pagado)}`;
  return `<strong>${esc(etiquetaOcupacion(o))}</strong> · ${esc(fila.nombre)}<br>${fechas}`;
}

function detalleOcupacion(o, fila) {
  const fechas = `<dt>Ingreso</dt><dd>${fechaLarga(o.desde)}</dd><dt>Salida</dt><dd>${fechaLarga(o.hasta)} (${nochesEntre(o.desde, o.hasta)} noches)</dd>`;
  if (o.tipo === "reserva" && o.nombre) {
    const saldo = o.total - o.pagado;
    const tel = soloDigitos(o.telefono);
    return `<h3>${esc(o.nombre)}</h3><dl>
      <dt>Reserva</dt><dd>${esc(o.id)} · ${o.estado === "confirmada" ? "Confirmada" : "Pendiente de pago"}</dd>
      <dt>Cabaña</dt><dd>${esc(o.cabana || fila.nombre)}</dd>${fechas}
      <dt>Huéspedes</dt><dd>${o.huespedes}${o.adicionales ? ` (${o.adicionales} en el dormi)` : ""}</dd>
      <dt>Llegó por</dt><dd>${esc(CANALES[o.canal] || o.canal)}</dd>
      <dt>Total</dt><dd>${pesos(o.total)}</dd><dt>Pagado</dt><dd>${pesos(o.pagado)}${saldo > 0 ? ` · <strong>debe ${pesos(saldo)}</strong>` : " · al día"}</dd>
      ${o.telefono ? `<dt>Teléfono</dt><dd>${esc(o.telefono)}</dd>` : ""}${o.email ? `<dt>Email</dt><dd>${esc(o.email)}</dd>` : ""}
      ${o.notas ? `<dt>Notas</dt><dd>${esc(o.notas)}</dd>` : ""}</dl>
      <div class="acciones">${tel ? `<a class="boton chico" href="https://wa.me/${tel}" target="_blank" rel="noopener">WhatsApp</a><a class="boton chico sec" href="tel:+${tel}">Llamar</a>` : ""}
      ${saldo > 0 && o.estado === "confirmada" ? `<button class="boton chico sec" data-cobrar-detalle="${esc(o.id)}">Cobrar</button>` : ""}</div>`;
  }
  if ((o.tipo === "airbnb" || o.tipo === "booking") && "monto_neto" in o) {
    return `<h3>Reserva de ${o.tipo === "airbnb" ? "Airbnb" : "Booking"}</h3><dl><dt>Cabaña</dt><dd>${esc(fila.nombre)}</dd>${fechas}
      <dt>Neto depositado</dt><dd>${o.monto_neto ? pesos(o.monto_neto) : "Sin cargar (Finanzas → Airbnb y Booking)"}</dd>${o.comision ? `<dt>Comisión</dt><dd>${pesos(o.comision)}</dd>` : ""}
      ${o.resumen ? `<dt>Detalle</dt><dd>${esc(o.resumen)}</dd>` : ""}</dl><p class="nota">Los datos del huésped están en ${o.tipo === "airbnb" ? "Airbnb" : "Booking"}.</p>`;
  }
  return `<h3>${esc(etiquetaOcupacion(o))}</h3><dl><dt>Cabaña</dt><dd>${esc(fila.nombre)}</dd>${fechas}</dl>`;
}

$("#mapa").addEventListener("click", async (e) => {
  const celda = e.target.closest("[data-oc]");
  if (!celda) return;
  const fila = mapa.filas[celda.dataset.fila];
  const o = fila.ocupaciones[celda.dataset.oc];
  $("#globo").hidden = true;
  $("#detalle-contenido").innerHTML = detalleOcupacion(o, fila);
  $("#detalle").showModal();
});
$("#detalle").addEventListener("click", async (e) => {
  const id = e.target.dataset.cobrarDetalle;
  if (!id) return;
  const o = mapa.filas.flatMap((f) => f.ocupaciones).find((x) => x.id === id);
  $("#detalle").close();
  await cobrar({ id, nombre: o.nombre, saldo: o.total - o.pagado, pagado: o.pagado });
  cargarMapa();
  cargar();
});
// Al pasar el mouse: globo con el resumen
$("#mapa").addEventListener("pointermove", (e) => {
  const celda = e.target.closest("[data-oc]");
  const globo = $("#globo");
  if (!celda || e.pointerType === "touch") return (globo.hidden = true);
  const fila = mapa.filas[celda.dataset.fila];
  globo.innerHTML = resumenOcupacion(fila.ocupaciones[celda.dataset.oc], fila);
  globo.hidden = false;
  globo.style.left = Math.min(e.clientX + 14, innerWidth - globo.offsetWidth - 8) + "px";
  globo.style.top = Math.min(e.clientY + 14, innerHeight - globo.offsetHeight - 8) + "px";
});
$("#mapa").addEventListener("pointerleave", () => ($("#globo").hidden = true));
$("#mapa-ant").onclick = () => { mapaMes = mesMas(mapaMes, -1); cargarMapa(); };
$("#mapa-sig").onclick = () => { mapaMes = mesMas(mapaMes, 1); cargarMapa(); };
$("#mapa-hoy").onclick = () => { mapaMes = null; cargarMapa(); };

// ---------- Turnos ----------
let agenda;
async function cargarTurnos() {
  const f = $("#turno-fecha");
  if (!f.value) f.value = hoyLocal();
  agenda = await api(`/api/admin/turnos?fecha=${f.value}`);
  const gestion = ["dueno", "recepcion"].includes(datos?.usuario?.rol);
  $("#turnos").innerHTML = agenda.recursos.map((r) => `<div class="recurso"><h3>${esc(r.nombre)} <small>${r.cantidad} a la vez · turnos de ${r.duracion_min} min</small></h3>
    <div class="horarios">${r.horarios.map((h) => `<div class="horario ${h.libres <= 0 ? "lleno" : ""}"><strong>${h.hora}</strong>
      ${h.turnos.map((t) => `<span class="chip">${esc(t.nombre || t.cabana || "Turno")}${t.cabana && t.nombre ? ` · ${esc(t.cabana)}` : ""}${t.cantidad > 1 ? ` ×${t.cantidad}` : ""}${t.nota ? ` · ${esc(t.nota)}` : ""}${gestion ? `<button data-borrar-turno="${t.id}" aria-label="Quitar turno">×</button>` : ""}</span>`).join("")}
      ${h.libres > 0 ? (gestion ? `<button class="dar" data-recurso="${esc(r.id)}" data-hora="${h.hora}">+ ${h.libres < r.cantidad ? `${h.libres} libre(s)` : "Libre"}</button>` : `<small>${h.libres} libre(s)</small>`) : "<small>Completo</small>"}
    </div>`).join("")}</div></div>`).join("");
}
async function reservasDelDia(fecha) {
  // Reservas que están alojadas ese día (para asignar el turno a una cabaña)
  const { filas } = await api(`/api/admin/calendario?mes=${fecha.slice(0, 7)}`);
  return filas.filter((f) => f.id !== "dormi").flatMap((f) => f.ocupaciones.filter((o) => o.tipo === "reserva" && o.id && fecha >= o.desde && fecha < o.hasta).map((o) => ({ ...o, cabana: f.nombre })));
}
$("#turnos").addEventListener("click", async (e) => {
  const d = e.target.dataset;
  if (d.borrarTurno) {
    if (!confirm("¿Quitar este turno?")) return;
    try { await api(`/api/admin/turnos/${d.borrarTurno}`, { method: "DELETE" }); } catch (err) { alert(err.message); }
    return cargarTurnos();
  }
  if (!d.recurso) return;
  const f = $("#form-turno");
  const r = agenda.recursos.find((x) => x.id === d.recurso);
  f.recurso.value = d.recurso;
  f.hora.value = d.hora;
  f.cantidad.max = r.horarios.find((h) => h.hora === d.hora).libres;
  $("#turno-titulo").textContent = `${r.nombre} · ${fechaLarga(agenda.fecha)} a las ${d.hora}`;
  const alojados = await reservasDelDia(agenda.fecha);
  $("#turno-reserva").innerHTML = `<option value="">— Sin reserva (escribí el nombre) —</option>` +
    alojados.map((o) => `<option value="${esc(o.id)}">${esc(o.cabana)} · ${esc(o.nombre)}</option>`).join("");
  f.hidden = false;
  f.scrollIntoView({ block: "center", behavior: "smooth" });
});
$("#form-turno").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  $("#error-turno").textContent = "";
  try {
    await api("/api/admin/turnos", { method: "POST", body: JSON.stringify({ fecha: agenda.fecha, hora: f.hora.value, recurso: f.recurso.value, reservaId: f.reservaId.value, nombre: f.nombre.value, cantidad: f.cantidad.value, nota: f.nota.value }) });
    f.reset();
    f.hidden = true;
    cargarTurnos();
  } catch (err) {
    $("#error-turno").textContent = err.message;
  }
});
$("#turno-cancelar").onclick = () => ($("#form-turno").hidden = true);
$("#turno-fecha").onchange = () => { $("#form-turno").hidden = true; cargarTurnos(); };
$("#turno-ant").onclick = () => { $("#turno-fecha").value = sumar($("#turno-fecha").value || hoyLocal(), -1); $("#turno-fecha").onchange(); };
$("#turno-sig").onclick = () => { $("#turno-fecha").value = sumar($("#turno-fecha").value || hoyLocal(), 1); $("#turno-fecha").onchange(); };

// ---------- Respuestas para clientes ----------
let respuestas = [];
async function cargarRespuestas() {
  respuestas = (await api("/api/admin/respuestas")).valor;
  pintarRespuestas();
}
function pintarRespuestas() {
  const q = $("#buscar-respuesta").value.trim().toLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "");
  const sinAcentos = (t) => t.toLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "");
  const lista = respuestas.map((x, i) => ({ ...x, i })).filter((x) => !q || sinAcentos(x.p + " " + x.r).includes(q));
  $("#respuestas").innerHTML = lista.map((x) => `<div class="respuesta"><strong>${esc(x.p)}</strong><p>${esc(x.r)}</p>
    <div class="acciones"><button class="boton chico sec" data-copiar-respuesta="${x.i}">Copiar</button><a class="boton chico" href="https://wa.me/?text=${encodeURIComponent(x.r)}" target="_blank" rel="noopener">Enviar por WhatsApp</a></div></div>`).join("") ||
    `<p class="nota">No hay respuestas que coincidan. ${datos?.usuario?.rol === "dueno" ? "Podés agregarla con «Editar»." : "Pedile al dueño que la agregue."}</p>`;
}
$("#buscar-respuesta").addEventListener("input", pintarRespuestas);
$("#respuestas").addEventListener("click", (e) => {
  const i = e.target.dataset.copiarRespuesta;
  if (i === undefined) return;
  navigator.clipboard.writeText(respuestas[i].r).then(() => (e.target.textContent = "¡Copiada!"));
});
function pintarEditorRespuestas() {
  $("#lista-editable").innerHTML = respuestas.map((x, i) => `<div class="editable-pregunta" data-i="${i}">
    <label>Pregunta<input data-c="p" value="${esc(x.p)}"></label><label>Respuesta<textarea data-c="r" rows="3">${esc(x.r)}</textarea></label>
    <button class="quitar" data-quitar-respuesta="${i}">Quitar</button></div>`).join("");
}
const leerEditorRespuestas = () => [...document.querySelectorAll(".editable-pregunta")].map((d) => ({ p: d.querySelector('[data-c="p"]').value, r: d.querySelector('[data-c="r"]').value }));
$("#btn-editar-respuestas").onclick = () => {
  $("#editor-respuestas").hidden = false;
  $("#respuestas").hidden = true;
  pintarEditorRespuestas();
};
$("#btn-cancelar-respuestas").onclick = () => { $("#editor-respuestas").hidden = true; $("#respuestas").hidden = false; };
$("#btn-agregar-respuesta").onclick = () => { respuestas = leerEditorRespuestas(); respuestas.unshift({ p: "", r: "" }); pintarEditorRespuestas(); };
$("#lista-editable").addEventListener("click", (e) => {
  if (e.target.dataset.quitarRespuesta === undefined) return;
  respuestas = leerEditorRespuestas();
  respuestas.splice(Number(e.target.dataset.quitarRespuesta), 1);
  pintarEditorRespuestas();
});
$("#btn-guardar-respuestas").onclick = async () => {
  $("#error-respuestas").textContent = "";
  try {
    respuestas = (await api("/api/admin/respuestas", { method: "POST", body: JSON.stringify({ preguntas: leerEditorRespuestas() }) })).valor;
    $("#editor-respuestas").hidden = true;
    $("#respuestas").hidden = false;
    pintarRespuestas();
  } catch (err) {
    $("#error-respuestas").textContent = err.message;
  }
};

// ---------- Estadísticas ----------
let estadisticasDatos;
const compacto = (n) => (Math.abs(n) >= 1e6 ? `$${(n / 1e6).toLocaleString("es-AR", { maximumFractionDigits: 1 })}M` : Math.abs(n) >= 1e3 ? `$${Math.round(n / 1e3)}k` : pesos(n));
const mesCorto = (m) => new Date(m + "-15T12:00:00Z").toLocaleDateString("es-AR", { month: "short", timeZone: "UTC" }).replace(".", "");

async function cargarEstadisticas() {
  const hasta = $("#est-hasta").value || hoyLocal().slice(0, 7);
  $("#est-hasta").value = hasta;
  const e = (estadisticasDatos = await api(`/api/admin/estadisticas?hasta=${hasta}`));
  const ingresos = e.serie.reduce((s, m) => s + m.ingresos, 0);
  const noches = e.serie.reduce((s, m) => s + m.noches, 0);
  const ocupacionProm = Math.round((e.serie.reduce((s, m) => s + m.ocupacion, 0) / e.serie.length) * 10) / 10;
  const kpi = (t, v, n = "") => `<div class="kpi"><span>${t}</span><strong>${v}</strong>${n ? `<small>${n}</small>` : ""}</div>`;
  $("#est-kpis").innerHTML = kpi("Ingresos 12 meses", pesos(ingresos)) + kpi("Ocupación promedio", porc(ocupacionProm)) +
    kpi("Tarifa promedio (ADR)", pesos(noches ? Math.round(ingresos / noches) : 0)) + kpi("Noches vendidas", noches) +
    kpi("Reservas directas", e.reservas.confirmadas, `${e.reservas.canceladas} canceladas`) + kpi("Estadía promedio", `${String(e.reservas.estadia_promedio).replace(".", ",")} noches`) +
    kpi("Anticipación promedio", `${String(e.reservas.anticipacion_promedio).replace(".", ",")} días`) + kpi("Huéspedes por reserva", String(e.reservas.huespedes_promedio).replace(".", ","), `${e.reservas.con_dormi} con dormi`);
  const serie = (campo, formato, titulo) => barras(e.serie.map((m) => ({ etiqueta: mesCorto(m.mes), valor: m[campo], detalle: `${nombreMesLargo(m.mes)}: ${formato(m[campo])}` })), { formato, titulo }) +
    tablaDatos(["Mes", titulo], e.serie.map((m) => [nombreMesLargo(m.mes), formato(m[campo])]));
  $("#g-ocupacion").innerHTML = serie("ocupacion", porc, "Ocupación");
  $("#g-ingresos").innerHTML = serie("ingresos", compacto, "Ingresos");
  $("#g-adr").innerHTML = serie("adr", compacto, "ADR");
  $("#g-canales").innerHTML = barrasH(e.canales.map((c) => ({ etiqueta: c.canal, valor: c.ingresos, detalle: `${c.canal}: ${pesos(c.ingresos)} · ${c.noches} noches${c.comisiones ? ` · comisiones ${pesos(c.comisiones)}` : ""}` })), { formato: compacto, titulo: "Ingresos por canal" }) +
    tablaDatos(["Canal", "Noches", "Ingresos", "Comisiones"], e.canales.map((c) => [c.canal, c.noches, pesos(c.ingresos), c.comisiones ? pesos(c.comisiones) : "—"]));
  $("#g-cabanas").innerHTML = barrasH(e.cabanas.map((c) => ({ etiqueta: c.cabana, valor: c.ocupacion, detalle: `${c.cabana}: ${porc(c.ocupacion)} · ${c.noches} noches · ${pesos(c.ingresos)}` })), { formato: porc, titulo: "Ocupación por cabaña" }) +
    tablaDatos(["Cabaña", "Noches", "Ocupación", "Ingresos"], e.cabanas.map((c) => [c.cabana, c.noches, porc(c.ocupacion), pesos(c.ingresos)]));
  $("#g-anticipacion").innerHTML = barrasH(e.reservas.anticipacion.map((a) => ({ etiqueta: a.tramo, valor: a.reservas })), { titulo: "Anticipación" });
  $("#g-dias").innerHTML = barrasH(e.reservas.por_dia_ingreso.map((d) => ({ etiqueta: d.dia, valor: d.reservas })), { titulo: "Día de llegada" });
  $("#g-origen").innerHTML = barrasH(e.reservas.por_canal.map((c) => ({ etiqueta: c.canal, valor: c.reservas })), { titulo: "Reservas por canal" });
  $("#g-turnos").innerHTML = barrasH(e.turnos.map((t) => ({ etiqueta: t.recurso, valor: t.turnos, detalle: `${t.recurso}: ${t.turnos} turnos (${t.unidades} usos)` })), { titulo: "Turnos por recurso" });
}
$("#est-hasta").onchange = cargarEstadisticas;

// ---------- Informes PDF ----------
const generado = () => `Tierras Mágicas · generado el ${new Date().toLocaleDateString("es-AR")} por ${datos?.usuario?.nombre || ""}`;

$("#btn-pdf-mes").onclick = async () => {
  const mes = $("#fin-mes").value || hoyLocal().slice(0, 7);
  const { resumen: r, flujo, por_cobrar } = await api(`/api/admin/finanzas?mes=${mes}`);
  const m = r.metricas;
  const doc = new Pdf({ titulo: `Informe ${mes}`, pie: generado() });
  doc.titulo1(`Informe mensual · ${nombreMesLargo(mes)}`, "Cabañas Tierras Mágicas · Villa Pehuenia - Moquehue");
  doc.indicadores([
    ["Cobrado (caja)", pesos(r.caja.cobros)], ["Gastos", pesos(r.caja.gastos)], ["Resultado de caja", pesos(r.caja.neto)], ["Ingresos del mes (devengados)", pesos(m.ingresos_devengados)],
    ["Ocupación", `${porc(m.ocupacion)} (${m.noches_vendidas} de ${m.noches_disponibles} noches)`], ["Tarifa promedio (ADR)", pesos(m.adr)], ["RevPAR", pesos(m.revpar)],
    ["Costo por noche", pesos(m.costo_noche)], ["Ocupación de equilibrio", porc(m.ocupacion_equilibrio)], ["Gastos fijos / variables", `${pesos(m.gastos_fijos)} / ${pesos(m.gastos_variables)}`],
  ]);
  if (m.otas_sin_monto) doc.parrafo(`Atención: ${m.otas_sin_monto} reserva(s) de Airbnb/Booking sin monto cargado; cuentan en la ocupación pero no en los ingresos.`);
  doc.titulo2("Por cabaña");
  doc.tabla([{ titulo: "Cabaña", ancho: 0.4 }, { titulo: "Noches", ancho: 0.2, derecha: true }, { titulo: "Ocupación", ancho: 0.2, derecha: true }, { titulo: "Ingresos", ancho: 0.2, derecha: true }],
    r.por_cabana.map((c) => [c.cabana, c.noches, porc(c.ocupacion), pesos(c.ingresos)]));
  doc.titulo2("Por canal");
  doc.tabla([{ titulo: "Canal", ancho: 0.4 }, { titulo: "Noches", ancho: 0.2, derecha: true }, { titulo: "Ingresos", ancho: 0.2, derecha: true }, { titulo: "Comisiones", ancho: 0.2, derecha: true }],
    r.por_canal.length ? r.por_canal.map((c) => [c.canal, c.noches, pesos(c.ingresos), c.comisiones ? pesos(c.comisiones) : "-"]) : [["Sin estadías en el mes", "", "", ""]]);
  doc.titulo2("Flujo de caja de 12 meses");
  doc.barras(flujo.map((f) => ({ etiqueta: mesCorto(f.mes), valor: Math.max(0, f.cobros) })), { formato: compacto, alto: 100 });
  doc.tabla([{ titulo: "Mes", ancho: 0.2 }, { titulo: "Cobros", ancho: 0.2, derecha: true }, { titulo: "Gastos", ancho: 0.2, derecha: true }, { titulo: "Neto", ancho: 0.2, derecha: true }, { titulo: "Acumulado", ancho: 0.2, derecha: true }],
    flujo.map((f) => [nombreMesLargo(f.mes), pesos(f.cobros), pesos(f.gastos), pesos(f.neto), pesos(f.acumulado)]));
  doc.titulo2("Cobros del mes");
  doc.tabla([{ titulo: "Fecha", ancho: 0.13 }, { titulo: "Concepto", ancho: 0.17 }, { titulo: "Medio", ancho: 0.17 }, { titulo: "Reserva / detalle", ancho: 0.35 }, { titulo: "Monto", ancho: 0.18, derecha: true }],
    [...r.cobros.map((p) => [corta(p.fecha), CONCEPTOS[p.concepto] || p.concepto, MEDIOS[p.medio] || p.medio, [p.reserva_id, p.huesped, p.nota].filter(Boolean).join(" · "), pesos(p.monto)]), ["Total", "", "", "", pesos(r.caja.cobros)]], { totalEnNegrita: true });
  doc.titulo2("Gastos del mes");
  doc.tabla([{ titulo: "Fecha", ancho: 0.13 }, { titulo: "Categoría", ancho: 0.3 }, { titulo: "Concepto", ancho: 0.27 }, { titulo: "Tipo", ancho: 0.12 }, { titulo: "Monto", ancho: 0.18, derecha: true }],
    [...r.gastos.map((g) => [g.mensual ? "Mensual" : corta(g.fecha), g.categoria, g.concepto, g.tipo === "fijo" ? "Fijo" : "Variable", pesos(g.monto)]), ["Total", "", "", "", pesos(r.caja.gastos)]], { totalEnNegrita: true });
  if (por_cobrar.length) {
    doc.titulo2("Saldos por cobrar");
    doc.tabla([{ titulo: "Huésped", ancho: 0.32 }, { titulo: "Cabaña", ancho: 0.18 }, { titulo: "Fechas", ancho: 0.22 }, { titulo: "Pagado", ancho: 0.14, derecha: true }, { titulo: "Saldo", ancho: 0.14, derecha: true }],
      por_cobrar.map((x) => [x.nombre, x.cabana, `${corta(x.checkin)} - ${corta(x.checkout)}`, pesos(x.pagado), pesos(x.saldo)]));
  }
  guardarArchivo(`informe-tierras-magicas-${mes}.pdf`, "application/pdf", doc.bytes());
};

$("#btn-pdf-est").onclick = async () => {
  const e = estadisticasDatos || (await api(`/api/admin/estadisticas?hasta=${$("#est-hasta").value || hoyLocal().slice(0, 7)}`));
  const doc = new Pdf({ titulo: `Estadísticas ${e.desde} a ${e.hasta}`, pie: generado() });
  const ingresos = e.serie.reduce((s, m) => s + m.ingresos, 0);
  const noches = e.serie.reduce((s, m) => s + m.noches, 0);
  doc.titulo1("Estadísticas de 12 meses", `${nombreMesLargo(e.desde)} a ${nombreMesLargo(e.hasta)} · Cabañas Tierras Mágicas`);
  doc.indicadores([
    ["Ingresos", pesos(ingresos)], ["Noches vendidas", String(noches)],
    ["Ocupación promedio", porc(Math.round((e.serie.reduce((s, m) => s + m.ocupacion, 0) / e.serie.length) * 10) / 10)], ["Tarifa promedio (ADR)", pesos(noches ? Math.round(ingresos / noches) : 0)],
    ["Reservas directas confirmadas", `${e.reservas.confirmadas} (${e.reservas.canceladas} canceladas)`], ["Estadía promedio", `${String(e.reservas.estadia_promedio).replace(".", ",")} noches`],
    ["Anticipación promedio", `${String(e.reservas.anticipacion_promedio).replace(".", ",")} días`], ["Reservas con dormi", String(e.reservas.con_dormi)],
  ]);
  doc.titulo2("Ocupación por mes");
  doc.barras(e.serie.map((m) => ({ etiqueta: mesCorto(m.mes), valor: m.ocupacion })), { formato: porc });
  doc.titulo2("Ingresos por mes");
  doc.barras(e.serie.map((m) => ({ etiqueta: mesCorto(m.mes), valor: m.ingresos })), { formato: compacto });
  doc.tabla([{ titulo: "Mes", ancho: 0.22 }, { titulo: "Ocupación", ancho: 0.13, derecha: true }, { titulo: "Noches", ancho: 0.11, derecha: true }, { titulo: "Ingresos", ancho: 0.18, derecha: true }, { titulo: "ADR", ancho: 0.18, derecha: true }, { titulo: "RevPAR", ancho: 0.18, derecha: true }],
    e.serie.map((m) => [nombreMesLargo(m.mes), porc(m.ocupacion), m.noches, pesos(m.ingresos), pesos(m.adr), pesos(m.revpar)]));
  doc.titulo2("Por canal");
  doc.tabla([{ titulo: "Canal", ancho: 0.4 }, { titulo: "Noches", ancho: 0.2, derecha: true }, { titulo: "Ingresos", ancho: 0.2, derecha: true }, { titulo: "Comisiones", ancho: 0.2, derecha: true }],
    e.canales.map((c) => [c.canal, c.noches, pesos(c.ingresos), c.comisiones ? pesos(c.comisiones) : "-"]));
  doc.titulo2("Por cabaña");
  doc.tabla([{ titulo: "Cabaña", ancho: 0.4 }, { titulo: "Noches", ancho: 0.2, derecha: true }, { titulo: "Ocupación", ancho: 0.2, derecha: true }, { titulo: "Ingresos", ancho: 0.2, derecha: true }],
    e.cabanas.map((c) => [c.cabana, c.noches, porc(c.ocupacion), pesos(c.ingresos)]));
  doc.titulo2("Reservas directas");
  doc.tabla([{ titulo: "Anticipación", ancho: 0.5 }, { titulo: "Reservas", ancho: 0.5, derecha: true }], e.reservas.anticipacion.map((a) => [a.tramo, a.reservas]));
  doc.tabla([{ titulo: "Día de llegada", ancho: 0.5 }, { titulo: "Reservas", ancho: 0.5, derecha: true }], e.reservas.por_dia_ingreso.map((d) => [d.dia, d.reservas]));
  doc.tabla([{ titulo: "Llegaron por", ancho: 0.5 }, { titulo: "Reservas", ancho: 0.5, derecha: true }], e.reservas.por_canal.length ? e.reservas.por_canal.map((c) => [c.canal, c.reservas]) : [["Sin reservas directas", ""]]);
  doc.titulo2("Uso de jacuzzi, sauna y equipos");
  doc.tabla([{ titulo: "Recurso", ancho: 0.5 }, { titulo: "Turnos", ancho: 0.25, derecha: true }, { titulo: "Usos", ancho: 0.25, derecha: true }], e.turnos.map((t) => [t.recurso, t.turnos, t.unidades]));
  guardarArchivo(`estadisticas-tierras-magicas-${e.hasta}.pdf`, "application/pdf", doc.bytes());
};

// ---------- Ajustes: calendarios de Airbnb/Booking y recursos de turnos ----------
let canales;
let recursosEdit;
async function cargarAjustesPanel() {
  [canales, recursosEdit] = await Promise.all([api("/api/admin/ajustes/canales"), api("/api/admin/ajustes/recursos")]);
  $("#canales").innerHTML = datos.cabanas.map((c) => {
    const v = canales.valor[c.id] || {};
    return `<div class="canal-cabana" data-cabana="${esc(c.id)}"><strong>${esc(c.nombre)}</strong>
      <label>Calendario exportado de Airbnb (enlace .ics)<input data-origen="airbnb" value="${esc(v.airbnb || "")}" placeholder="https://www.airbnb.com/calendar/ical/....ics" inputmode="url"></label>
      <label>Calendario exportado de Booking (enlace .ics)<input data-origen="booking" value="${esc(v.booking || "")}" placeholder="https://admin.booking.com/hotel/hoteladmin/ical.html?t=..." inputmode="url"></label>
      ${c.ical_exportar ? `<span class="nota">Para pegar en Airbnb y Booking (importar):</span><code>${esc(c.ical_exportar)}</code>` : ""}</div>`;
  }).join("");
  pintarRecursos();
}
function pintarRecursos() {
  $("#recursos").innerHTML = `<thead><tr><th>Nombre</th><th>Cantidad</th><th>Duración (min)</th><th>Desde</th><th>Hasta</th><th></th></tr></thead><tbody>` +
    recursosEdit.valor.map((r, i) => `<tr data-i="${i}" data-id="${esc(r.id || "")}"><td><input data-c="nombre" value="${esc(r.nombre)}"></td><td><input type="number" min="1" data-c="cantidad" value="${r.cantidad}"></td>
      <td><input type="number" min="15" step="15" data-c="duracion_min" value="${r.duracion_min}"></td><td><input type="time" data-c="desde" value="${r.desde}"></td><td><input type="time" data-c="hasta" value="${r.hasta}"></td>
      <td><button class="chico-link" data-quitar-recurso="${i}">Quitar</button></td></tr>`).join("") + "</tbody>";
}
const leerRecursos = () => [...document.querySelectorAll("#recursos tr[data-i]")].map((f) => {
  const v = (c) => f.querySelector(`[data-c="${c}"]`).value;
  return { id: f.dataset.id, nombre: v("nombre"), cantidad: Number(v("cantidad")), duracion_min: Number(v("duracion_min")), desde: v("desde"), hasta: v("hasta") };
});
$("#btn-guardar-canales").onclick = async () => {
  $("#error-canales").textContent = "";
  const valor = Object.fromEntries([...document.querySelectorAll(".canal-cabana")].map((d) => [d.dataset.cabana,
    { airbnb: d.querySelector('[data-origen="airbnb"]').value, booking: d.querySelector('[data-origen="booking"]').value }]));
  try {
    canales = await api("/api/admin/ajustes/canales", { method: "POST", body: JSON.stringify({ valor }) });
    await api("/api/admin/sincronizar", { method: "POST" }).catch(() => {});
    await cargar();
    alert("Enlaces guardados. Se sincroniza ahora y después cada 15 minutos.");
  } catch (err) {
    $("#error-canales").textContent = err.message;
  }
};
$("#btn-sync-ajustes").onclick = async (e) => {
  e.target.disabled = true;
  try { await api("/api/admin/sincronizar", { method: "POST" }); } finally { e.target.disabled = false; cargar(); }
};
$("#btn-agregar-recurso").onclick = () => {
  recursosEdit.valor = leerRecursos();
  recursosEdit.valor.push({ id: "", nombre: "", cantidad: 1, duracion_min: 60, desde: "10:00", hasta: "20:00" });
  pintarRecursos();
};
$("#recursos").addEventListener("click", (e) => {
  if (e.target.dataset.quitarRecurso === undefined) return;
  recursosEdit.valor = leerRecursos();
  recursosEdit.valor.splice(Number(e.target.dataset.quitarRecurso), 1);
  pintarRecursos();
});
$("#btn-guardar-recursos").onclick = async () => {
  $("#error-recursos").textContent = "";
  try {
    recursosEdit = await api("/api/admin/ajustes/recursos", { method: "POST", body: JSON.stringify({ valor: leerRecursos() }) });
    pintarRecursos();
    alert("Guardado. Los turnos nuevos usan estos horarios.");
  } catch (err) {
    $("#error-recursos").textContent = err.message;
  }
};

// Vista inicial: la última que se usó (se carga cuando ya se conoce el rol)
try { document.body.dataset.vista = localStorage.getItem("tm-vista") || "operacion"; } catch { document.body.dataset.vista = "operacion"; }

cargar().then(() => mostrarVista(document.body.dataset.vista));

// Instalable como app (PWA)
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
