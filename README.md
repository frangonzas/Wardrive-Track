# Wardrive Track

![Pruebas multiplataforma](https://github.com/frangonzas/Wardrive-Track/actions/workflows/tests.yml/badge.svg)

**Análisis local y visualización geográfica de capturas Wi-Fi y registros GPS.**

Proyecto multiplataforma desarrollado en **Python 3.10+**, con interfaz web local. Importa archivos **PCAP, PCAPNG, CSV, LOG y TXT**, identifica redes Wi-Fi, cruza observaciones con trazas GPS por fecha/hora, explora los resultados sobre un mapa y exporta a **CSV y GeoJSON**.

**Versión:** 0.1.0 · **Sistemas:** Windows, macOS y Linux · **Dependencias Python:** ninguna · **Idioma de la documentación:** español

> **Importante:** la ubicación representada corresponde al lugar donde se observó una señal Wi-Fi, **no necesariamente al emplazamiento físico del punto de acceso**. Un PCAP sin GPS no proporciona, por sí mismo, la posición geográfica de una red. La aplicación no inventa coordenadas ni consulta bases de datos de BSSID.

## Instalación rápida (copiar y pegar)

Requisitos: **Python 3.10 o posterior**, **Git** y un navegador moderno. No necesitas instalar paquetes con pip.

### macOS (Terminal)

~~~bash
python3 --version
git --version
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 run.py
~~~

### Linux (Terminal)

~~~bash
python3 --version
git --version
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 run.py
~~~

### Windows (PowerShell)

~~~powershell
py --version
git --version
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
py -3 run.py
~~~

Si Windows no reconoce **py**, prueba **python --version** y ejecuta **python run.py**. En macOS/Linux, si no reconoce **python3**, instala Python 3.10+ y repite los pasos.

La aplicación inicia un servidor HTTP en **127.0.0.1**, asigna un puerto disponible y abre el navegador. Si no abre automáticamente, copia la dirección local que aparece en la terminal. **Para detenerla, pulsa Ctrl+C.**

**Guías completas:** [Instalación y actualización](docs/INSTALACION.md) · [Manual de uso](docs/USO.md) · [Solución de problemas](docs/SOLUCION_PROBLEMAS.md).

## Funciones

| Módulo | Funcionalidad |
| --- | --- |
| Importación | PCAP, PCAPNG, registros GPS en LOG/TXT, JSON por línea y CSV, incluido WiGLE 1.6 |
| Análisis | BSSID, SSID, RSSI cuando está disponible, canal, recuento de observaciones |
| Geolocalización | Coordenadas explícitas y correlación con GPS por proximidad temporal (máximo 8 segundos) |
| Mapa | Puntos de observación y recorrido GPS; plano esquemático alternativo sin Internet |
| Exploración | Inventario de redes, búsqueda y filtros |
| Exportación | CSV de redes y GeoJSON con puntos georreferenciados y recorrido |
| Privacidad | Análisis local; no se suben archivos a un servidor externo |

## Primer uso en 3 pasos

1. Ejecuta la aplicación y selecciona **Cargar demostración**. Los datos de ejemplo son inventados y sirven para verificar el funcionamiento.
2. Para analizar tus datos, importa un PCAP/PCAPNG o un CSV/LOG/TXT compatible. Si las capturas no incluyen GPS, importa también un registro GPS con marcas de tiempo sincronizadas.
3. Explora las redes detectadas y el mapa; exporta los resultados a **CSV** o **GeoJSON**.

Los ejemplos de la carpeta **examples/** son sintéticos. Para correlacionar una captura real con GPS, ambas fuentes deben compartir una referencia de tiempo consistente. Las fechas sin zona horaria se interpretan como UTC.

## Formatos admitidos

| Archivo | Alcance en v0.1.0 |
| --- | --- |
| **.pcap** | Tramas Wi-Fi 802.11 beacon / probe response, con enlace 802.11 o Radiotap compatible |
| **.pcapng** | Capturas con SHB, IDB y EPB para interfaces Wi-Fi compatibles |
| **.csv** | Columnas BSSID/MAC, SSID, RSSI, latitud, longitud, fecha/hora; WiGLE 1.6 |
| **.log / .txt** | Líneas con pares clave/valor, JSON por línea y NMEA RMC |

Ejemplo de archivo LOG propio:

~~~text
2026-10-29T12:00:00Z GPS lat=40.41680 lon=-3.70380
2026-10-29T12:00:03Z BSSID=02:AA:BB:CC:DD:01 SSID="Laboratorio" RSSI=-48 channel=6
~~~

## Comandos de mantenimiento

**Ejecutar sin abrir el navegador:**

~~~bash
python3 run.py --no-browser
~~~

**Definir un puerto local (ejemplo 8765):**

~~~bash
python3 run.py --port 8765
~~~

**Ejecutar las pruebas desde la raíz del repositorio:**

~~~bash
python3 -m unittest discover -s tests -v
~~~

En Windows, sustituye **python3** por **py -3**. Para descargar actualizaciones del repositorio, desde la carpeta del proyecto ejecuta **git pull --ff-only**.

## Arquitectura

~~~text
Wardrive-Track/
├── run.py                     # Punto de entrada
├── start_windows.bat          # Lanzador Windows
├── start_macos_linux.sh       # Lanzador macOS/Linux
├── requirements.txt           # Sin paquetes adicionales
├── wardrive_track/
│   ├── __init__.py
│   ├── core.py                # Modelo de sesión y cruce GPS
│   ├── parsers.py             # Lectores y normalización
│   └── server.py              # Servidor HTTP local / API
├── web/
│   ├── index.html             # Panel de control
│   ├── style.css
│   └── app.js
├── examples/                  # Datos sintéticos
├── tests/                     # Pruebas unitarias
├── docs/
│   ├── INSTALACION.md
│   ├── USO.md
│   └── SOLUCION_PROBLEMAS.md
└── README.md
~~~

## Límites y consideraciones

- Máximo **32 MiB por archivo** y **60.000 registros por tipo y sesión**.
- Los PCAP Ethernet no contienen por sí mismos las tramas de gestión Wi-Fi necesarias para identificar puntos de acceso.
- RSSI no permite calcular una distancia exacta. La posición mostrada es una **observación georreferenciada**, no una triangulación.
- La vista web limita el volumen de filas y puntos dibujados para mantener la fluidez; las exportaciones incluyen los datos procesados.
- La información se conserva en memoria mientras se ejecuta el proceso; exporta antes de cerrar.
- El mapa de calles utiliza **Leaflet** y teselas de **OpenStreetMap** en línea; sin Internet se usa un plano esquemático. Las peticiones de teselas pueden revelar al proveedor la zona visualizada.
- No implementa captura activa, seguimiento de personas, consultas a bases de localización ni geolocalización de BSSID sin coordenadas observadas.

## Seguridad y uso responsable

Utiliza capturas propias o con autorización. Los BSSID, nombres de redes y coordenadas pueden ser sensibles; **no publiques capturas o exportaciones reales** en el repositorio. El servidor está restringido al equipo local (**127.0.0.1**). Más detalles en [Política de seguridad](SECURITY.md).

## Desarrollo

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para ejecutar pruebas y proponer cambios, y [CHANGELOG.md](CHANGELOG.md) para conocer el historial de versiones. Proyecto en fase **v0.1.0**; **no se ha concedido todavía una licencia de reutilización**. Hasta que el titular añada una licencia explícita, se aplican los derechos de autor habituales.

---

**Wardrive Track** · [Repositorio oficial](https://github.com/frangonzas/Wardrive-Track) · Proyecto de análisis offline-first y cartografía de observaciones Wi-Fi.
