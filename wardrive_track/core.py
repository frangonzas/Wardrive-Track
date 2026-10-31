"""Sesiones de análisis Wi-Fi/Bluetooth y correlación GPS de observaciones.

No se infieren ubicaciones de puntos de acceso ni identidades Bluetooth.
"""
from __future__ import annotations

import bisect
import csv
import io
from collections import Counter
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from .parsers import MAX_RECORDS, parse_file

SYNC_SECONDS = 8
SECURITY_ORDER = ["OPEN", "WEP", "WPA", "WPA2", "WPA2/WPA3", "WPA3", "OWE", "No determinada"]


class Session:
    def __init__(self):
        self.lock = RLock()
        self.observations: list[dict] = []
        self.fixes: list[dict] = []
        self.files: list[dict] = []

    def reset(self):
        with self.lock:
            self.observations.clear()
            self.fixes.clear()
            self.files.clear()

    def import_data(self, name: str, data: bytes) -> dict:
        obs, gps, warnings = parse_file(name, data)
        with self.lock:
            n_obs = min(len(obs), max(0, MAX_RECORDS - len(self.observations)))
            n_gps = min(len(gps), max(0, MAX_RECORDS - len(self.fixes)))
            self.observations.extend(obs[:n_obs])
            self.fixes.extend(gps[:n_gps])
            if n_obs < len(obs) or n_gps < len(gps):
                warnings.append("Se alcanzó el límite de 60.000 registros por tipo.")
            types = Counter(o.get("protocol", "Wi-Fi") for o in obs[:n_obs])
            self.files.append({"name": name, "observations": n_obs, "gps": n_gps,
                               "wifi": types["Wi-Fi"], "ble": types["BLE"],
                               "bluetooth": types["Bluetooth"]})
            return {"filename": name, "observations": n_obs, "gps": n_gps,
                    "wifi": types["Wi-Fi"], "ble": types["BLE"],
                    "bluetooth": types["Bluetooth"], "warnings": warnings}

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            observations = [r.copy() for r in self.observations]
            fixes = [r.copy() for r in self.fixes]
            files = [r.copy() for r in self.files]
        return aggregate(observations, fixes, files)


def iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    except (OverflowError, OSError, ValueError):
        return None


