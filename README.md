# Wardrive Track — Versión 0.3.0

![Versión actual](https://img.shields.io/badge/%C3%9ALTIMA%20VERSI%C3%93N-v0.3.0-13b99d?style=for-the-badge)
![Creador](https://img.shields.io/badge/CREADOR-Fran%20Gonzas-244664?style=for-the-badge)
![Pruebas](https://github.com/frangonzas/Wardrive-Track/actions/workflows/tests.yml/badge.svg)
![Ejecutables](https://github.com/frangonzas/Wardrive-Track/actions/workflows/build.yml/badge.svg)

**Versión oficial actual: v0.3.0 — 31 de octubre de 2026**  
**Creador: Fran Gonzas · [@frangonzas](https://github.com/frangonzas)**

Análisis visual y local de capturas **Wi-Fi, Bluetooth y BLE**, incluyendo formatos compatibles con **ESP32 Marauder**, PCAP, PCAPNG y registros CSV/LOG/TXT con GPS. Compatible con **Windows, macOS y Linux**. Interfaz y documentación en español.

> **ATENCIÓN SI SE ABRE UNA VERSIÓN ANTIGUA:** esta edición se distingue por mostrar **v0.3.0 · Fran Gonzas** en la pantalla y por generar ejecutables cuyo nombre lleva obligatoriamente **v0.3.0**. Los binarios antiguos con nombre genérico no se actualizan al ejecutar Git. Lee [Cómo actualizar sin confusiones](docs/ACTUALIZACION.md).

## Instalación limpia recomendada

Necesitas **Python 3.10+**, Git y un navegador. No hay dependencias adicionales de Python para ejecutar el código. Utilizamos una carpeta nueva para no arrancar accidentalmente una copia anterior.

### macOS — Terminal

~~~bash
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git Wardrive-Track-v0.3.0
cd Wardrive-Track-v0.3.0
python3 run.py --version
python3 run.py --diagnostico
python3 run.py
~~~

### Windows — PowerShell

~~~powershell
cd $HOME
git clone https://github.com/frangonzas/Wardrive-Track.git Wardrive-Track-v0.3.0
cd Wardrive-Track-v0.3.0
py -3 run.py --version
py -3 run.py --diagnostico
py -3 run.py
~~~

### Linux — Ubuntu/Debian

~~~bash
sudo apt update
sudo apt install -y python3 git
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git Wardrive-Track-v0.3.0
cd Wardrive-Track-v0.3.0
python3 run.py --version
python3 run.py --diagnostico
python3 run.py
~~~

La primera comprobación debe imprimir **Wardrive Track v0.3.0 | Creador: Fran Gonzas**. El diagnóstico comprueba que la interfaz y los ejemplos están presentes. La aplicación imprime una URL local que incluye **?v=0.3.0** y abre esa versión en el navegador. Finaliza con **Ctrl+C**.

[Guía completa de instalación](docs/INSTALACION.md) · [Última versión y verificación](docs/ULTIMA_VERSION.md)

## Ejecutables autónomos por sistema operativo

También están disponibles compilaciones que no necesitan Python. Para evitar ambigüedades, el archivo incluye versión y sistema:

| Sistema | Archivo ejecutable |
| --- | --- |
| Windows | **Wardrive-Track-v0.3.0-Windows.exe** |
| macOS | **Wardrive-Track-v0.3.0-macOS** |
| Linux | **Wardrive-Track-v0.3.0-Linux** |

**[Descargar compilaciones comprobadas de v0.3.0](https://github.com/frangonzas/Wardrive-Track/actions/runs/41188218392)**: abre la ejecución, busca **Artifacts** y descarga el paquete de tu sistema. Los artifacts pueden requerir iniciar sesión en GitHub y tienen retención limitada.

**No elijas** los paquetes antiguos denominados simplemente Wardrive-Track-Windows, Wardrive-Track-macOS o Wardrive-Track-Linux. No corresponden a la nueva nomenclatura versionada.

[Guía de descarga y compilación local](docs/COMPILACION.md)

## Funcionalidades

| Módulo | Funciones |
| --- | --- |
| Wi-Fi | SSID, BSSID, canal, RSSI, fechas y número de observaciones |
| Seguridad Wi-Fi | OPEN, WEP, WPA, WPA2, WPA2/WPA3, WPA3, OWE y No determinada |
| Bluetooth / BLE | Nombre publicitado cuando existe, dirección, RSSI y tecnología |
| GPS | Puntos explícitos y correlación temporal con un margen máximo de 8 segundos |
| Importación | PCAP, PCAPNG, WiGLE CSV 1.6, LOG, TXT y NMEA RMC |
| Filtros | Nombre, dirección MAC, protocolo, seguridad, señal y presencia de GPS |
| Cartografía | Marcadores Wi-Fi/Bluetooth diferenciados, recorrido y plano esquemático |
| Exportación | CSV y GeoJSON de toda la sesión o de las selecciones filtradas |
| Privacidad | Análisis local; no se envían las capturas a nuestros servidores |

**El mapa señala el lugar de observación**, no la posición física del router o del dispositivo Bluetooth. No se infieren posiciones a partir de una MAC; las direcciones BLE pueden rotar y no representan necesariamente una identidad permanente. No se realizan ataques ni captura activa de radio.

## Primer uso y pruebas

1. Comprueba la versión en la terminal y en el encabezado de la web: **0.3.0 · Fran Gonzas**.
2. Pulsa **Cargar demostración completa** para explorar los cinco archivos sintéticos Wi-Fi, BLE/BT y GPS.
3. Filtra por tecnología y seguridad (WEP/WPA/WPA2/WPA3), busca por nombre y observa el mapa.
4. Importa tus capturas autorizadas y exporta CSV o GeoJSON antes de cerrar. La sesión vive en memoria.

**Pruebas automatizadas — macOS/Linux:**

~~~bash
python3 -m unittest discover -s tests -v
~~~

**Windows:**

~~~powershell
py -3 -m unittest discover -s tests -v
~~~

## Arquitectura del repositorio

~~~text
Wardrive-Track/
├── README.md                 # Portada: última versión
├── CHANGELOG.md              # Histórico de versiones
├── run.py                    # Ejecutar desde Python
├── build.py                  # Compilar ejecutables con versión en el nombre
├── wardrive_track/
│   ├── __init__.py           # FUENTE ÚNICA: versión, creador y metadatos
│   ├── server.py             # API /api/about y recursos empaquetados
│   ├── core.py               # Inventario y coordenadas GPS
│   ├── parsers.py            # PCAP, PCAPNG, CSV, LOG, TXT, NMEA
│   └── radio.py              # WPA/RSN y anuncios BLE
├── web/                      # Interfaz HTML, CSS y JavaScript
├── examples/                 # Capturas de demostración sintéticas
├── tests/                    # Suite automatizada
├── scripts/verify_build.py   # Prueba el ejecutable REAL y el HTML
├── docs/                     # Manuales íntegramente en español
└── .github/workflows/        # Tests y compilaciones Windows/macOS/Linux
~~~

**Prevención de versiones antiguas:** tanto el ejecutable como la API, el diagnóstico y la web obtienen el número de versión de la misma fuente del código Python. El flujo de compilación verifica el binario real, que el HTML corresponde a v0.3.0 y que la demostración BLE funciona antes de publicar el paquete.

## Documentación profesional

- [Instalación paso a paso](docs/INSTALACION.md)
- [Actualizar desde v0.1 o v0.2](docs/ACTUALIZACION.md)
- [Cómo verificar la última versión](docs/ULTIMA_VERSION.md)
- [Descargar o crear ejecutables](docs/COMPILACION.md)
- [Manual de uso y filtros](docs/USO.md)
- [Compatibilidad ESP32 Marauder](docs/MARAUDER.md)
- [Solución de problemas](docs/SOLUCION_PROBLEMAS.md)
- [Historial de versiones](CHANGELOG.md)
- [Privacidad y seguridad](SECURITY.md)

**Seguridad:** solo capturas propias o autorizadas. Las direcciones y las coordenadas pueden ser sensibles. El mapa de calles utiliza recursos externos de Leaflet y OpenStreetMap cuando hay conexión; el plano esquemático no los necesita. No existe licencia abierta publicada, por lo que la reutilización queda sujeta a los derechos del titular.

---

**Wardrive Track v0.3.0 · © 2026 Fran Gonzas** · Proyecto independiente: no es software oficial de ESP32 Marauder.
