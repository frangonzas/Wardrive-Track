# Contribuir a Wardrive Track

Gracias por ayudar a mejorar Wardrive Track. Se priorizan los cambios legibles, pequeños, verificables y compatibles con Windows, macOS y Linux.

## Preparar el entorno

~~~bash
git clone https://github.com/frangonzas/Wardrive-Track.git
cd Wardrive-Track
python3 --version
python3 -m unittest discover -s tests -v
~~~

En Windows sustituye **python3** por **py -3**. No se necesitan dependencias externas en Python.

## Reglas del proyecto

1. Evita dependencias nuevas salvo justificación técnica; conserva la privacidad y el procesamiento local.
2. Documenta el comportamiento en español y añade pruebas para nuevos formatos.
3. Nunca uses datos de localización de personas ni capturas reales de terceros como fixtures.
4. No infieras ubicaciones de BSSID a partir de fuentes no verificadas ni presentes en la captura.
5. Mantén compatibles las exportaciones CSV/GeoJSON y la semántica de las observaciones.
6. Antes de proponer un cambio, ejecuta las pruebas y comprueba la demostración.

## Proponer un cambio

Abre una incidencia describiendo el comportamiento esperado, reproduce el problema con datos sintéticos y envía un pull request con resumen, pruebas y cambios documentales. No incluyas secretos ni información sensible en issues o commits.

La licencia del código aún no está definida por el titular: antes de reutilizarlo o redistribuirlo, solicita autorización o espera a que se publique una licencia explícita.
