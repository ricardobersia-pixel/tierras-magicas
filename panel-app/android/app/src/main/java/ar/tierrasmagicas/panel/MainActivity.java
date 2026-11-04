package ar.tierrasmagicas.panel;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import com.getcapacitor.Bridge;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.BridgeWebViewClient;
import java.io.File;
import java.io.FileOutputStream;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (bridge != null) {
            bridge.setWebViewClient(new ClienteConMotivo(bridge));
            // El panel llama a window.TMNativo.guardarArchivo(...) para los informes PDF y planillas CSV
            bridge.getWebView().addJavascriptInterface(new Archivos(this), "TMNativo");
        }
    }

    // Guarda un archivo generado por el panel y abre el selector del teléfono para verlo, guardarlo o compartirlo
    static class Archivos {

        private final Activity actividad;

        Archivos(Activity actividad) {
            this.actividad = actividad;
        }

        @JavascriptInterface
        public void guardarArchivo(String nombre, String tipo, String base64) {
            try {
                File carpeta = new File(actividad.getCacheDir(), "compartidos");
                if (!carpeta.exists() && !carpeta.mkdirs()) throw new IllegalStateException("No se pudo crear la carpeta");
                File archivo = new File(carpeta, nombre.replaceAll("[^A-Za-z0-9._-]", "_"));
                try (FileOutputStream salida = new FileOutputStream(archivo)) {
                    salida.write(Base64.decode(base64, Base64.DEFAULT));
                }
                Uri uri = FileProvider.getUriForFile(actividad, actividad.getPackageName() + ".fileprovider", archivo);
                Intent compartir = new Intent(Intent.ACTION_SEND).setType(tipo).putExtra(Intent.EXTRA_STREAM, uri).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                Intent ver = new Intent(Intent.ACTION_VIEW).setDataAndType(uri, tipo).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                Intent selector = Intent.createChooser(ver, "Abrir, guardar o compartir").putExtra(Intent.EXTRA_INITIAL_INTENTS, new Intent[] { compartir });
                actividad.runOnUiThread(() -> actividad.startActivity(selector));
            } catch (Exception e) {
                actividad.runOnUiThread(() -> Toast.makeText(actividad, "No se pudo guardar el archivo: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }
        }
    }

    // Igual que el de Capacitor, pero le dice a la página de error por qué no abrió el panel
    // (error de red con su código de Android, o el código HTTP que respondió el servidor).
    static class ClienteConMotivo extends BridgeWebViewClient {

        private final Bridge bridge;

        ClienteConMotivo(Bridge bridge) {
            super(bridge);
            this.bridge = bridge;
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (request.isForMainFrame()) mostrarError(view, "red", error.getErrorCode(), request.getUrl());
        }

        @Override
        public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse respuesta) {
            if (request.isForMainFrame()) mostrarError(view, "http", respuesta.getStatusCode(), request.getUrl());
        }

        private void mostrarError(WebView view, String tipo, int codigo, Uri url) {
            String pagina = bridge.getErrorUrl();
            if (pagina == null) return;
            view.loadUrl(
                Uri.parse(pagina)
                    .buildUpon()
                    .appendQueryParameter("tipo", tipo)
                    .appendQueryParameter("codigo", String.valueOf(codigo))
                    .appendQueryParameter("url", String.valueOf(url))
                    .build()
                    .toString()
            );
        }
    }
}
