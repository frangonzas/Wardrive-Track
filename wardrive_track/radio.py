"""Clasificación pasiva de seguridad Wi-Fi y anuncios Bluetooth LE.

No se intentan conexiones ni identificación de personas o geolocalización de MAC.
Todos los metadatos se obtienen exclusivamente de los archivos importados.
"""
from __future__ import annotations

import re
import struct


def security_from_text(value: object) -> str:
    """Normaliza la seguridad *declarada* por los CSV/logs."""
    raw = str(value or "").upper()
    if not raw or raw in ("UNKNOWN", "N/A", "NONE", "UNSPECIFIED", "NO DETERMINADA"):
        return "No determinada"
    if "WPA3" in raw and ("WPA2" in raw or "TRANSITION" in raw):
        return "WPA2/WPA3"
    if "WPA3" in raw or "SAE" in raw:
        return "WPA3"
    if "WPA2" in raw or "RSN" in raw:
        return "WPA2"
    if "WPA" in raw:
        return "WPA"
    if "WEP" in raw:
        return "WEP"
    if "OWE" in raw:
        return "OWE"
    if any(x in raw for x in ("OPEN", "ABIER", "SIN CIFRADO", "[ESS]", "UNSECURED")):
        return "OPEN"
    return "No determinada"


def _akm_suites(blob: bytes) -> list[int]:
    """Extrae IDs AKM del RSN IE; un IE truncado no se interpreta."""
    if len(blob) < 8:
        return []
    i = 2 + 4  # versión + group cipher
    if i + 2 > len(blob):
        return []
    pair_count = int.from_bytes(blob[i:i+2], "little")
    i += 2 + pair_count * 4
    if i + 2 > len(blob):
        return []
    akm_count = int.from_bytes(blob[i:i+2], "little")
    i += 2
    if akm_count > 32 or i + akm_count * 4 > len(blob):
        return []
    suites = []
    for j in range(akm_count):
        suite = blob[i+j*4:i+(j+1)*4]
        if suite[:3] == b"\x00\x0f\xac":
            suites.append(suite[3])
    return suites


def security_from_ies(capabilities: int, ies: bytes) -> str:
    """Identifica OPEN/WEP/WPA/WPA2/WPA3 a partir de beacon/probe-response.

    WPA2+WPA3 mixto se anuncia mediante AKM PSK(2) y SAE(8). Si el IE RSN
    está presente pero no es completo, se informa RSN/WPA2 como aproximación
    de familia (el subtipo AKM no está confirmado).
    """
    privacy = bool(capabilities & 0x0010)
    rsn, wpa = None, False
    i = 0
    while i + 2 <= len(ies):
        eid, size = ies[i], ies[i+1]
        i += 2
        if i + size > len(ies):
            break
        value = ies[i:i+size]
        if eid == 48 and size >= 2:
            rsn = value
        elif eid == 221 and size >= 4 and value[:4] == b"\x00\x50\xf2\x01":
            wpa = True
        i += size
    if rsn is not None:
        akm = _akm_suites(rsn)
        has_sae = any(k in (8, 9, 24) for k in akm)
        has_psk = any(k in (2, 4, 6) for k in akm)
        if 18 in akm:
            return "OWE"
        if has_sae and has_psk:
            return "WPA2/WPA3"
        if has_sae or any(k in (11, 12, 13) for k in akm):
            return "WPA3"
        return "WPA2"
    if wpa:
        return "WPA"
    if privacy:
        return "WEP"  # herencia; otros esquemas propietarios quedan fuera
    return "OPEN"


def protocol_from_text(value: object, fallback: str = "Wi-Fi") -> str:
    text = str(value or "").strip().upper()
    if text in ("BLE", "BTLE", "BLUETOOTH LE", "BLUETOOTH LOW ENERGY", "LE"):
        return "BLE"
    if text in ("BT", "BLUETOOTH", "BLUETOOTH CLASSIC", "BR/EDR", "CLASSIC"):
        return "Bluetooth"
    if text in ("WIFI", "WI-FI", "80211", "802.11", "WLAN", ""):
        return fallback
    return fallback


def _ad_name(data: bytes) -> str:
    """Campos AD 0x09 (complete) y 0x08 (shortened)."""
    full, short = "", ""
    i = 0
    while i < len(data):
        length = data[i]
        i += 1
        if length == 0 or i + length > len(data):
            break
        tag = data[i]
        value = data[i+1:i+length]
        if tag in (8, 9):
            name = value.decode("utf-8", "replace").replace("\x00", "").strip()[:100]
            if tag == 9:
                full = name
            else:
                short = name
        i += length
    return full or short


def _mac_from_air(raw: bytes) -> str:
    return ":".join(f"{x:02X}" for x in raw[::-1])


def ble_hci_frame(packet: bytes, linktype: int, ts: float | None) -> list[dict]:
    """Extrae anuncios BLE de HCI H4 (201) o HCI H4 con pseudo-header (187).

    Ambos formatos son comunes en volcados de controladores; no se atribuye
    soporte a todos los PCAP Bluetooth. No se procesa tráfico de datos.
    """
    if linktype == 187:
        if len(packet) < 5:
            return []
        packet = packet[4:]
    if linktype not in (187, 201) or len(packet) < 4 or packet[0] != 4:
        return []
    if packet[1] != 0x3E:  # LE Meta Event
        return []
    n = packet[2]
    payload = packet[3:3+n]
    if len(payload) < 2 or payload[0] != 2:  # LE Advertising Report
        return []
    reports = payload[1]
    pos = 2
    output = []
    for _ in range(min(reports, 64)):
        if pos + 9 > len(payload):
            break
        event_type, addr_type = payload[pos], payload[pos+1]
        address = _mac_from_air(payload[pos+2:pos+8])
        length = payload[pos+8]
        pos += 9
        if pos + length + 1 > len(payload):
            break
        advertisement = payload[pos:pos+length]
        rssi = struct.unpack_from("<b", payload, pos+length)[0]
        pos += length + 1
        if address == "00:00:00:00:00:00":
            continue
        output.append({
            "bssid": address, "ssid": _ad_name(advertisement),
            "protocol": "BLE", "security": "No aplica",
            "rssi": rssi, "channel": None, "ts": ts,
            "lat": None, "lon": None,
            "address_type": "Aleatoria" if addr_type else "Pública",
        })
    return output
