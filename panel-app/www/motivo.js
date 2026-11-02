// Traduce por qué no abrió el panel a un mensaje para el usuario.
// tipo "red": código de error del WebView de Android (WebViewClient.ERROR_*). tipo "http": código que respondió el servidor.
const RAILWAY = "Railway → servicio → Settings → Networking → Public Domain";
const LOGS = "Railway → servicio → Deployments → View logs";

export function diagnosticar({ tipo, codigo }, conInternet) {
  if (tipo === "http") {
    if (codigo === 404) {
      return {
        motivo: "Railway no tiene ningún servicio con esa dirección.",
        accion: `La dirección está mal escrita o no es la del servicio. Copiala de ${RAILWAY}. Si está vacía, tocá "Generate Domain". Después tocá "Cambiar la dirección".`,
      };
    }
    if (codigo === 502 || codigo === 503 || codigo === 504) {
      return {
        motivo: "El servidor no está respondiendo: no arrancó, se cayó o se está reiniciando.",
        accion: `Si recién se publicó una versión, esperá un par de minutos y reintentá. Si sigue, revisá el error en ${LOGS}.`,
      };
    }
    if (codigo >= 500) {
      return { motivo: `El servidor tuvo un error interno (código ${codigo}).`, accion: `Reintentá en un momento. Si sigue, revisá ${LOGS}.` };
    }
    return { motivo: `El servidor respondió con el código ${codigo}.`, accion: "Reintentá. Si sigue, revisá que la dirección sea la del panel." };
  }

  if (tipo === "red") {
    if (!conInternet) {
      return { motivo: "El teléfono no tiene internet.", accion: "Revisá los datos móviles o el Wi-Fi y tocá Reintentar." };
    }
    switch (codigo) {
      case -2: // ERROR_HOST_LOOKUP
        return { motivo: "Esa dirección no existe.", accion: `Revisá que esté bien escrita. La correcta está en ${RAILWAY}.` };
      case -6: // ERROR_CONNECT
      case -7: // ERROR_IO
      case -8: // ERROR_TIMEOUT
        return {
          motivo: "El servidor no contesta.",
          accion: `Puede estar apagado o reiniciándose. Esperá un minuto y reintentá. Si sigue, revisá ${LOGS}.`,
        };
      case -11: // ERROR_FAILED_SSL_HANDSHAKE
        return {
          motivo: "No se pudo verificar la conexión segura (https) con el servidor.",
          accion: "Revisá que la fecha y la hora del teléfono sean correctas y reintentá.",
        };
      default:
        return { motivo: `Falló la conexión con el servidor (código ${codigo}).`, accion: "Reintentá. Si sigue, probá con otra red (Wi-Fi o datos)." };
    }
  }

  // Sin detalle (versión anterior de la app o error desconocido)
  return conInternet
    ? { motivo: "El servidor no respondió como se esperaba.", accion: `Revisá la dirección (${RAILWAY}) y que el servicio esté activo.` }
    : { motivo: "El teléfono no tiene internet.", accion: "Revisá los datos móviles o el Wi-Fi y tocá Reintentar." };
}
