"""Wardrive Track — inventario local Wi-Fi y Bluetooth/BLE.

Una única fuente de versión para la aplicación, CLI, API y compilaciones.
"""
APP_NAME = "Wardrive Track"
CREATOR = "Fran Gonzas"
__version__ = "0.3.0"
RELEASE_DATE = "2026-10-31"
REPOSITORY = "https://github.com/frangonzas/Wardrive-Track"

def metadata() -> dict[str, str]:
    """Datos oficiales de la versión de la instalación en ejecución."""
    return {
        "name": APP_NAME,
        "version": __version__,
        "creator": CREATOR,
        "release_date": RELEASE_DATE,
        "repository": REPOSITORY,
    }
