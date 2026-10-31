# Actualización desde Wardrive Track 0.1 / 0.2 a 0.3.0

**Creador: Fran Gonzas · Versión de destino: 0.3.0**

## Por qué puede seguir apareciendo una edición antigua

- La terminal está abierta en otro clon o una carpeta de Descargas anterior.
- Se está ejecutando un archivo EXE/binario empaquetado antiguo.
- Una pestaña del navegador apunta al servidor de un proceso anterior.
- El acceso directo o lanzador apunta a una carpeta que no es la del código actualizado.

**Importante:** hacer git pull **no actualiza los ejecutables PyInstaller** previamente descargados.

## Solución recomendada: carpeta nueva, sin borrar nada

Cierra la aplicación antigua con Ctrl+C y las pestañas asociadas. No borres todavía tus archivos de captura.

**macOS:**

~~~bash
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git Wardrive-Track-v0.3.0
cd Wardrive-Track-v0.3.0
python3 run.py --version
python3 run.py --diagnostico
python3 run.py
~~~

**Windows PowerShell:**

~~~powershell
cd $HOME
git clone https://github.com/frangonzas/Wardrive-Track.git Wardrive-Track-v0.3.0
cd Wardrive-Track-v0.3.0
py -3 run.py --version
py -3 run.py --diagnostico
py -3 run.py
~~~

**Linux:**

~~~bash
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git Wardrive-Track-v0.3.0
cd Wardrive-Track-v0.3.0
python3 run.py --version
python3 run.py --diagnostico
python3 run.py
~~~

Si ya existe la carpeta nueva, utiliza git pull --ff-only **dentro de ella**, en lugar de clonarla de nuevo. No emplees git reset --hard para resolver errores: podría eliminar cambios.

## Alternativa: actualizar el clon antiguo

Entra en la carpeta que contiene el proyecto original y ejecuta:

~~~bash
git status
git pull --ff-only
python3 run.py --version
python3 run.py --diagnostico
~~~

En Windows sustituye python3 por py -3. Si Git informa de modificaciones locales, haz una copia de seguridad antes de resolverlas.

## Si usabas un ejecutable autónomo

Descarga el artifact de **[v0.3.0](https://github.com/frangonzas/Wardrive-Track/actions/runs/41188218392)**. Debe incluir **v0.3.0** en el nombre. Un ejecutable viejo nunca cambia por actualizar el repositorio.

Comprueba --version en el archivo recién descargado, ejecútalo y utiliza solo la URL que imprima esa sesión.

## Comprobación final

1. La terminal dice **Wardrive Track v0.3.0 · Fran Gonzas**.
2. El panel web indica **v0.3.0 · Fran Gonzas**.
3. La ruta /api/about del puerto activo devuelve versión **0.3.0**.
4. La demostración incluye **5 archivos sintéticos** con Wi-Fi y BLE.

[Volver al README](../README.md) · [Manual de compilación](COMPILACION.md)
