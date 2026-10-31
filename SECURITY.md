# Seguridad, privacidad y límites

Wardrive Track v0.2 es una herramienta de análisis **pasivo y local**. Abre capturas guardadas por el usuario y presenta observaciones Wi-Fi, Bluetooth/BLE y GPS. No inicia conexiones radio ni ejecuta ataques, descifrado, escucha activa o seguimiento de dispositivos.

## Datos que pueden ser sensibles

Los archivos de entrada pueden incluir SSID, BSSID, direcciones Bluetooth, nombres publicitados, intensidad de señal, hora y coordenadas GPS. Los identificadores y coordenadas pueden estar vinculados a personas. No publiques capturas ni exportaciones reales sin revisar cuidadosamente su contenido.

**Bluetooth:** las direcciones BLE pueden ser aleatorias y rotar. Wardrive Track no atribuye una identidad persistente a un MAC ni identifica al titular de un dispositivo. El mapa describe dónde se observó una señal, nunca una localización precisa del emisor.

## Aislamiento y red

- El servidor Python escucha únicamente en **127.0.0.1**.
- Se valida la cabecera **Host** y los orígenes de solicitudes de escritura.
- Las capturas permanecen en memoria de la aplicación, sin subida automática.
- Cada archivo está limitado a **32 MiB**.
- Los CSV exportados neutralizan prefijos que algunos programas de hojas de cálculo ejecutarían como fórmulas.
- Los nombres SSID/BLE se insertan en la interfaz mediante **textContent** (no como HTML).
- El modo mapa de calles requiere **Leaflet** desde un CDN y teselas de **OpenStreetMap**. Esas solicitudes externas pueden revelar la región del mapa consultada y direcciones IP. Para evitarlo, trabaja sin conexión y utiliza el mapa esquemático local.

## Precauciones

Importa solo capturas autorizadas. Si vas a compartir GeoJSON, elimina primero coordenadas, fechas e identificadores no necesarios. No publiques tokens, contraseñas, sesiones ni capturas con contenido sensible en GitHub.

No expongas el servidor mediante proxies, reenvío de puertos o túneles. Ejecuta siempre la versión del proyecto que corresponda a una revisión de confianza.

## Divulgación responsable

Para informar de una vulnerabilidad, contacta con el responsable del repositorio de forma privada antes de publicar un informe explotable, una captura o información personal.

Esta aplicación es un proyecto de software en desarrollo; no implica una auditoría formal de ciberseguridad o cumplimiento legal.
