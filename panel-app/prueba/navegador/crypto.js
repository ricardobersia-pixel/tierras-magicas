// Reemplaza node:crypto en la app de prueba con lo que usan src/reservas.js y src/usuarios.js.
// Contraseñas con PBKDF2-SHA256 (en el servidor: scrypt). Los datos de prueba nunca salen del teléfono.
import { sha256 } from "@noble/hashes/sha2";
import { pbkdf2 } from "@noble/hashes/pbkdf2";
import { Buffer } from "./bytes.js";

const randomBytes = (n) => Buffer.from([...crypto.getRandomValues(new Uint8Array(n))].map((b) => b.toString(16).padStart(2, "0")).join(""), "hex");

function createHash(algoritmo) {
  if (algoritmo !== "sha256") throw new Error("Solo sha256");
  let datos = "";
  const h = {
    update: (s) => ((datos += s), h),
    digest: (codificacion) => {
      const r = new Buffer(sha256(new TextEncoder().encode(datos)));
      return codificacion ? r.toString(codificacion) : r;
    },
  };
  return h;
}

const scryptSync = (clave, sal, largo) => new Buffer(pbkdf2(sha256, clave, sal, { c: 2000, dkLen: largo }));

function timingSafeEqual(a, b) {
  if (a.length !== b.length) throw new RangeError("Largo distinto");
  let dif = 0;
  for (let i = 0; i < a.length; i++) dif |= a[i] ^ b[i];
  return dif === 0;
}

export default { randomBytes, createHash, scryptSync, timingSafeEqual };
