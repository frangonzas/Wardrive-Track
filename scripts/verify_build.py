"""Smoke test de un ejecutable PyInstaller real (no solo --help).

Comprueba:
  1. Identidad y versión de --version.
  2. Recursos web/ejemplos empaquetados con --diagnostico.
  3. Servidor local, HTML actual, API y carga de demostración.
Uso: python scripts/verify_build.py <ruta-del-ejecutable>
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

from wardrive_track import __version__, CREATOR


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/verify_build.py <ejecutable>")
    binary = Path(sys.argv[1]).resolve()
    if not binary.is_file():
        raise SystemExit(f"No existe el ejecutable: {binary}")
    for option in ("--version", "--diagnostico"):
        result = subprocess.run([str(binary), option], capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=45)
        if result.returncode:
            raise AssertionError(f"{option} devolvió {result.returncode}: {result.stderr}\n{result.stdout}")
        if __version__ not in result.stdout or CREATOR not in result.stdout:
            raise AssertionError(f"{option}: versión o creador incorrectos: {result.stdout}")
    process = subprocess.Popen([str(binary), "--no-browser", "--port", "0"],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace", bufsize=1)
    try:
        url = None
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                raise AssertionError(f"El ejecutable finalizó antes de iniciar el servidor: {process.returncode}")
            match = re.search(r"http://127[.]0[.]0[.]1:(\d+)", line)
            if match:
                url = f"http://127.0.0.1:{match.group(1)}"
                break
        if not url:
            raise AssertionError("El ejecutable no anunció el puerto local")
        with urlopen(url + "/api/about", timeout=10) as response:
            about = json.load(response)
            assert about["version"] == __version__, about
            assert about["creator"] == CREATOR, about
        with urlopen(url + "/?v=" + __version__, timeout=10) as response:
            html = response.read().decode("utf-8")
            assert f"v{__version__}" in html and CREATOR in html, "Interfaz obsoleta"
            assert "securityFilter" in html and "typeFilter" in html, "Faltan filtros BLE/Wi-Fi"
        with urlopen(url + "/app.js?v=" + __version__, timeout=10) as response:
            assert response.status == 200
        with urlopen(Request(url + "/api/demo", data=b"", method="POST"), timeout=10) as response:
            assert len(json.load(response)["reports"]) == 5
        with urlopen(url + "/api/status", timeout=10) as response:
            data = json.load(response)
            assert data["app"]["version"] == __version__
            assert data["stats"]["ble"] > 0
        print(f"OK: {binary.name} · {CREATOR} · v{__version__} · web/API/demo verificadas")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


if __name__ == "__main__":
    main()
