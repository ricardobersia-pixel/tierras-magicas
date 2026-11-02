// App de prueba: el panel funciona sin servidor. Atiende en el teléfono los pedidos a /api/…
// que hacen admin.js e ingresar.html, con la lógica del servidor y una base SQLite local.
import { abrirBase, borrarBase } from "./navegador/db.js";

const fetchOriginal = window.fetch.bind(window);
const listo = abrirBase()
  .then(() => import("./api.js"))
  .then((api) => (api.cargarDatosDePrueba(), api));

window.fetch = async (recurso, opciones = {}) => {
  const url = new URL(typeof recurso === "string" ? recurso : recurso.url, location.href);
  if (url.origin !== location.origin || !url.pathname.startsWith("/api/")) return fetchOriginal(recurso, opciones);
  const api = await listo;
  const cuerpo = opciones.body ? JSON.parse(opciones.body) : undefined;
  const { estado, cuerpo: respuesta } = api.atender((opciones.method || "GET").toUpperCase(), url, cuerpo);
  return new Response(JSON.stringify(respuesta), { status: estado, headers: { "Content-Type": "application/json" } });
};

function restablecer() {
  if (!confirm("¿Borrar todos los datos de prueba (reservas, usuarios, tareas) y volver a empezar?")) return;
  borrarBase();
  localStorage.removeItem("tm-prueba-sesion");
  location.replace("/ingresar.html");
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

document.addEventListener("DOMContentLoaded", async () => {
  const aviso = document.createElement("div");
  aviso.className = "aviso-prueba";
  aviso.innerHTML = `<span><strong>Versión de prueba</strong> · los datos quedan solo en este teléfono</span>`;
  const boton = document.createElement("button");
  boton.textContent = "Restablecer";
  boton.onclick = restablecer;
  aviso.append(boton);
  document.body.prepend(aviso);

  // En la pantalla de ingreso: los usuarios de prueba, tocando uno se completan email y contraseña
  const form = document.getElementById("form-ingreso");
  if (form) {
    const api = await listo;
    const lista = document.createElement("div");
    lista.className = "usuarios-prueba";
    lista.innerHTML = `<p class="nota">Usuarios de prueba (contraseña <code>${esc(api.CLAVE_PRUEBA)}</code>). Tocá uno para completar:</p>` +
      api.USUARIOS_PRUEBA.map((u) => `<button type="button" class="boton chico sec" data-email="${esc(u.email)}">${esc(u.nombre)}</button>`).join("");
    lista.addEventListener("click", (e) => {
      if (!e.target.dataset.email) return;
      form.email.value = e.target.dataset.email;
      form.clave.value = api.CLAVE_PRUEBA;
    });
    form.after(lista);
  }
});
