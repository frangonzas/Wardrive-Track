"""Compilación nativa VERSIONADA y reproducible mediante PyInstaller.

El nombre incluye la versión y el sistema. Evita sobrescribir/confundir EXE
de versiones anteriores. Crea artifacts de GitHub Actions con los mismos datos.
"""
from __future__ import annotations
import os
import platform
import subprocess
import sys
from pathlib import Path

from wardrive_track import __version__, CREATOR


def binary_name() -> str:
    system = platform.system()
    os_name = {"Darwin": "macOS", "Windows": "Windows", "Linux": "Linux"}.get(system)
    if os_name is None:
        raise SystemExit(f"Sistema no soportado para compilar: {system}")
    return f"Wardrive-Track-v{__version__}-{os_name}"


def main():
    root = Path(__file__).resolve().parent
    for name in ("web/index.html", "web/app.js", "web/style.css", "examples/captura_ejemplo.pcap"):
        if not (root / name).is_file():
            raise SystemExit(f"Recurso imprescindible no encontrado: {name}")
    name = binary_name()
    cmd = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
        "--onefile", "--noupx", "--name", name,
        "--add-data", f"web{os.pathsep}web",
        "--add-data", f"examples{os.pathsep}examples",
        str(root / "run.py"),
    ]
    print(f"Compilación de {name} · Creador: {CREATOR}", flush=True)
    try:
        subprocess.run(cmd, check=True, cwd=root)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Compilación fallida: código {exc.returncode}") from exc
    target = root / "dist" / (name + (".exe" if os.name == "nt" else ""))
    if not target.is_file():
        raise SystemExit(f"No se generó el ejecutable esperado: {target}")
    print(f"Ejecutable: {target}", flush=True)
    # GitHub Actions publica el nombre real derivado de la versión, sin
    # duplicar números de versión en archivos YAML.
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"binary_path={target}\n")
            output.write(f"artifact_name={name}\n")


if __name__ == "__main__":
    main()
