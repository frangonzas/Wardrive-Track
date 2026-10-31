"""Pruebas de la API local, exportaciones y controles de origen."""
from __future__ import annotations

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from wardrive_track.core import Session
from wardrive_track.server import Handler


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Handler.session = Session()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.address = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=5)

    def setUp(self):
        Handler.session.reset()

    def test_http_status_and_frontend(self):
        with urlopen(self.address + "/api/status", timeout=5) as response:
            data = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(data["stats"]["wifi"], 0)
        with urlopen(self.address, timeout=5) as response:
            html = response.read().decode()
            self.assertIn("Wardrive Track", html)
            self.assertIn("securityFilter", html)

    def test_demo_and_export(self):
        req = Request(self.address + "/api/demo", method="POST", data=b"")
        with urlopen(req, timeout=5) as response:
            report = json.loads(response.read())
            self.assertEqual(len(report["reports"]), 5)
        with urlopen(self.address + "/api/status", timeout=5) as response:
            data = json.loads(response.read())
            self.assertEqual(data["stats"]["networks"], 12)
            self.assertEqual(data["stats"]["wifi"], 6)
            self.assertEqual(data["stats"]["ble"], 5)
            self.assertEqual(data["stats"]["bluetooth"], 1)
            self.assertEqual(data["stats"]["located"], 9)
        with urlopen(self.address + "/api/export.csv", timeout=5) as response:
            content = response.read().decode("utf-8-sig")
            self.assertIn("protocol,bssid,ssid,security", content)
            self.assertIn("BLE", content)
        with urlopen(self.address + "/api/export.geojson", timeout=5) as response:
            geo = json.loads(response.read())
            self.assertEqual(geo["type"], "FeatureCollection")
            points = [f for f in geo["features"] if f["geometry"]["type"] == "Point"]
            self.assertEqual(len(points), 9)

    def test_upload_and_clear(self):
        log = b'2026-10-29T12:00:00Z BLE MAC=D2:11:22:33:44:55 name="Sensor" RSSI=-64\n'
        req = Request(
            self.address + "/api/import?name=test.log", data=log,
            headers={"Content-Type": "application/octet-stream"}, method="POST",
        )
        with urlopen(req, timeout=5) as response:
            self.assertEqual(json.loads(response.read())["ble"], 1)
        req = Request(self.address + "/api/clear", data=b"", method="POST")
        with urlopen(req, timeout=5):
            pass
        self.assertEqual(Handler.session.snapshot()["stats"]["networks"], 0)

    def test_reject_cross_origin_and_bad_extension(self):
        req = Request(
            self.address + "/api/demo", data=b"", method="POST",
            headers={"Origin": "https://otro-sitio.invalid"},
        )
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=5)
        self.assertEqual(err.exception.code, 403)

        req = Request(
            self.address + "/api/import?name=malware.exe", data=b"test",
            method="POST",
        )
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=5)
        self.assertEqual(err.exception.code, 415)


if __name__ == "__main__":
    unittest.main()
