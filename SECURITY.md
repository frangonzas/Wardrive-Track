# Seguridad y privacidad

Wardrive Track está diseñado para el análisis **local y pasivo de archivos** que el usuario ya posee. No ejecuta capturas activas, no fuerza autenticaciones, no analiza tráfico de clientes y no consulta proveedores externos para intentar ubicar BSSID.

## Superficie de exposición

- Servidor web HTTP vinculado a **127.0.0.1**, no a 0.0.0.0.
- Importaciones limitadas a tipos conocidos y **32 MiB por archivo**.
- No almacena capturas en disco: los datos importados quedan en memoria mientras la aplicación está abierta.
- No se recopilan telemetrías remotas de las capturas.
- **Excepción de red:** la interfaz puede descargar Leaflet y teselas OpenStreetMap si está conectada a Internet; el área visible del mapa puede ser conocida por ese servicio.

## Buenas prácticas

Utiliza el programa exclusivamente con capturas obtenidas legalmente y con autorización. No subas al repositorio PCAP reales, listados BSSID, ubicaciones o datos personales. Revisa los GeoJSON y CSV antes de compartirlos.

No expongas el servidor mediante proxies públicos o túneles. Si usas datos sensibles, desactiva Internet para visualizar un plano esquemático local.

## Notificación responsable de vulnerabilidades

Evita publicar detalles explotables o datos privados en incidencias públicas. Contacta de forma privada con el responsable del repositorio antes de divulgar una vulnerabilidad.

## Alcance de esta versión

Es una primera versión funcional, **no un producto auditado ni certificado**. Los archivos de captura son entradas no confiables: mantenlos dentro del tamaño admitido y usa fuentes verificadas.
