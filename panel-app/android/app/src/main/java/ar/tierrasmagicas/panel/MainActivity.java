package ar.tierrasmagicas.panel;

import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import com.getcapacitor.Bridge;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.BridgeWebViewClient;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (bridge != null) bridge.setWebViewClient(new ClienteConMotivo(bridge));
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
