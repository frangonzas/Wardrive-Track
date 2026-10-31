# Wardrive Track — identificar la versión oficial

**Versión actual: 0.3.0**  
**Creador: Fran Gonzas**  
**Fecha: 31/10/2026**  
**Repositorio: https://github.com/frangonzas/Wardrive-Track**

La rama **main** mantiene el código actual. Las versiones anteriores siguen en el historial de Git, pero no son la edición recomendada.

## Verificar el código de la carpeta actual

macOS/Linux:

~~~bash
python3 run.py --version
python3 run.py --diagnostico
~~~

Windows (PowerShell):

~~~powershell
py -3 run.py --version
py -3 run.py --diagnostico
~~~

La primera orden debe responder **Wardrive Track v0.3.0 | Creador: Fran Gonzas**. La segunda imprime la ruta de los recursos, comprueba el HTML y los ejemplos y responde **Diagnóstico correcto**.

## Verificar un ejecutable descargado

Su nombre debe contener **v0.3.0**:

- Wardrive-Track-v0.3.0-Windows.exe
- Wardrive-Track-v0.3.0-macOS
- Wardrive-Track-v0.3.0-Linux

Ejecuta ese archivo con el argumento **--version** antes de abrirlo. Los ejecutables con nombre genérico corresponden a paquetes antiguos.

## Comprobar el navegador

En la web aparecerá **v0.3.0 · Fran Gonzas**. La terminal proporciona la dirección de la ejecución activa, con parámetro **?v=0.3.0**. No utilices pestañas antiguas que sigan conectadas a otro proceso.

Puedes consultar también la API local en **http://127.0.0.1:PUERTO/api/about**, sustituyendo PUERTO por el número indicado en tu terminal.

Devolverá nombre, versión, creador, fecha y repositorio. Si el dato de versión es diferente, no estás conectado al programa nuevo.

**Si se muestra la versión anterior**, sigue la guía [ACTUALIZACION.md](ACTUALIZACION.md).
