"""Servidor local limitado a loopback, para evitar dependencias gráficas."""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .core import Session, as_csv, as_geojson
from . import APP_NAME, CREATOR, __version__, metadata


def resources_root() -> Path:
    """Localiza web/ y examples/ tanto en código como en PyInstaller --onefile."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent


WEB = resources_root() / "web"
EXAMPLES = resources_root() / "examples"
MAX_FILE_BYTES = 32 * 1024 * 1024
SUPPORTED = {".pcap", ".pcapng", ".log", ".txt", ".csv"}


class Handler(BaseHTTPRequestHandler):
    session: Session
    server_version = f"WardriveTrack/{__version__}"

    def _headers(self, status: int, ctype: str, length: int, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' https://*.tile.openstreetmap.org https://unpkg.com data:; style-src 'self' 'unsafe-inline' https://unpkg.com; script-src 'self' https://unpkg.com; connect-src 'self'; font-src 'self'; object-src 'none'; frame-ancestors 'none'")
        if extra:
            for key, value in extra.items():
                self.send_header(key, value)
        self.end_headers()

    def _send(self, body: bytes, ctype="application/json; charset=utf-8", status=200, extra=None):
        self._headers(status, ctype, len(body), extra)
        self.wfile.write(body)

    def _json(self, value, status=200):
        self._send(json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8"), status=status)

    def _valid_host(self):
        host = self.headers.get("Host", "")
        port = self.server.server_address[1]
        return host in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _valid_origin(self):
        origin = self.headers.get("Origin")
        if origin is None:
            return True
        return origin in (f"http://127.0.0.1:{self.server.server_address[1]}",
                          f"http://localhost:{self.server.server_address[1]}")

    def do_GET(self):
        if not self._valid_host():
            return self._json({"error": "Host no permitido"}, 403)
        path = urlsplit(self.path).path
        if path == "/api/about":
            return self._json(metadata())
        if path == "/api/status":
            snapshot = self.session.snapshot()
            snapshot["app"] = metadata()
            return self._json(snapshot)
        if path == "/api/export.geojson":
            body = json.dumps(as_geojson(self.session.snapshot()), ensure_ascii=False).encode()
            return self._send(body, "application/geo+json; charset=utf-8", extra={"Content-Disposition": 'attachment; filename="wardrive-track.geojson"'})
        if path == "/api/export.csv":
            body = as_csv(self.session.snapshot()).encode("utf-8-sig")
            return self._send(body, "text/csv; charset=utf-8", extra={"Content-Disposition": 'attachment; filename="wardrive-track.csv"'})
        names = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
        name = names.get(path)
        if name:
            file = WEB / name
            ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
            if name == "index.html":
                html = file.read_text(encoding="utf-8")
                html = html.replace("__WARDRIVE_VERSION__", __version__)
                html = html.replace("__WARDRIVE_CREATOR__", CREATOR)
                html = html.replace("__WARDRIVE_APP__", APP_NAME)
                return self._send(html.encode("utf-8"), ctype + "; charset=utf-8")
            return self._send(file.read_bytes(), ctype + "; charset=utf-8")
        return self._json({"error": "No encontrado"}, 404)

    def do_POST(self):
        if not self._valid_host() or not self._valid_origin():
            return self._json({"error": "Origen no permitido"}, 403)
        path = urlsplit(self.path)
        if path.path == "/api/clear":
            if self.headers.get("Content-Length") not in ("0", None):
                return self._json({"error": "Cuerpo no admitido"}, 400)
            self.session.reset()
            return self._json({"ok": True})
        if path.path == "/api/demo":
            example = EXAMPLES
            self.session.reset()
            reports = []
            for name in ("ejemplo_wigle.csv", "ruta_gps.log", "captura_ejemplo.pcap", "ejemplo_bluetooth.csv", "bt_wardrive_demo.log"):
                reports.append(self.session.import_data(name, (example / name).read_bytes()))
            return self._json({"reports": reports})
        if path.path != "/api/import":
            return self._json({"error": "No encontrado"}, 404)
        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            length = -1
        if not 0 < length <= MAX_FILE_BYTES:
            return self._json({"error": "Cada archivo debe tener entre 1 byte y 32 MiB."}, 413)
        name = parse_qs(path.query).get("name", [""])[0]
        name = re.split(r"[/\\]", name)[-1][:150]
        if Path(name).suffix.lower() not in SUPPORTED:
            return self._json({"error": "Formato no permitido. Usa PCAP, PCAPNG, LOG, TXT o CSV."}, 415)
        data = self.rfile.read(length)
        if len(data) != length:
            return self._json({"error": "Lectura incompleta"}, 400)
        try:
            result = self.session.import_data(name, data)
            return self._json(result)
        except Exception:
            return self._json({"error": "No se ha podido analizar el archivo."}, 422)

    def log_message(self, fmt, *args):
        # No imprimimos nombres de redes o datos de usuario por defecto.
        if os.environ.get("WARDRIVE_DEBUG") == "1":
            super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} {__version__} — Fran Gonzas — análisis local de Wi-Fi y Bluetooth/BLE")
    parser.add_argument("--version", action="version", version=f"{APP_NAME} v{__version__} | Creador: {CREATOR}")
    parser.add_argument("--diagnostico", action="store_true", help="Comprobar versión y recursos de esta instalación")
    parser.add_argument("--no-browser", action="store_true", help="No abrir el navegador automáticamente")
    parser.add_argument("--port", type=int, default=0, help="Puerto local, por defecto automático")
    args = parser.parse_args()
    if args.diagnostico:
        print(f"{APP_NAME} v{__version__}")
        print(f"Creador: {CREATOR}")
        print(f"Ejecutable: {sys.executable}")
        print(f"Directorio de recursos: {resources_root()}")
        required = [WEB / "index.html", WEB / "app.js", WEB / "style.css",
                    EXAMPLES / "captura_ejemplo.pcap", EXAMPLES / "ejemplo_bluetooth.csv"]
        missing = [str(p) for p in required if not p.is_file()]
        if missing:
            for item in missing:
                print(f"FALTA: {item}")
            parser.exit(2, "Diagnóstico fallido: faltan recursos de esta versión.\n")
        print("Diagnóstico correcto: interfaz y ejemplos incluidos.")
        return
    for asset in (WEB / "index.html", WEB / "app.js", WEB / "style.css"):
        if not asset.is_file():
            parser.error(f"Falta el recurso: {asset}. Usa la carpeta completa o vuelve a descargar la versión.")
    Handler.session = Session()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/?v={__version__}"
    print(f"\n{APP_NAME} v{__version__} · Creador: {CREATOR}", flush=True)
    print(f"Servidor local: {url}\nCtrl+C para cerrar\n", flush=True)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
