# Instalación, verificación y actualización

Esta guía contiene comandos **listos para copiar y pegar**, separados por plataforma.

## 1. Requisitos

- **Python 3.10 o posterior**: https://www.python.org/downloads/
- **Git**: https://git-scm.com/downloads
- Navegador actualizado (Firefox, Chrome, Edge o Safari).
- Conexión a Internet **solo** para descargar el proyecto y visualizar el mapa de calles. El análisis local funciona desconectado.

**No instales paquetes con pip:** Wardrive Track emplea únicamente módulos de la biblioteca estándar de Python. No necesita crear un entorno virtual para ejecutarse.

## 2. macOS: instalación por Terminal

Abre **Terminal** (Aplicaciones → Utilidades → Terminal).

### Paso 1: comprueba Python y Git

~~~bash
python3 --version
git --version
~~~

Si alguno falta, instala Python desde https://www.python.org/downloads/macos/ y Git desde https://git-scm.com/downloads/mac. Vuelve a abrir Terminal.

### Paso 2: descarga Wardrive Track

~~~bash
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
~~~

### Paso 3: inicia la aplicación

~~~bash
python3 run.py
~~~

Se mostrará una URL similar a **http://127.0.0.1:XXXXX** (el puerto cambia cada vez si no se fija). Normalmente el navegador se abrirá solo.

**Para cerrarla:** pulsa **Ctrl+C** en la Terminal desde la que la ejecutaste.

**Prueba rápida:**

~~~bash
python3 -m unittest discover -s tests -v
~~~

## 3. Linux: Ubuntu, Debian y derivadas

Abre una terminal. Instala los requisitos si no los tienes:

~~~bash
sudo apt update
sudo apt install -y python3 git
~~~

Verifica y descarga:

~~~bash
python3 --version
git --version
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 run.py
~~~

Las versiones antiguas de distribuciones pueden incluir Python anterior a 3.10. En ese caso, instala Python 3.10+ mediante los repositorios o el método recomendado por tu distribución. En Fedora puedes usar **sudo dnf install python3 git**.

**Pruebas:**

~~~bash
python3 -m unittest discover -s tests -v
~~~

## 4. Windows 10 y 11: PowerShell

Instala **Python 3.10+** desde https://www.python.org/downloads/windows/ y **Git para Windows** desde https://git-scm.com/downloads/win.

Durante la instalación de Python, activa la opción **Add Python to PATH** si se ofrece.

Abre **PowerShell** y ejecuta:

~~~powershell
py --version
git --version
cd $HOME
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
py -3 run.py
~~~

Si **py** no funciona pero **python** sí:

~~~powershell
python --version
python run.py
~~~

Pruebas:

~~~powershell
py -3 -m unittest discover -s tests -v
~~~

Puedes utilizar también el archivo **start_windows.bat** incluido en el proyecto.

## 5. Ejecutar con opciones

Desde la carpeta Wardrive-Track:

**No abrir navegador automáticamente** (macOS/Linux):

~~~bash
python3 run.py --no-browser
~~~

**Usar un puerto fijo**:

~~~bash
python3 run.py --port 8765
~~~

Accede a **http://127.0.0.1:8765** en el navegador.

En Windows, sustituye **python3** por **py -3**.

> El servidor escucha únicamente en **127.0.0.1**, de modo que no se publica en la red local ni en Internet.

## 6. Actualizar el proyecto

Abre Terminal/PowerShell y entra en la carpeta clonada.

**macOS/Linux:**

~~~bash
cd ~/Wardrive-Track
git pull --ff-only
python3 run.py
~~~

**Windows PowerShell:**

~~~powershell
cd "$HOME\Wardrive-Track"
git pull --ff-only
py -3 run.py
~~~

Si has modificado archivos, Git podría impedir la actualización automática. Consulta **git status** antes de sobrescribir trabajo personal.

## 7. Desinstalar

Para desinstalar Wardrive Track basta con cerrar el programa y eliminar su carpeta. No instala servicios ni dependencias Python adicionales.

## 8. Verificar la primera ejecución

1. Abre el panel local.
2. Selecciona **Cargar demostración**.
3. Debes ver redes detectadas, algunas con coordenadas, y un recorrido GPS.
4. Exporta CSV y GeoJSON.
5. Cierra la aplicación con **Ctrl+C**.

Para interpretar correctamente una captura o importar GPS real, consulta [USO.md](USO.md). Para errores habituales, consulta [SOLUCION_PROBLEMAS.md](SOLUCION_PROBLEMAS.md).

## 9. Ejecutables independientes (opcional)

Si prefieres utilizar la versión compilada sin instalar Python, consulta la guía [COMPILACION.md](COMPILACION.md), que explica cómo obtener los artifacts de Windows, macOS y Linux desde GitHub Actions o compilar con PyInstaller en tu propio equipo. Los binarios no están firmados digitalmente.
