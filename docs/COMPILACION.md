# Compilación y ejecutables — Wardrive Track 0.2.0

La aplicación ofrece dos opciones:

1. **Recomendada para desarrollo y diagnóstico:** ejecutar el código con **Python 3.10+** sin paquetes adicionales.
2. **Ejecutable independiente:** crear un archivo nativo con PyInstaller para cada sistema operativo.

Los paquetes creados por GitHub Actions no están firmados digitalmente ni notarizados. En macOS, Windows y algunas distribuciones Linux podrían mostrarse advertencias de seguridad. La versión Python permite verificar y ejecutar el código sin instalar binarios de terceros.

## Descargar ejecutables creados automáticamente

1. Abre la página [GitHub Actions](https://github.com/frangonzas/Wardrive-Track/actions/workflows/build.yml).
2. Selecciona una ejecución con el resultado **verde: Success**.
3. En la parte inferior, sección **Artifacts**, elige:
   - **Wardrive-Track-Windows** → Windows (archivo .exe).
   - **Wardrive-Track-macOS** → macOS (ejecutable).
   - **Wardrive-Track-Linux** → Linux (ejecutable).
4. Descarga el ZIP y extrae su contenido.
5. Ejecuta el binario desde una terminal o PowerShell.

Los artifacts se conservan durante un período limitado (**30 días**). La descarga puede requerir iniciar sesión en GitHub.

**Nota:** los binarios se compilan **de forma nativa** en GitHub Actions para el sistema de destino. La compatibilidad depende de la arquitectura, versión del sistema y bibliotecas disponibles. El paquete macOS se genera en un runner Apple Silicon o Intel según el runner proporcionado por GitHub; revisa la arquitectura de la ejecución antes de usarlo.

## Compilar tú mismo en macOS

~~~bash
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 -m pip install --upgrade pyinstaller
python3 -m unittest discover -s tests -v
python3 build.py
./dist/Wardrive-Track --help
./dist/Wardrive-Track
~~~

## Compilar en Linux (Debian/Ubuntu)

~~~bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pyinstaller
python -m unittest discover -s tests -v
python build.py
./dist/Wardrive-Track --help
./dist/Wardrive-Track
~~~

Usar un entorno virtual evita modificar los paquetes Python del sistema y los problemas de PEP 668 en distribuciones recientes.

## Compilar en Windows — PowerShell

~~~powershell
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
py -3 -m pip install --upgrade pyinstaller
py -3 -m unittest discover -s tests -v
py -3 build.py
.\dist\Wardrive-Track.exe --help
.\dist\Wardrive-Track.exe
~~~

## Datos que incluye el binario

El script **build.py** empaqueta automáticamente:
- El motor Python.
- La interfaz web completa (**web/**).
- Los cinco archivos sintéticos de demostración (**examples/**).

El binario resultante arranca un servidor HTTP privado en **127.0.0.1** y abre el navegador, igual que la versión Python. Se detiene mediante **Ctrl+C** en la terminal desde la que se ejecuta.

El instalador y la firma digital no forman parte de esta versión; no es un MSI/DMG/DEB. Para auditorías o uso habitual recomendamos el código fuente.

## CI y verificación

La compilación automatizada está definida en **.github/workflows/build.yml** y publica un artifact por sistema operativo. Antes de empaquetar, ejecuta la suite Python; después comprueba que el ejecutable responde a **--help**. Estas validaciones no sustituyen pruebas manuales de la interfaz en los tres sistemas.
