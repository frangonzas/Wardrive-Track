"""Lectores de PCAP/PCAPNG, registros GPS, NMEA y CSV WiGLE sin dependencias.

Todas las marcas de tiempo devueltas son segundos UTC (Unix). Las fechas sin
zona horaria se interpretan como UTC. El GPS se conserva solo si es explícito.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .radio import ble_hci_frame, protocol_from_text, security_from_ies, security_from_text

MAX_RECORDS = 60000


def timestamp(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, (int, float)) or re.fullmatch(r"\d{10}(?:\.\d+)?|\d{13}", str(value).strip()):
        x = float(value)
        return x / 1000 if x > 1e11 else x
    s = str(value).strip()
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def coordinate(lat: Any, lon: Any) -> tuple[float, float] | None:
    try:
        a, b = float(lat), float(lon)
        if math.isfinite(a) and math.isfinite(b) and -90 <= a <= 90 and -180 <= b <= 180:
            return a, b
    except (ValueError, TypeError, OverflowError):
        pass
    return None


def number(v: Any) -> int | None:
    try:
        return int(float(v)) if str(v).strip() else None
    except (ValueError, TypeError, OverflowError):
        return None


def normalize_mac(value: Any) -> str | None:
    s = re.sub(r"[^0-9a-fA-F]", "", str(value or ""))
    if len(s) != 12:
        return None
    return ":".join(s[i:i+2] for i in range(0, 12, 2)).upper()


def _record(row: dict[str, Any], default_protocol: str = 'Wi-Fi') -> tuple[dict | None, dict | None]:
    r = {re.sub(r"[^a-z0-9]", "", str(k).lower()): v for k, v in row.items() if k is not None}
    def get(*aliases):
        for key in aliases:
            v = r.get(key)
            if v is not None and str(v).strip():
                return v
        return None
    lat = get("lat", "latitude", "currentlatitude", "gpslat")
    lon = get("lon", "lng", "longitude", "currentlongitude", "gpslon")
    coords = coordinate(lat, lon)
    t = timestamp(get("time", "timestamp", "ts", "firstseen", "datetime", "date", "utc"))
    fix = {"lat": coords[0], "lon": coords[1], "ts": t} if coords else None
    typ = protocol_from_text(get("type", "networktype", "protocol", "radio"), default_protocol)
    mac = normalize_mac(get("bssid", "mac", "netid", "ap"))
    obs = None
    if mac:
        obs = {"bssid": mac, "ssid": str(get("ssid", "name", "devicename", "localname") or ""),
               "protocol": typ,
               "security": security_from_text(get("authmode", "security", "encryption", "auth")) if typ == "Wi-Fi" else "No aplica",
               "rssi": number(get("rssi", "signal", "dbm")),
               "channel": number(get("channel", "ch")), "ts": t,
               "lat": coords[0] if coords else None,
               "lon": coords[1] if coords else None}
    return obs, fix


def _nmea_coord(raw: str, hemi: str) -> float | None:
    try:
        x = float(raw)
        degree = int(x // 100)
        result = degree + (x - degree * 100) / 60
        if hemi in ("S", "W"):
            result *= -1
        return result
    except (ValueError, TypeError):
        return None


def _nmea(line: str) -> dict | None:
    start = line.find("$")
    if start < 0:
        return None
    fields = line[start:].split("*")[0].split(",")
    if len(fields) < 10 or not fields[0].endswith("RMC") or fields[2] != "A":
        return None
    lat = _nmea_coord(fields[3], fields[4])
    lon = _nmea_coord(fields[5], fields[6])
    coords = coordinate(lat, lon)
    if not coords:
        return None
    ts = None
    try:
        date = fields[9]
        hour = fields[1]
        year = 2000 + int(date[4:6]) if int(date[4:6]) < 80 else 1900 + int(date[4:6])
        dt = datetime(year, int(date[2:4]), int(date[:2]), int(hour[:2]),
                      int(hour[2:4]), int(float(hour[4:])), tzinfo=timezone.utc)
        ts = dt.timestamp()
    except (ValueError, IndexError):
        pass
    return {"lat": coords[0], "lon": coords[1], "ts": ts}


KV_RE = re.compile(r'(?P<key>[A-Za-z_][\w.-]*)\s*[:=]\s*(?:"(?P<quoted>[^"]*)"|(?P<unquoted>[^\s,;]+))')
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b")


def read_text(data: bytes, default_protocol: str = 'Wi-Fi') -> tuple[list[dict], list[dict], list[str]]:
    content = data.decode("utf-8-sig", errors="replace")
    lines = content.splitlines()
    observations: list[dict] = []
    fixes: list[dict] = []
    warnings: list[str] = []
    if not lines:
        return observations, fixes, ["Archivo de texto vacío."]
    header_i = 0
    for i, line in enumerate(lines[:4]):
        if re.search(r"(?:^|,)\s*(?:MAC|BSSID|NetID)\s*,", line, re.I):
            header_i = i
            break
    header = lines[header_i].lower()
    looks_csv = "," in header and ("mac" in header or "bssid" in header or "latitude" in header or "lat" in header)
    if looks_csv:
        reader = csv.DictReader(io.StringIO("\n".join(lines[header_i:])))
        for idx, row in enumerate(reader):
            if idx >= MAX_RECORDS:
                warnings.append("Límite de filas alcanzado; se omitió el resto.")
                break
            obs, fix = _record(row, default_protocol)
            if obs:
                observations.append(obs)
            if fix:
                fixes.append(fix)
    else:
        for idx, line in enumerate(lines):
            if idx >= MAX_RECORDS:
                warnings.append("Límite de líneas alcanzado; se omitió el resto.")
                break
            s = line.strip()
            if not s:
                continue
            fix = _nmea(s)
            if fix:
                fixes.append(fix)
                continue
            obj = None
            if s.startswith("{"):
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, dict):
                        obj = parsed
                except (ValueError, TypeError):
                    pass
            if obj is None:
                obj = {m.group("key"): m.group("quoted") if m.group("quoted") is not None else m.group("unquoted")
                       for m in KV_RE.finditer(s)}
                if "timestamp" not in obj and "time" not in obj:
                    match = DATE_RE.search(s)
                    if match:
                        obj["timestamp"] = match.group(0)
            local_protocol = default_protocol
            if not any(k.lower() in ("type", "networktype", "protocol", "radio") for k in obj):
                if re.search(r"\b(?:BLE|BTLE)\b", s, re.I):
                    local_protocol = "BLE"
                elif re.search(r"\b(?:BLUETOOTH|BT)\b", s, re.I):
                    local_protocol = "Bluetooth"
            obs, fix2 = _record(obj, local_protocol)
            if obs:
                observations.append(obs)
            if fix2:
                fixes.append(fix2)
    if not observations and not fixes:
        warnings.append("No se encontraron redes ni coordenadas reconocibles en este texto.")
    return observations, fixes, warnings


# Los campos iniciales de Radiotap tienen alineaciones definidas por la especificación.
RADIOTAP_FIELDS = {
    0: (8, 8), 1: (1, 1), 2: (1, 1), 3: (2, 4), 4: (2, 2),
    5: (1, 1), 6: (1, 1), 7: (2, 2), 8: (2, 2), 9: (2, 2),
    10: (1, 1), 11: (1, 1), 12: (1, 1), 13: (1, 1),
    14: (2, 2), 15: (2, 2), 16: (1, 1), 17: (1, 1),
}


def _radiotap(packet: bytes) -> tuple[bytes, int | None, int | None]:
    if len(packet) < 8 or packet[0] != 0:
        return b"", None, None
    rt_len = struct.unpack_from("<H", packet, 2)[0]
    if rt_len < 8 or rt_len > len(packet):
        return b"", None, None
    off, present = 4, []
    for _ in range(16):
        if off + 4 > rt_len:
            return packet[rt_len:], None, None
        word = struct.unpack_from("<I", packet, off)[0]
        present.append(word)
        off += 4
        if not word & 0x80000000:
            break
    else:
        return packet[rt_len:], None, None
    rssi, freq = None, None
    for word_index, word in enumerate(present):
        for bit in range(31):
            if not (word & (1 << bit)):
                continue
            field = word_index * 32 + bit
            if field not in RADIOTAP_FIELDS:
                return packet[rt_len:], rssi, freq
            align, length = RADIOTAP_FIELDS[field]
            off += (-off) % align
            if off + length > rt_len:
                return packet[rt_len:], None, None
            if field == 5:
                rssi = struct.unpack_from("<b", packet, off)[0]
            if field == 3:
                freq = struct.unpack_from("<H", packet, off)[0]
            off += length
    return packet[rt_len:], rssi, freq


def _freq_to_channel(freq: int | None) -> int | None:
    if freq == 2484:
        return 14
    if freq and 2412 <= freq <= 2472:
        return (freq - 2407) // 5
    if freq and 5000 <= freq <= 5900:
        return (freq - 5000) // 5
    if freq and 5955 <= freq <= 7115:
        return (freq - 5950) // 5
    return None


def _wifi(packet: bytes, linktype: int, ts: float | None) -> dict | None:
    rssi, freq = None, None
    if linktype == 127:
        packet, rssi, freq = _radiotap(packet)
    elif linktype != 105:
        return None
    if len(packet) < 36:
        return None
    frame_control = int.from_bytes(packet[0:2], "little")
    # Solo beacons y probe-responses de AP. No se registran estaciones cliente.
    if (frame_control & 0xFC) not in (0x80, 0x50):
        return None
    mac = normalize_mac(packet[16:22].hex())
    if not mac:
        return None
    capabilities = int.from_bytes(packet[34:36], "little")
    ssid, channel = "", _freq_to_channel(freq)
    i = 36
    while i + 2 <= len(packet):
        tag, length = packet[i], packet[i+1]
        i += 2
        if i + length > len(packet):
            break
        value = packet[i:i+length]
        if tag == 0 and length <= 32:
            ssid = value.decode("utf-8", errors="replace")
        if tag == 3 and length == 1:
            channel = value[0]
        i += length
    return {"bssid": mac, "ssid": ssid, "rssi": rssi, "channel": channel,
            "security": security_from_ies(capabilities, packet[36:]), "protocol": "Wi-Fi",
            "ts": ts, "lat": None, "lon": None}


MAGICS = {b"\xd4\xc3\xb2\xa1": ("<", 1e6), b"\xa1\xb2\xc3\xd4": (">", 1e6),
          b"\x4d\x3c\xb2\xa1": ("<", 1e9), b"\xa1\xb2\x3c\x4d": (">", 1e9)}


def _pcap(data: bytes) -> tuple[list[dict], list[str]]:
    if len(data) < 24 or data[:4] not in MAGICS:
        return [], ["Cabecera PCAP no válida."]
    endian, divisor = MAGICS[data[:4]]
    linktype = struct.unpack_from(endian + "I", data, 20)[0] & 0xFFFF
    if linktype not in (105, 127, 187, 201):
        return [], [f"Linktype {linktype} no compatible: se requieren tramas 802.11, Radiotap o Bluetooth HCI H4."]
    observations: list[dict] = []
    off = 24
    while off + 16 <= len(data) and len(observations) < MAX_RECORDS:
        sec, fraction, captured, _original = struct.unpack_from(endian + "IIII", data, off)
        off += 16
        if captured > len(data) - off or captured > 8_000_000:
            break
        frame = data[off:off+captured]
        ts = sec + fraction / divisor
        if linktype in (187, 201):
            observations.extend(ble_hci_frame(frame, linktype, ts)[:MAX_RECORDS-len(observations)])
        else:
            obs = _wifi(frame, linktype, ts)
            if obs:
                observations.append(obs)
        off += captured
    return observations, ([] if observations else ["No se encontraron anuncios Wi-Fi o BLE compatibles."])


def _pcapng(data: bytes) -> tuple[list[dict], list[str]]:
    observations, warnings = [], []
    off, endian, interfaces = 0, "<", []
    while off + 12 <= len(data) and len(observations) < MAX_RECORDS:
        if data[off:off+4] == b"\x0a\x0d\x0d\x0a":
            if off + 12 > len(data):
                break
            bom = data[off+8:off+12]
            endian = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">" if bom == b"\x1a\x2b\x3c\x4d" else "?"
            if endian == "?":
                break
            interfaces = []
        kind, size = struct.unpack_from(endian + "II", data, off)
        if size < 12 or size % 4 or off + size > len(data):
            break
        if kind == 1 and size >= 20:
            linktype = struct.unpack_from(endian + "H", data, off+8)[0]
            resolution = 1e6
            p = off + 16
            while p + 4 <= off + size - 4:
                code, length = struct.unpack_from(endian+"HH", data, p)
                p += 4
                if code == 0 or p + length > off + size - 4:
                    break
                if code == 9 and length == 1:
                    n = data[p]
                    resolution = (2 ** (n & 127)) if n & 128 else (10 ** n)
                p += (length + 3) & ~3
            interfaces.append((linktype, resolution))
        if kind == 6 and size >= 32:
            iface, hi, lo, caplen = struct.unpack_from(endian+"IIII", data, off+8)
            if iface < len(interfaces) and caplen <= size-32:
                linktype, resolution = interfaces[iface]
                ts = ((hi << 32) | lo) / resolution
                frame = data[off+28:off+28+caplen]
                if linktype in (187, 201):
                    observations.extend(ble_hci_frame(frame, linktype, ts)[:MAX_RECORDS-len(observations)])
                else:
                    obs = _wifi(frame, linktype, ts)
                    if obs:
                        observations.append(obs)
        off += size
    if not observations:
        warnings.append("No se encontraron anuncios Wi-Fi o BLE compatibles en PCAPNG.")
    return observations, warnings


def parse_file(filename: str, data: bytes) -> tuple[list[dict], list[dict], list[str]]:
    suffix = Path(filename).suffix.lower()
    if suffix in (".log", ".txt", ".csv"):
        return read_text(data, "BLE" if filename.lower().startswith(("bt_wardrive", "ble_", "bluetooth_")) else "Wi-Fi")
    if suffix == ".pcap":
        obs, warnings = _pcap(data)
        return obs, [], warnings
    if suffix == ".pcapng":
        obs, warnings = _pcapng(data)
        return obs, [], warnings
    return [], [], [f"Extensión no admitida: {suffix or '(sin extensión)'}"]
