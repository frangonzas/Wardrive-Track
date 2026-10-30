# Manual de usuario

## Objetivo

Wardrive Track procesa **archivos previamente capturados** y permite explorar redes Wi-Fi observadas, asociadas con coordenadas proporcionadas por una fuente GPS. **No captura tráfico por sí mismo** y **no consulta ninguna base de geolocalización de routers**.

## Flujo recomendado

1. Inicia el programa con **python3 run.py** (o **py -3 run.py** en Windows).
2. Pulsa **Cargar demostración** y familiarízate con el panel.
3. Selecciona **Importar archivos** o arrastra archivos al recuadro de importación.
4. Importa primero tu captura **.pcap/.pcapng** y después el archivo **.log/.txt/.csv** con GPS. El orden no es obligatorio; el motor recalcula los cruces.
5. Consulta las tarjetas de métricas, el mapa y el inventario de redes.
6. Utiliza el buscador y los filtros para localizar BSSID/SSID.
7. Exporta los resultados antes de cerrar el programa.

## Cómo relaciona Wi-Fi y GPS

Una captura 802.11 puede incluir SSID, BSSID y fecha/hora. Los registros GPS pueden incluir latitud, longitud y fecha/hora. El programa asocia una observación Wi-Fi con el punto GPS de tiempo más cercano si la diferencia es **igual o inferior a 8 segundos**. No interpola posiciones ni infiere coordenadas a partir del BSSID.

**Ejemplo de un archivo de registro de texto compatible:**

~~~text
2026-10-29T12:00:00Z GPS lat=40.41680 lon=-3.70380
2026-10-29T12:00:03Z BSSID=02:AA:BB:CC:DD:01 SSID="Mi_Lab" RSSI=-48 channel=6
~~~

Las marcas de tiempo sin zona horaria se interpretan como **UTC**, no como hora local.

## Interpretación de los resultados

- **Redes detectadas:** BSSID únicos procesados.
- **Redes con GPS:** redes con alguna observación asociada a coordenadas.
- **Observaciones:** apariciones procesadas en los archivos.
- **Puntos de ruta:** coordenadas GPS extraídas.
- **Marcadores del mapa:** lugar desde el que se observó una señal; no la localización garantizada del router.
- **Recorrido GPS:** secuencia de puntos importados.
- **RSSI:** nivel de señal recibido; no debe interpretarse como distancia exacta.

Cuando un BSSID tiene varias observaciones georreferenciadas, se muestra la correspondiente a la señal más fuerte (si existe RSSI).

## Exportaciones

**CSV:** inventario de redes, con columnas BSSID, SSID, RSSI, canal, seguridad anunciada, número de observaciones, coordenadas de observación y fecha de última detección. Incluye redes sin GPS.

**GeoJSON:** entidades Point para redes georreferenciadas y LineString para el recorrido GPS si existen al menos dos puntos. Las redes sin coordenadas no aparecen como puntos ficticios.

## Archivos compatibles

- **PCAP/PCAPNG:** tramas beacon o probe response 802.11 en interfaces compatibles. Los PCAP Ethernet normales no son equivalentes a capturas Wi-Fi en modo monitor.
- **LOG/TXT:** registros por línea con campos clave/valor, JSON y sentencias NMEA RMC.
- **CSV:** cabeceras reconocibles de BSSID, MAC, SSID, RSSI, latitud y longitud; compatible con WiGLE 1.6.

## Datos de prueba

La carpeta **examples/** contiene un PCAP, un log GPS y un CSV WiGLE **sintéticos**. La opción **Cargar demostración** carga automáticamente estos archivos y reemplaza la sesión actual.

## Privacidad y límites

La información importada permanece en la memoria del proceso local, no se guarda automáticamente. Cada archivo admite **hasta 32 MiB** y hay un límite de **60.000 registros por tipo** en la sesión. El mapa de calles depende de recursos externos (Leaflet/OpenStreetMap); si necesitas evitar sus solicitudes, trabaja sin conexión con el plano esquemático.

Utiliza únicamente archivos obtenidos con permiso y evita compartir capturas o ubicaciones identificables.
