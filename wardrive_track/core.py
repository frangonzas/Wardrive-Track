"""Modelo de sesión y correlación temporal de observaciones Wi-Fi con GPS."""
from __future__ import annotations

import bisect
import csv
import io
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from .parsers import MAX_RECORDS, parse_file

SYNC_SECONDS = 8


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
                warnings.append("Límite de 60.000 registros por tipo alcanzado en la sesión.")
            self.files.append({"name": name, "observations": n_obs, "gps": n_gps})
            return {"filename": name, "observations": n_obs, "gps": n_gps, "warnings": warnings}

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
    # Solo coordenadas GPS con fecha se usan para correlación; un punto aislado
    # sin fecha se puede dibujar, pero no ubica redes por proximidad temporal.
    timed = sorted((p for p in fixes if p["ts"] is not None), key=lambda p: p["ts"])
    times = [p["ts"] for p in timed]
    networks = {}
    located_sightings = 0
    for record in observations:
        r = record.copy()
        if r["lat"] is None and r["ts"] is not None and timed:
            pos = bisect.bisect_left(times, r["ts"])
            nearby = [timed[i] for i in (pos-1, pos) if 0 <= i < len(timed)]
            if nearby:
                best = min(nearby, key=lambda p: abs(p["ts"] - r["ts"]))
                if abs(best["ts"] - r["ts"]) <= SYNC_SECONDS:
                    r["lat"], r["lon"] = best["lat"], best["lon"]
        bssid = r["bssid"]
        if bssid not in networks:
            networks[bssid] = {"bssid": bssid, "ssid": r.get("ssid") or "(oculta)",
                               "rssi": r.get("rssi"), "channel": r.get("channel"),
                               "security": r.get("security", "No determinada"),
                               "count": 0, "located_count": 0, "lat": None,
                               "lon": None, "last_seen": None, "_best_signal": -1000,
                               "_best_ts": -1}
        n = networks[bssid]
        n["count"] += 1
        if r.get("ssid"):
            n["ssid"] = r["ssid"]
        if r.get("channel") is not None:
            n["channel"] = r["channel"]
        if r.get("security"):
            n["security"] = r["security"]
        if r.get("rssi") is not None:
            if n["rssi"] is None or r["rssi"] > n["rssi"]:
                n["rssi"] = r["rssi"]
        if r.get("ts") is not None and r["ts"] > n["_best_ts"]:
            n["_best_ts"] = r["ts"]
            n["last_seen"] = iso(r["ts"])
        if r["lat"] is not None and r["lon"] is not None:
            located_sightings += 1
            n["located_count"] += 1
            # Coordenada de la observación de señal más alta, no posición real del AP.
            signal = r["rssi"] if r["rssi"] is not None else -999
            if n["lat"] is None or signal > n["_best_signal"]:
                n["lat"], n["lon"] = r["lat"], r["lon"]
                n["_best_signal"] = signal
    rows = []
    for n in networks.values():
        n.pop("_best_signal")
        n.pop("_best_ts")
        rows.append(n)
    rows.sort(key=lambda n: (n["lat"] is None, -(n["rssi"] if n["rssi"] is not None else -999), n["ssid"].lower()))
    track = [{"lat": p["lat"], "lon": p["lon"], "timestamp": iso(p["ts"])} for p in sorted(fixes, key=lambda p: (p["ts"] is None, p["ts"] or 0))]
    return {"networks": rows, "track": track, "files": files or [],
            "stats": {"networks": len(rows), "located": sum(n["lat"] is not None for n in rows),
                      "sightings": len(observations), "located_sightings": located_sightings,
                      "gps": len(fixes), "files": len(files or [])}, "sync_tolerance": SYNC_SECONDS}


def as_geojson(data: dict) -> dict:
    features = []
    for n in data["networks"]:
        if n["lat"] is None:
            continue
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [n["lon"], n["lat"]]},
                         "properties": {key: val for key, val in n.items() if key not in ("lat", "lon")}})
    track = [p for p in data["track"] if p["lat"] is not None]
    if len(track) >= 2:
        features.append({"type": "Feature", "geometry": {"type": "LineString",
                         "coordinates": [[p["lon"], p["lat"]] for p in track]},
                         "properties": {"name": "Recorrido GPS", "kind": "track"}})
    return {"type": "FeatureCollection", "features": features}


def as_csv(data: dict) -> str:
    out = io.StringIO()
    columns = ["bssid", "ssid", "rssi", "channel", "security", "count", "located_count", "lat", "lon", "last_seen"]
    writer = csv.DictWriter(out, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(data["networks"])
    return out.getvalue()
