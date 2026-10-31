# Manual de usuario — Wardrive Track 0.3.0

**Creador: Fran Gonzas.** La versión debe verse en la parte superior de la interfaz. Comprueba la instalación con el comando --version antes de importar archivos.

## 1. Abrir la aplicación

Instala Python 3.10+ y Git, clona el repositorio y ejecútalo con **python3 run.py** en macOS/Linux o **py -3 run.py** en Windows. El navegador abre un servidor local (127.0.0.1) creado por la aplicación.

Para una instalación completa, consulta [INSTALACION.md](INSTALACION.md).

## 2. Cargar datos

En el menú lateral, pulsa **Importar capturas** o arrastra uno o varios archivos al área indicada:

- **.pcap/.pcapng:** beacons/probe-response Wi-Fi (linktype 105 o Radiotap 127), anuncios BLE HCI H4 (linktype 187/201).
- **.csv:** WiGLE 1.6 o CSV estructurado con cabeceras reconocibles (MAC, SSID, RSSI, AuthMode, CurrentLatitude, CurrentLongitude, Type).
- **.log/.txt:** registros estructurados con pares clave=valor, JSON por línea o sentencias NMEA RMC.

La importación agrega registros a la sesión y recalcula el inventario. **Cargar demostración completa** sustituye la sesión actual por cinco archivos sintéticos; **Vaciar sesión** borra la memoria.

Cada importación devuelve un resumen y advertencias de formatos no reconocidos. No significa que todos los PCAP contengan tramas útiles.

## 3. Leer los indicadores

- **Total identificadores:** número de combinaciones distintas de tecnología + dirección MAC observada.
- **Redes Wi-Fi:** identificadores BSSID de AP detectados.
- **BLE / Bluetooth:** identificadores anunciados por esas tecnologías; un mismo dispositivo puede usar direcciones cambiantes.
- **Con geolocalización:** registros del inventario con al menos una observación GPS.
- **Observaciones:** número de registros importados, incluidos repetidos.
- **Puntos GPS:** posiciones explícitas de los registros importados.
- **Archivos:** fuentes importadas en la sesión.

## 4. Seguridad y clasificación Wi-Fi

La gráfica resume los recuentos de seguridad en redes Wi-Fi. Cada red tiene una clasificación **OPEN**, **WEP**, **WPA**, **WPA2**, **WPA2/WPA3**, **WPA3**, **OWE** o **No determinada**, cuando los beacons o CSV contienen información suficiente. No es un test de vulnerabilidad.

Bluetooth no utiliza WPA/WPA2/WPA3; sus filas muestran un guion en esa columna. El filtro de seguridad limita la vista a redes Wi-Fi que coincidan.

Consulta [MARAUDER.md](MARAUDER.md) para más detalles sobre formatos y cómo se obtiene la etiqueta de seguridad.

## 5. Filtros combinados del explorador

Debajo del mapa, el bloque **Inventario de radio** incluye seis controles:

| Filtro | Qué hace |
|---|---|
| **Buscar nombre / MAC** | Busca texto en SSID, nombre Bluetooth, MAC y protocolo |
| **Tecnología** | Todas / Wi-Fi / BLE / Bluetooth clásico |
| **Seguridad Wi-Fi** | Todos / OPEN / WEP / WPA / WPA2 / WPA2-WPA3 mixto / WPA3 / OWE / No determinada |
| **GPS** | Todos / Con GPS / Sin GPS |
| **Señal (dBm)** | Todos / fuerte (≥ −60) / media (−80 a −61) / débil (< −80) / no disponible |
| **Ordenar** | Mayor señal / nombre A–Z / cantidad de observaciones / más reciente |

Los filtros se combinan y se reflejan en la **tabla y en los marcadores Wi-Fi/Bluetooth del mapa**. La ruta GPS de la sesión continúa visible para situar las observaciones. El botón **Restablecer filtros** devuelve los valores predeterminados.

Para mantener fluida la interfaz, la tabla muestra hasta 1.500 registros y el mapa hasta 4.500 marcadores, aunque el inventario completo queda disponible para exportar.

## 6. Coordenadas y límites de localización

Un marcador significa **punto donde la antena detectó la señal**. No determina dónde está el punto de acceso ni dónde se encuentra el dispositivo.

Si el registro contiene latitud/longitud, se respeta esa observación. Si no, se puede relacionar con un punto GPS importado **dentro de 8 segundos de la misma marca temporal**. Si no hay coincidencia, se mantiene **Sin GPS**.

Los relojes de PCAP y del GPS deben estar alineados. Las marcas de tiempo sin zona horaria se interpretan como UTC. El recorrido GPS se representa mediante la secuencia de los puntos con coordenadas.

El mapa de calles puede solicitar teselas de OpenStreetMap y recursos de Leaflet; si falla su carga o no hay conexión, el programa utiliza un **plano esquemático** sin fondo cartográfico.

## 7. Exportar

Selecciona **CSV** para inventario de redes o **GeoJSON** para puntos y trazado GPS.

- **Sin marcar «Exportar solo resultados filtrados»**: exporta toda la sesión procesada.
- **Con la casilla marcada**: exporta el inventario visible tras aplicar los filtros; en GeoJSON se mantiene la ruta GPS completa y solo se incluyen puntos de emisores que superan los filtros.
- CSV incluye registros sin GPS. GeoJSON solo incluye puntos con coordenadas válidas.

Las exportaciones CSV neutralizan posibles valores interpretados como fórmulas por hojas de cálculo.

## 8. Guardar y cerrar

La sesión se mantiene **en RAM**. Exporta antes de cerrar el programa. Pulsa **Ctrl+C** en la terminal para detener el servidor. Los archivos originales permanecen donde tú los hayas guardado.

## 9. Buenas prácticas

Importa únicamente datos para los que tengas autorización. Las MAC y coordenadas de redes y dispositivos Bluetooth son información potencialmente sensible. Las direcciones aleatorias BLE no proporcionan una identidad persistente. No publiques capturas de terceros, geolocalizaciones personales ni identificadores sin revisar.
