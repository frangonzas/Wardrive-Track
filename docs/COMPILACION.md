# Ejecutables y compilación — Wardrive Track 0.3.0

**Creador: Fran Gonzas.**

## Descargar binarios autónomos

La versión 0.3.0 genera ejecutables identificados inequívocamente por sistema:

| Sistema | Archivo |
| --- | --- |
| Windows | Wardrive-Track-v0.3.0-Windows.exe |
| macOS | Wardrive-Track-v0.3.0-macOS |
| Linux | Wardrive-Track-v0.3.0-Linux |

1. Abre la **[ejecución validada v0.3.0](https://github.com/frangonzas/Wardrive-Track/actions/runs/41188218392)**.
2. Busca **Artifacts** debajo de los trabajos, descarga el ZIP de tu sistema y extráelo.
3. Ejecuta el binario con **--version** y **--diagnostico** para comprobar la identidad y los recursos.
4. Después inicia el programa normalmente.

Los artifacts de GitHub pueden exigir inicio de sesión y se eliminan al cumplirse su retención (30 días). Los binarios **no están firmados digitalmente ni notarizados**. No utilices los paquetes anteriores sin número de versión.

**Windows PowerShell:**

~~~powershell
.\Wardrive-Track-v0.3.0-Windows.exe --version
.\Wardrive-Track-v0.3.0-Windows.exe --diagnostico
.\Wardrive-Track-v0.3.0-Windows.exe
~~~

**macOS:**

~~~bash
chmod +x Wardrive-Track-v0.3.0-macOS
./Wardrive-Track-v0.3.0-macOS --version
./Wardrive-Track-v0.3.0-macOS --diagnostico
./Wardrive-Track-v0.3.0-macOS
~~~

**Linux:**

~~~bash
chmod +x Wardrive-Track-v0.3.0-Linux
./Wardrive-Track-v0.3.0-Linux --version
./Wardrive-Track-v0.3.0-Linux --diagnostico
./Wardrive-Track-v0.3.0-Linux
~~~

## Compilar por cuenta propia

Para la compilación necesitas PyInstaller, solo como dependencia de construcción. No hace falta para ejecutar el programa desde código Python.

**macOS:**

~~~bash
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 -m pip install --upgrade pyinstaller
python3 build.py
python3 scripts/verify_build.py dist/Wardrive-Track-v0.3.0-macOS
~~~

**Linux Ubuntu/Debian:**

~~~bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pyinstaller
python build.py
python scripts/verify_build.py dist/Wardrive-Track-v0.3.0-Linux
~~~

**Windows PowerShell:**

~~~powershell
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
py -3 -m pip install --upgrade pyinstaller
py -3 build.py
py -3 scripts/verify_build.py .\dist\Wardrive-Track-v0.3.0-Windows.exe
~~~

## Control de calidad obligatorio

GitHub Actions ejecuta pruebas Python y JavaScript, compila el binario, valida **--version** y **--diagnostico**, arranca el servidor desde el **ejecutable real**, consulta **/api/about**, recibe el HTML con la versión y creador correctos, comprueba los filtros y carga la demostración Wi-Fi/BLE.

El archivo scripts/verify_build.py reproduce este control. La compilación lleva la carpeta web/ y examples/ dentro del ejecutable. No se entrega un instalador MSI/DMG/DEB; la arquitectura del binario depende de la máquina donde fue compilado.

**No confundas** la versión del repositorio con un binario ya descargado. Este último debe ser sustituido por el nuevo.
