# ESP32 Marauder: guía de archivos compatibles

Wardrive Track **no se instala en el ESP32**: es una aplicación de escritorio para analizar los archivos que has guardado en la tarjeta SD o en tu ordenador.

## Funciones de Marauder y archivos resultantes

| Función en Marauder | Fuente | Interpretación en Wardrive Track |
|---|---|---|
| WiFi → Sniffers → **Scan APs / Beacon Sniff** | Capturas **.pcap** | SSID, BSSID y seguridad anunciada (si están presentes los IEs RSN/WPA); no tiene por qué contener GPS |
| WiFi → Sniffers → **Wardrive** | Registros **wardrive_...** (habitualmente WiGLE) | Coordenadas GPS vinculadas a las observaciones Wi-Fi |
| Bluetooth → Sniffers → **Bluetooth Wardrive** | Registros **bt_wardrive_...** | Dirección y nombre (si se registró), RSSI y coordenadas (si existen) |
| Volcados BLE HCI de herramientas compatibles | **.pcap / .pcapng** con linktype 187/201 | Anuncios BLE LE Advertising Report, nombres en AD structures y RSSI |
| Registros de GPS | **.log / .txt** o NMEA RMC | Ruta geográfica y posibilidad de cruce temporal con PCAP |

**Los nombres de menús, el tipo de archivo y los campos disponibles varían según el hardware y la versión del firmware.** Consulta el menú **help** del firmware y verifica cada archivo.

Fuentes originales del firmware:
- [Wardrive — documentación oficial de ESP32 Marauder](https://github.com/justcallmekoko/ESP32Marauder/wiki/wardrive).
- [Bluetooth Wardrive](https://github.com/justcallmekoko/ESP32Marauder/wiki/bluetooth-wardrive).
- [Scan APs](https://github.com/justcallmekoko/ESP32Marauder/wiki/Scan-APs).
- [Bluetooth Sniffers](https://github.com/justcallmekoko/ESP32Marauder/wiki/bluetooth-sniffers).

## Flujo recomendado para tus capturas

1. Obtén archivos Wi-Fi y, si tu dispositivo dispone de GPS, sus registros Wardrive.
2. Obtén **Bluetooth Wardrive** si la plataforma y el firmware lo soportan.
3. Copia los archivos a tu ordenador con un lector SD o medio de almacenamiento autorizado.
4. Inicia Wardrive Track.
5. Importa los archivos **sin transformar las fechas**; la correlación necesita marcas de tiempo coherentes.
6. Filtra por **Wi-Fi**, **BLE**, **Bluetooth clásico**, **WEP**, **WPA**, **WPA2** o **WPA3**.
7. Comprueba los puntos GPS y exporta los resultados.

## Filtrar WEP/WPA/WPA2/WPA3 con precisión

Los beacons Wi-Fi 802.11 anuncian estructuras de capacidades:
- **OPEN:** no se anuncia bit de privacidad ni estructuras RSN/WPA.
- **WEP:** bit de privacidad activado, sin estructuras WPA/RSN reconocidas (clasificación heredada, orientativa).
- **WPA:** antiguo Information Element WPA vendor-specific.
- **WPA2:** RSN Information Element con suites AKM no-WPA3.
- **WPA3:** suites AKM SAE o Enterprise de tipo reconocido.
- **WPA2/WPA3:** mezcla PSK + SAE anunciada en el mismo RSN IE.
- **OWE:** cifrado oportunista para redes de acceso abierto mejoradas.
- **No determinada:** el archivo no aporta información suficiente.

Un CSV WiGLE puede incluir el campo **AuthMode** con una descripción textual. Wardrive Track lo normaliza para el filtrado. Una etiqueta no garantiza la robustez de la configuración, y en Bluetooth no se utiliza la clasificación WPA.

## ¿Qué reconoce en Bluetooth?

- CSV WiGLE 1.6 con **Type=BLE** o **Type=BT**.
- LOG/TXT con campos **BLE**, **Bluetooth**, **MAC**, **name**, **RSSI**, **lat** y **lon**.
- Un archivo con prefijo **bt_wardrive**, **ble_** o **bluetooth_** puede servir como indicador de protocolo BLE en líneas que no incorporen Type explícito.
- Capturas HCI H4 (**linktype 201**; **187** con pseudo-header) que incluyan **LE Advertising Report** de tipo 0x02.

Por diseño, **no** implementa la interpretación completa de todos los formatos Bluetooth PCAP, intercambio de datos de conexión, BR/EDR ni identificación de personas mediante direcciones aleatorias.

## Modelos ESP32-C5 y diferencias de hardware

Los ESP32-C5 disponen de capacidades distintas de los antiguos ESP32 y no todas las funciones de escaneo aparecen en todos los binarios. Wardrive Track depende del **archivo obtenido**, no del nombre del modelo. La mejor validación es importar una muestra corta, confirmar sus campos y revisar las advertencias antes de registrar una sesión prolongada.

## Ejemplos

La carpeta **examples/** contiene registros sintéticos:
- **ejemplo_wigle.csv:** redes Wi-Fi y coordenadas.
- **captura_ejemplo.pcap:** beacon 802.11 y una red sin GPS.
- **ejemplo_bluetooth.csv:** anuncios BLE y un dispositivo BT etiquetado.
- **bt_wardrive_demo.log:** líneas BLE de ejemplo.
- **ruta_gps.log:** recorrido GPS.

Los ejemplos no identifican dispositivos reales.

## Límites y protección de datos

Si una entrada no contiene GPS, **no se coloca en el mapa** a menos que exista un punto GPS sincronizado en el margen permitido de ±8 segundos. Las direcciones BLE pueden rotar. Guarda los archivos SD originales de forma privada y exporta únicamente los datos que necesitas compartir.
