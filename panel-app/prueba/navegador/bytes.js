// Lo mínimo de Buffer que usan src/reservas.js y src/usuarios.js (hex y base64url)
export class Buffer extends Uint8Array {
  static from(texto, codificacion) {
    if (codificacion !== "hex") throw new Error("Solo hex");
    return new Buffer((texto.match(/../g) || []).map((h) => parseInt(h, 16)));
  }

  toString(codificacion) {
    if (codificacion === "hex") return [...this].map((b) => b.toString(16).padStart(2, "0")).join("");
    if (codificacion === "base64url") return btoa(String.fromCharCode(...this)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    return new TextDecoder().decode(this);
  }
}
