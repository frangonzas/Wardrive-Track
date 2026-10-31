# Registro de cambios

## 0.2.0 — 2026-10-31

**Evolución Wi-Fi + Bluetooth/BLE con enfoque ESP32 Marauder.**

### Motor de análisis
- Clasificación de seguridad Wi-Fi por *Information Elements* 802.11: **OPEN, WEP, WPA, WPA2, WPA2/WPA3, WPA3 y OWE**.
- Importación de registros **WiGLE 1.6** con tecnologías **WIFI, BLE y BT** y de LOG/TXT Bluetooth estructurados.
- Decodificador básico de **BLE HCI H4 Advertising Report** en PCAP/PCAPNG con linktype 187 y 201; extrae dirección, tipo de dirección, nombre publicitado y RSSI.
- Inventario por **tecnología + MAC**, para evitar confundir Bluetooth y Wi-Fi.
- Estadísticas por radio, nuevas métricas de RSSI, fechas de primera/última observación y clasificación agregada de seguridad.
- Protección de valores CSV que puedan ejecutarse como fórmulas al abrir una hoja de cálculo.

### Interfaz
- Nueva consola responsiva con filtros combinables por nombre/MAC, radio, seguridad, GPS y señal; ordenación seleccionable.
- Marcadores Wi-Fi y Bluetooth diferenciados, recorrido GPS y modo de mapa esquemático.
- Exportaciones completas o limitadas a los filtros activos (CSV/GeoJSON).
- Demo con archivos sintéticos Wi-Fi, BLE y BT.

### Distribución y calidad
- Documentación completa en español para uso con archivos ESP32 Marauder.
- Pruebas unitarias de protocolos Wi-Fi/BT, compatibilidad de importación, API y restricciones de origen.
- GitHub Actions con sintaxis Python/JS y matriz Windows, macOS y Linux (Python 3.10/3.13).
- Empaquetado opcional con PyInstaller y compilaciones independientes para tres sistemas.

### Límites expresos
- Los BLE MAC aleatorios no se asocian a individuos ni a identidades persistentes.
- Sin escaneo activo, ni ataques, ni localización inferida desde un BSSID.
- Solo compatible con subconjuntos documentados de PCAP Bluetooth; no es un analizador general de HCI/BR-EDR.

## 0.1.0 — 2026-10-30

- Primera versión pública con PCAP/PCAPNG Wi-Fi 802.11, CSV WiGLE, GPS NMEA/LOG, correlación temporal, panel web local, mapa y exportación CSV/GeoJSON.
- Primer juego de ejemplos y pruebas automatizadas.
