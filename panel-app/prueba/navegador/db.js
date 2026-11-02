// Reemplaza src/db.js en la app de prueba: la misma interfaz que node:sqlite (prepare/run/get/all/exec)
// sobre sql.js, con la base guardada en el teléfono (localStorage).
import initSqlJs from "sql.js/dist/sql-wasm.js";
import wasmBinary from "sql.js/dist/sql-wasm.wasm";
import { crearEsquema } from "../../../src/esquema.js";

const CLAVE = "tm-prueba-base";
let base = null;
let guardadoPendiente = false;

// Se guarda después de terminar la operación en curso: exportar en medio de una transacción la cortaría
function guardarLuego() {
  if (guardadoPendiente) return;
  guardadoPendiente = true;
  setTimeout(() => {
    guardadoPendiente = false;
    const bytes = base.export();
    let texto = "";
    for (let i = 0; i < bytes.length; i += 0x8000) texto += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    localStorage.setItem(CLAVE, btoa(texto));
  }, 0);
}

function cargarGuardada() {
  const texto = localStorage.getItem(CLAVE);
  if (!texto) return null;
  return Uint8Array.from(atob(texto), (c) => c.charCodeAt(0));
}

export async function abrirBase() {
  const SQL = await initSqlJs({ wasmBinary });
  base = new SQL.Database(cargarGuardada() || undefined);
  crearEsquema(db);
  guardarLuego();
}

export function borrarBase() {
  localStorage.removeItem(CLAVE);
}

const filas = (sql, params) => {
  const st = base.prepare(sql);
  try {
    st.bind(params);
    const resultado = [];
    while (st.step()) resultado.push(st.getAsObject());
    return resultado;
  } finally {
    st.free();
  }
};

export const db = {
  exec(sql) {
    base.exec(sql);
    guardarLuego();
  },
  prepare(sql) {
    return {
      run: (...params) => {
        base.run(sql, params);
        const changes = base.getRowsModified();
        const lastInsertRowid = base.exec("SELECT last_insert_rowid()")[0].values[0][0];
        guardarLuego();
        return { changes, lastInsertRowid };
      },
      get: (...params) => filas(sql, params)[0],
      all: (...params) => filas(sql, params),
    };
  },
};
