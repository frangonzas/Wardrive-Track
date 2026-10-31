# Wardrive Track

![Python · Windows macOS Linux](https://img.shields.io/badge/Python-3.10%2B-3977b8?logo=python&logoColor=white)
![Versión](https://img.shields.io/badge/versi%C3%B3n-0.2.0-17af90)
![Pruebas multiplataforma](https://github.com/frangonzas/Wardrive-Track/actions/workflows/tests.yml/badge.svg)
![Licencia](https://img.shields.io/badge/licencia-pendiente-lightgrey)

**Explorador local de observaciones Wi-Fi, Bluetooth y BLE, orientado a los archivos guardados por ESP32 Marauder.**

Wardrive Track convierte capturas **PCAP/PCAPNG** y registros **WiGLE 1.6/CSV/LOG/TXT** en un inventario visual de redes y anuncios Bluetooth, con clasificación de seguridad Wi-Fi, filtrado combinado, mapa de puntos GPS y exportación a **CSV/GeoJSON**.

**Windows · macOS · Linux · Python estándar (sin paquetes pip) · Interfaz en español · Datos procesados localmente.**

> **Importante:** no determina la posición física de un router ni de un dispositivo Bluetooth a partir de su MAC. Los puntos del mapa representan **lugares de observación** documentados mediante GPS; si el archivo no proporciona coordenadas, no se inventan. Algunas direcciones BLE son aleatorias y cambian; una dirección no equivale a una identidad estable.

## Instalación rápida

Necesitas **Python 3.10 o superior**, **Git** y un navegador.

### macOS

Abre **Terminal** y copia:

~~~bash
python3 --version
git --version
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 run.py
~~~

### Windows (PowerShell)

~~~powershell
py --version
git --version
cd $HOME
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
py -3 run.py
~~~

### Linux (Ubuntu / Debian)

~~~bash
sudo apt update
sudo apt install -y python3 git
cd ~
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 run.py
~~~

El programa abre su panel web en una URL local del tipo **http://127.0.0.1:PUERTO**. Si no se abre el navegador, copia esa URL desde la terminal. Para detenerlo pulsa **Ctrl+C**.

**No se requieren dependencias de Python ni instalación mediante pip.** Los mapas de calles utilizan Leaflet y teselas de OpenStreetMap a través de Internet; en ausencia de conexión se habilita un plano esquemático.

**Guías:** [Instalación paso a paso](docs/INSTALACION.md) · [Manual completo](docs/USO.md) · [Problemas frecuentes](docs/SOLUCION_PROBLEMAS.md).

## Novedades de la versión 0.2

| Módulo | Funcionalidad |
|---|---|
| **Wi-Fi** | SSID/BSSID, RSSI, canal, recuento y seguridad anunciada: OPEN, WEP, WPA, WPA2, WPA2/WPA3, WPA3 y OWE |
| **Bluetooth Low Energy (BLE)** | Direcciones MAC, nombres anunciados (si están presentes), RSSI, tipo de dirección HCI, GPS observado |
| **Bluetooth clásico** | Inventario de entradas BT etiquetadas explícitamente en CSV/LOG; no analiza tramas BR/EDR |
| **Filtros combinables** | Nombre o MAC, tecnología, protocolo de seguridad, presencia de GPS, rango de señal y ordenación |
| **Cartografía** | Marcadores Wi-Fi y Bluetooth diferenciados, línea de recorrido GPS, plano local sin Internet |
| **Exportaciones** | CSV y GeoJSON de la sesión completa o de los **resultados filtrados** |
| **Compatibilidad** | PCAP/PCAPNG Wi-Fi 802.11/Radiotap; anuncios BLE desde HCI H4 linktypes 187 y 201; CSV WiGLE 1.6, LOG, TXT y NMEA RMC |
| **Seguridad** | Servidor en 127.0.0.1, límite 32 MiB/archivo, CSV protegido ante fórmulas y ausencia de telemetría de capturas |

### Clasificación de seguridad Wi-Fi

Para tramas beacon/probe-response se analizan los **Information Elements** anunciados por el punto de acceso: bit de privacidad, **WPA vendor IE** y **RSN IE con suites AKM**. Se reconoce la transición WPA2/WPA3 (PSK + SAE), WPA3-SAE y OWE. Para CSV/LOG se normaliza el campo **AuthMode/Security** proporcionado por el origen.

Cuando no puede determinarse una categoría, se muestra **No determinada**. El cifrado anunciado **no es una prueba** de la seguridad efectiva de la red ni sustituye una auditoría.

### Bluetooth: qué significa realmente la información

Para anuncios **BLE**, la aplicación extrae datos de advertising HCI que estén presentes en el archivo: dirección, nombre publicitado y RSSI. Para registros **BT** marcados explícitamente, muestra sus metadatos. En Bluetooth el campo «Seguridad Wi-Fi» aparece **No aplica**. No se infiere fabricante, propietario, ubicación física ni identidad de la persona portadora.

## Tu primer análisis

1. Ejecuta **python3 run.py** (o **py -3 run.py** en Windows).
2. Selecciona **Cargar demostración completa**: contiene Wi-Fi, BLE, Bluetooth clásico y un recorrido GPS con datos sintéticos.
3. En **Inventario de radio**, prueba los filtros de **Tecnología**, **Seguridad Wi-Fi**, **GPS**, **RSSI** y la búsqueda por nombre/MAC.
4. Activa **Exportar solo resultados filtrados** si deseas guardar exactamente la selección del inventario. En caso contrario, CSV/GeoJSON incluyen toda la sesión.
5. Importa tus capturas y registros autorizados desde **Importar capturas**; puedes seleccionar varios archivos a la vez.
6. Exporta tus resultados antes de cerrar, porque la sesión se mantiene en memoria.

El archivo **.pcap** no incluye necesariamente datos GPS. Para asociar capturas sin coordenadas con una ruta GPS, los relojes deben estar sincronizados: la aplicación asigna el punto GPS **más cercano dentro de 8 segundos**, sin triangular ni consultar servicios de geolocalización de direcciones.

## Compatibilidad por formato

| Formato | Redes Wi-Fi | BLE | Bluetooth clásico | GPS |
|---|---|---|---|---|
| PCAP / PCAPNG con 802.11 o Radiotap | Beacon/probe-response | — | — | Mediante otro archivo sincronizado |
| PCAP / PCAPNG HCI H4 linktype 187/201 | — | LE Advertising Report | — | Mediante otro archivo sincronizado |
| WiGLE 1.6 CSV con Type=WIFI/BLE/BT | Sí | Sí | Sí, si Type=BT | Sí, si existen coordenadas |
| LOG/TXT estructurado y registros de Marauder compatibles | Sí | Sí | Sí, si va etiquetado | Sí |
| NMEA RMC | — | — | — | Sí, ruta con posición/tiempo |

Los PCAP genéricos de Ethernet, todos los tipos de paquetes Bluetooth y formatos propietarios desconocidos **no** están soportados. Los campos admitidos varían entre versiones, firmware y modelos ESP32 Marauder. Si no aparece un nombre, no se rellena artificialmente.

Ejemplo de registro de texto admitido:

~~~text
2026-10-29T12:00:00Z GPS lat=40.41680 lon=-3.70380
2026-10-29T12:00:02Z BSSID=02:AA:BB:CC:DD:01 SSID="Laboratorio WiFi" RSSI=-48 channel=6 security=WPA2
2026-10-29T12:00:03Z BLE MAC=D2:11:22:33:44:55 name="Sensor de pruebas" RSSI=-64
~~~

Consulta [Formatos y datos de ESP32 Marauder](docs/MARAUDER.md) para información específica de sus funciones WiFi Wardrive, Bluetooth Wardrive y registros.

## Operaciones y pruebas

**Ejecutar sin abrir navegador:**

~~~bash
python3 run.py --no-browser
~~~

**Fijar el puerto:**

~~~bash
python3 run.py --port 8765
~~~

**Pruebas automatizadas:**

~~~bash
python3 -m unittest discover -s tests -v
~~~

**Actualizar desde GitHub** (en la carpeta de tu instalación):

~~~bash
git pull --ff-only
python3 run.py
~~~

En Windows sustituye **python3** por **py -3**. Se ejecutan pruebas de sintaxis y tests automáticos en **Windows, macOS y Linux** con Python 3.10 y 3.13 usando GitHub Actions.

## Estructura

~~~text
Wardrive-Track/
├── run.py                    # Arranque
├── wardrive_track/
│   ├── core.py               # Inventario y cruce temporal GPS
│   ├── parsers.py            # WiGLE, NMEA, PCAP y PCAPNG
│   ├── radio.py              # Clasificación WPA/WPA2/WPA3 y HCI BLE
│   └── server.py             # Servidor/API HTTP local
├── web/
│   ├── index.html            # Consola de análisis
│   ├── style.css             # Estilos responsivos
│   └── app.js                # Mapa, filtros y exportaciones
├── examples/                 # Datos de prueba sintéticos
├── tests/                    # Suite automatizada
├── docs/                     # Manuales en español
├── .github/workflows/        # CI multiplataforma
└── README.md
~~~

## Privacidad, ética y límites

- Analiza exclusivamente **capturas y registros que poseas y estés autorizado a usar**.
- Las MAC, los nombres de dispositivos Bluetooth y las coordenadas pueden constituir información sensible. No publiques capturas reales sin anonimizar.
- Las direcciones BLE aleatorias pueden rotar; el inventario muestra **identificadores observados**, no personas ni necesariamente dispositivos únicos persistentes.
- Los resultados geográficos se refieren a **observaciones**. Una medición RSSI por sí sola no da distancia ni localización exacta.
- Las capturas permanecen en memoria mientras dura la sesión y no se suben a nuestros servidores. **Leaflet y OpenStreetMap son servicios de visualización externos** cuando el mapa de calles está activo y pueden recibir peticiones de teselas de la región visualizada.
- Hasta **32 MiB por archivo** y **60.000 registros por tipo de sesión** (observaciones / GPS). La tabla y el mapa limitan el volumen dibujado para mantener la fluidez.
- No ofrece ataques, descifrado de contraseñas, captura activa, asociación automática de clientes ni búsqueda de personas.
- Esta versión **no ha sido sometida a auditoría de seguridad independiente**.

## Proyecto y contribuciones

[Historial de cambios](CHANGELOG.md) · [Contribuir](CONTRIBUTING.md) · [Seguridad](SECURITY.md) · [Estado de las pruebas](https://github.com/frangonzas/Wardrive-Track/actions)

**Licencia:** aún no se ha publicado ninguna licencia explícita. Hasta que el propietario del repositorio añada una, se mantienen todos los derechos reservados. La disponibilidad pública del código no implica permiso automático para redistribuirlo.

**Proyecto independiente**: Wardrive Track es un lector de archivos, no firmware ESP32 Marauder ni una afiliación oficial con sus desarrolladores.