def aggregate(observations: list[dict], fixes: list[dict], files: list[dict] | None = None) -> dict:
    # El GPS ya asociado explícitamente prevalece siempre. La correlación
    # temporal sólo se aplica cuando hay tiempo y un punto cercano (< 8 s).
    timed = sorted((p for p in fixes if p["ts"] is not None), key=lambda p: p["ts"])
    times = [p["ts"] for p in timed]
    inventory: dict[tuple[str, str], dict] = {}
    located_sightings = 0
    for record in observations:
        r = record.copy()
        if (r.get("lat") is None or r.get("lon") is None) and r.get("ts") is not None and timed:
            pos = bisect.bisect_left(times, r["ts"])
            nearby = [timed[i] for i in (pos-1, pos) if 0 <= i < len(timed)]
            if nearby:
                closest = min(nearby, key=lambda p: abs(p["ts"] - r["ts"]))
                if abs(closest["ts"] - r["ts"]) <= SYNC_SECONDS:
                    r["lat"], r["lon"] = closest["lat"], closest["lon"]
        mac = r["bssid"]
        protocol = r.get("protocol", "Wi-Fi")
        if protocol not in ("Wi-Fi", "BLE", "Bluetooth"):
            protocol = "Wi-Fi"
        key = protocol, mac
        if key not in inventory:
            inventory[key] = {
                "bssid": mac, "ssid": r.get("ssid") or "(sin nombre)",
                "protocol": protocol, "security": r.get("security") or
                    ("No determinada" if protocol == "Wi-Fi" else "No aplica"),
                "rssi": r.get("rssi"), "rssi_min": r.get("rssi"),
                "channel": r.get("channel") if protocol == "Wi-Fi" else None,
                "address_type": r.get("address_type") or "No indicada",
                "count": 0, "located_count": 0, "lat": None, "lon": None,
                "first_seen": None, "last_seen": None,
                "_first_ts": None, "_last_ts": None, "_best_signal": -1000,
            }
        n = inventory[key]
        n["count"] += 1
        if r.get("ssid"):
            n["ssid"] = r["ssid"]
        if protocol == "Wi-Fi" and r.get("channel") is not None:
            n["channel"] = r["channel"]
        if protocol == "Wi-Fi" and r.get("security") not in (None, "", "No determinada"):
            n["security"] = r["security"]
        if r.get("address_type"):
            n["address_type"] = r["address_type"]
        if r.get("rssi") is not None:
            if n["rssi"] is None or r["rssi"] > n["rssi"]:
                n["rssi"] = r["rssi"]
            if n["rssi_min"] is None or r["rssi"] < n["rssi_min"]:
                n["rssi_min"] = r["rssi"]
        if r.get("ts") is not None:
            if n["_first_ts"] is None or r["ts"] < n["_first_ts"]:
                n["_first_ts"] = r["ts"]
                n["first_seen"] = iso(r["ts"])
            if n["_last_ts"] is None or r["ts"] > n["_last_ts"]:
                n["_last_ts"] = r["ts"]
                n["last_seen"] = iso(r["ts"])
        if r.get("lat") is not None and r.get("lon") is not None:
            n["located_count"] += 1
            located_sightings += 1
            signal = r["rssi"] if r.get("rssi") is not None else -999
            if n["lat"] is None or signal > n["_best_signal"]:
                n["lat"], n["lon"] = r["lat"], r["lon"]
                n["_best_signal"] = signal

    networks = []
    for n in inventory.values():
        for private in ("_first_ts", "_last_ts", "_best_signal"):
            n.pop(private, None)
        networks.append(n)
    networks.sort(key=lambda n: (n["lat"] is None, n["protocol"] != "Wi-Fi",
                                 -(n["rssi"] if n["rssi"] is not None else -999),
                                 n["ssid"].lower()))
    track = [{"lat": p["lat"], "lon": p["lon"], "timestamp": iso(p["ts"])}
             for p in sorted(fixes, key=lambda p: (p["ts"] is None, p["ts"] or 0))]
    types = Counter(n["protocol"] for n in networks)
    security = Counter(n["security"] for n in networks if n["protocol"] == "Wi-Fi")
    return {
        "networks": networks, "track": track, "files": files or [],
        "security": {name: security[name] for name in SECURITY_ORDER},
        "stats": {
            "networks": len(networks), "wifi": types["Wi-Fi"],
            "ble": types["BLE"], "bluetooth": types["Bluetooth"],
            "located": sum(n["lat"] is not None for n in networks),
            "sightings": len(observations), "located_sightings": located_sightings,
            "gps": len(fixes), "files": len(files or []),
        }, "sync_tolerance": SYNC_SECONDS,
    }


def as_geojson(data: dict) -> dict:
    features = []
    for n in data["networks"]:
        if n["lat"] is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [n["lon"], n["lat"]]},
            "properties": {key: value for key, value in n.items() if key not in ("lat", "lon")},
        })
    track = [p for p in data["track"] if p["lat"] is not None]
    if len(track) >= 2:
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[p["lon"], p["lat"]] for p in track]},
            "properties": {"name": "Recorrido GPS", "kind": "track"},
        })
    return {"type": "FeatureCollection", "features": features}


def _csv_safe(value):
    """Neutraliza el inicio de fórmulas en hojas de cálculo (CSV injection)."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def as_csv(data: dict) -> str:
    out = io.StringIO()
    columns = ["protocol", "bssid", "ssid", "security", "channel", "rssi",
               "rssi_min", "count", "located_count", "lat", "lon",
               "first_seen", "last_seen", "address_type"]
    writer = csv.DictWriter(out, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for network in data["networks"]:
        writer.writerow({key: _csv_safe(network.get(key, "")) for key in columns})
    return out.getvalue()
