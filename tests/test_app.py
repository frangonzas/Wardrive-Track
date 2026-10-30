import json
import struct
import unittest
from datetime import datetime, timezone
from pathlib import Path

from wardrive_track.core import Session, aggregate, as_csv, as_geojson
from wardrive_track.parsers import _pcapng, coordinate, parse_file, read_text, timestamp

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


class ParserTests(unittest.TestCase):
    def test_wigle_csv_header_preamble(self):
        obs, gps, errors = parse_file("ejemplo_wigle.csv", (EXAMPLES / "ejemplo_wigle.csv").read_bytes())
        self.assertEqual(len(obs), 4)
        self.assertEqual(len(gps), 4)
        self.assertEqual(obs[0]["bssid"], "02:11:22:33:44:55")
        self.assertEqual(obs[1]["rssi"], -42)
        self.assertEqual(errors, [])

    def test_log_timestamp_and_nmea(self):
        obs, fixes, warnings = read_text(b"2026-10-29T12:00:04Z GPS lat=40.4 lon=-3.7\n")
        self.assertFalse(obs)
        self.assertEqual(len(fixes), 1)
        self.assertEqual(fixes[0]["lat"], 40.4)
        nmea = b"$GPRMC,120004.00,A,4025.0080,N,00342.2280,W,0.0,0.0,291026,,,A*00\n"
        _, fixes, _ = read_text(nmea)
        self.assertEqual(len(fixes), 1)
        self.assertAlmostEqual(fixes[0]["lat"], 40.4168, places=3)
        self.assertLess(fixes[0]["lon"], 0)

    def test_pcap_extraction(self):
        obs, gps, warnings = parse_file("captura_ejemplo.pcap", (EXAMPLES / "captura_ejemplo.pcap").read_bytes())
        self.assertEqual(len(obs), 4)
        self.assertEqual(gps, [])
        self.assertEqual(obs[0]["ssid"], "DEMO_PCAP_A")
        self.assertEqual(obs[1]["rssi"], -41)
        self.assertEqual(obs[2]["channel"], 11)
        self.assertEqual(warnings, [])

    def test_pcapng_blocks(self):
        orig = (EXAMPLES / "captura_ejemplo.pcap").read_bytes()
        frame = orig[40:]
        frame = frame[:struct.unpack_from("<I", orig, 32)[0]]
        def block(kind, body):
            padded = body + b"\0" * ((-len(body)) % 4)
            n = len(padded) + 12
            return struct.pack("<II", kind, n) + padded + struct.pack("<I", n)
        shb = block(0x0a0d0d0a, struct.pack("<IHHq", 0x1a2b3c4d, 1, 0, -1))
        idb = block(1, struct.pack("<HHI", 127, 0, 65535))
        ts = int(datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc).timestamp() * 1e6)
        epb = block(6, struct.pack("<IIIII", 0, ts >> 32, ts & 0xffffffff, len(frame), len(frame)) + frame)
        obs, warnings = _pcapng(shb + idb + epb)
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0]["ssid"], "DEMO_PCAP_A")
        self.assertEqual(warnings, [])

    def test_invalid_and_no_inferred_coordinates(self):
        self.assertIsNone(coordinate("not", "2"))
        self.assertIsNone(timestamp("invalid"))
        obs, fixes, errors = parse_file("ether.pcap", b"bad data")
        self.assertEqual(obs, [])
        self.assertTrue(errors)
        d = aggregate([{"bssid": "02:00:00:00:00:01", "ssid": "Test",
                        "rssi": -55, "channel": 1, "ts": 100.0,
                        "lat": None, "lon": None}], [])
        self.assertEqual(d["stats"]["located"], 0)
        self.assertEqual(as_geojson(d)["features"], [])


class IntegrationTests(unittest.TestCase):
    def test_merge_capture_and_gps(self):
        session = Session()
        a = session.import_data("captura_ejemplo.pcap", (EXAMPLES / "captura_ejemplo.pcap").read_bytes())
        self.assertEqual(a["observations"], 4)
        first = session.snapshot()
        self.assertEqual(first["stats"]["located"], 0)
        session.import_data("ruta_gps.log", (EXAMPLES / "ruta_gps.log").read_bytes())
        after = session.snapshot()
        self.assertEqual(after["stats"]["gps"], 5)
        self.assertEqual(after["stats"]["networks"], 3)
        self.assertEqual(after["stats"]["located"], 2)
        self.assertEqual(after["stats"]["located_sightings"], 3)
        without = [n for n in after["networks"] if n["ssid"] == "DEMO_SIN_GPS"][0]
        self.assertIsNone(without["lat"])
        self.assertIn("DEMO_PCAP_A", as_csv(after))
        self.assertEqual(len(as_geojson(after)["features"]), 3)

    def test_demo_full(self):
        s = Session()
        for path in EXAMPLES.iterdir():
            if path.suffix in (".pcap", ".csv", ".log"):
                s.import_data(path.name, path.read_bytes())
        result = s.snapshot()
        self.assertEqual(result["stats"]["networks"], 6)
        self.assertEqual(result["stats"]["located"], 5)
        self.assertEqual(result["stats"]["sightings"], 8)
        self.assertEqual(len(result["files"]), 3)
        json.dumps(result, allow_nan=False)
        s.reset()
        self.assertEqual(s.snapshot()["stats"]["networks"], 0)


if __name__ == "__main__":
    unittest.main()
