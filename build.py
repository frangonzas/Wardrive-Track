"""Genera un ejecutable autónomo para el sistema anfitrión con PyInstaller.

La aplicación no necesita PyInstaller para ejecutarse desde el código fuente.
Instalación opcional: python -m pip install pyinstaller
Uso: python build.py
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    for name in ("web", "examples", "run.py"):
        if not (root / name).exists():
            raise SystemExit(f"Falta {name}. Ejecuta desde el repositorio completo.")
    cmd = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
        "--onefile", "--noupx", "--name", "Wardrive-Track",
        "--add-data", f"web{os.pathsep}web",
        "--add-data", f"examples{os.pathsep}examples",
        str(root / "run.py"),
    ]
    print("Construyendo Wardrive Track para", sys.platform, flush=True)
    try:
        subprocess.run(cmd, check=True, cwd=root)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Error de compilación: {exc.returncode}") from exc
    except FileNotFoundError:
        raise SystemExit("Falta PyInstaller: python -m pip install pyinstaller")
    print("Ejecutable generado en:", root / "dist", flush=True)

if __name__ == "__main__":
    main()
