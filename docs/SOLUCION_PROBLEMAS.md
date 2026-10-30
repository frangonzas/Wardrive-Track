# Solución de problemas

## «python», «python3» o «py» no se reconoce

Comprueba la instalación:

**macOS/Linux:**

~~~bash
python3 --version
~~~

**Windows PowerShell:**

~~~powershell
py --version
python --version
~~~

Instala una versión **3.10 o superior** de https://www.python.org/downloads/ y reinicia la terminal. En Windows comprueba la configuración de PATH.

## «git» no se reconoce

Instala Git desde https://git-scm.com/downloads/ y reinicia la terminal.

## «fatal: destination path 'Wardrive-Track' already exists»

La carpeta ya existe. **No es necesario volver a clonar**:

~~~bash
cd Wardrive-Track
git pull --ff-only
~~~

## El navegador no se abre

Arranca manualmente:

~~~bash
python3 run.py --no-browser
~~~

Copia la dirección **http://127.0.0.1:PUERTO** que aparezca en la terminal y ábrela en tu navegador. En Windows usa **py -3 run.py --no-browser**.

## «Address already in use» o puerto ocupado

El programa selecciona un puerto libre por defecto. Si fijaste **--port 8765**, prueba sin ese parámetro o elige otro puerto.

## El mapa aparece vacío

Si **no hay GPS**, los BSSID se mostrarán en el inventario pero no en el mapa. Importa registros con latitud y longitud, o utiliza la demostración.

Si hay coordenadas pero no se ven calles, puede faltar Internet o el CDN de Leaflet puede estar bloqueado. El plano esquemático sin conexión sigue mostrando las coordenadas.

## El PCAP no muestra redes

La versión 0.1 analiza tramas **802.11 beacon y probe response** con formatos de enlace compatibles. Una captura Ethernet (linktype 1) puede contener tráfico de red pero no esos beacons 802.11. Revisa el tipo de captura de origen.

## Los datos GPS no se relacionan con los PCAP

Comprueba:

1. Que la captura y el GPS tienen marcas de tiempo.
2. Que los relojes estaban sincronizados.
3. Que la fecha y la zona horaria son correctas: los timestamps sin zona se consideran **UTC**.
4. Que hay al menos un GPS a **8 segundos o menos** de la observación.
5. Que las coordenadas son válidas (latitud entre −90 y 90; longitud entre −180 y 180).

El programa **nunca inventa una posición** para una red sin ubicación documentada.

## El archivo excede el límite

Se aceptan **32 MiB por archivo**. Divide las capturas grandes en archivos menores y vuelve a importarlos.

## La demostración no aparece

Asegúrate de clonar el repositorio completo, con la carpeta **examples/**. Ejecuta desde la raíz:

~~~bash
python3 -m unittest discover -s tests -v
~~~

En Windows sustituye **python3** por **py -3**.

## No puedo actualizar con «git pull»

Consulta el estado:

~~~bash
git status
~~~

Si tienes cambios locales, guárdalos primero con un commit o una copia de seguridad. Evita **git reset --hard** salvo que entiendas que destruye cambios.

## Abrí la interfaz y perdí los resultados al cerrar

Es el comportamiento previsto: la sesión vive en RAM. Usa **Exportar CSV** o **Exportar GeoJSON** antes de detener el servidor.
