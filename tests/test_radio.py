"""Pruebas de seguridad Wi-Fi, informes ESP32 Marauder y anuncios BLE."""
import struct
import unittest

from wardrive_track.core import Session, aggregate, as_csv, as_geojson
from wardrive_track.parsers import parse_file, read_text
from wardrive_track.radio import (
    ble_hci_frame, protocol_from_text, security_from_ies, security_from_text,
)


def ie(tag, payload):
    return bytes([tag, len(payload)]) + payload


def rsn(*akm_types):
    group = b"\x00\x0f\xac\x04"
    body = b"\x01\x00" + group + b"\x01\x00" + group
    body += len(akm_types).to_bytes(2, "little")
    for t in akm_types:
        body += b"\x00\x0f\xac" + bytes([t])
    body += b"\x00\x00"
    return ie(48, body)


def wifi_frame(security_ies=b"", cap=0, name=b"TEST_NET"):
    mac = bytes.fromhex("021122334455")
    hdr = b"\x80\x00\x00\x00" + b"\xff"*6 + mac + mac + b"\x00\x00"
    fixed = b"\x00"*8 + b"\x64\x00" + cap.to_bytes(2, "little")
    return hdr + fixed + ie(0, name) + ie(3, b"\x06") + security_ies


def pcap(linktype, frames):
    header = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, linktype)
    payload = bytearray(header)
    for i, frame in enumerate(frames):
        payload.extend(struct.pack("<IIII", 1790000000 + i, 0, len(frame), len(frame)))
        payload.extend(frame)
    return bytes(payload)


def ble_hci(name=b"Prueba_BLE", address=b"\x05\x04\x03\x02\x01\xd2"):
    ad = bytes([len(name) + 1, 9]) + name
    report = bytes([0, 1]) + address + bytes([len(ad)]) + ad + bytes([0xC4])
    meta = bytes([2, 1]) + report
    return bytes([4, 0x3E, len(meta)]) + meta


class SecurityTests(unittest.TestCase):
    def test_normalization(self):
        expected = {
            "[ESS]": "OPEN", "[WEP][ESS]": "WEP",
            "[WPA-PSK-CCMP][ESS]": "WPA",
            "[WPA2-PSK-CCMP][ESS]": "WPA2",
            "[WPA2-PSK][WPA3-SAE]": "WPA2/WPA3",
            "[WPA3-SAE]": "WPA3",
            "OWE": "OWE", "": "No determinada",
        }
        for value, result in expected.items():
            with self.subTest(value=value):
                self.assertEqual(security_from_text(value), result)

    def test_rsn_akm_and_legacy(self):
        combinations = [
            (0, b"", "OPEN"),
            (0x10, b"", "WEP"),
            (0x10, ie(221, b"\x00\x50\xf2\x01\x01\x00"), "WPA"),
            (0x10, rsn(2), "WPA2"),
            (0x10, rsn(8), "WPA3"),
            (0x10, rsn(2, 8), "WPA2/WPA3"),
            (0x10, rsn(18), "OWE"),
        ]
        for cap, ies, expected in combinations:
            with self.subTest(expected=expected):
                self.assertEqual(security_from_ies(cap, ies), expected)

    def test_pcap_wifi_security(self):
        names = [
            ("OPEN", wifi_frame()),
            ("WEP", wifi_frame(cap=0x10)),
            ("WPA2", wifi_frame(rsn(2), cap=0x10)),
            ("WPA3", wifi_frame(rsn(8), cap=0x10)),
            ("WPA2/WPA3", wifi_frame(rsn(2, 8), cap=0x10)),
        ]
        for expected, frame in names:
            with self.subTest(expected=expected):
                observations, gps, warning = parse_file("scan.pcap", pcap(105, [frame]))
                self.assertEqual(len(observations), 1, warning)
                self.assertEqual(observations[0]["security"], expected)
                self.assertEqual(observations[0]["protocol"], "Wi-Fi")
                self.assertEqual(observations[0]["ssid"], "TEST_NET")

    def test_protocol_types(self):
        self.assertEqual(protocol_from_text("BLE"), "BLE")
        self.assertEqual(protocol_from_text("BT"), "Bluetooth")
        self.assertEqual(protocol_from_text("WIFI"), "Wi-Fi")
        self.assertEqual(protocol_from_text("", "BLE"), "BLE")


class BluetoothTests(unittest.TestCase):
    def test_ble_hci_name_rssi_address(self):
        decoded = ble_hci_frame(ble_hci(), 201, 1234.0)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0]["bssid"], "D2:01:02:03:04:05")
        self.assertEqual(decoded[0]["ssid"], "Prueba_BLE")
        self.assertEqual(decoded[0]["rssi"], -60)
        self.assertEqual(decoded[0]["address_type"], "Aleatoria")
        self.assertEqual(decoded[0]["security"], "No aplica")

    def test_ble_hci_pcap_and_pseudoheader(self):
        for linktype, frame in [
            (201, ble_hci()),
            (187, b"\x00\x00\x00\x00" + ble_hci()),
        ]:
            with self.subTest(linktype=linktype):
                obs, fixes, errors = parse_file("bt.pcap", pcap(linktype, [frame]))
                self.assertEqual(len(obs), 1, errors)
                self.assertEqual(obs[0]["protocol"], "BLE")

    def test_wigle_bluetooth_csv(self):
        content = (
            "WigleWifi-1.6,appRelease=Demo\n"
            "MAC,SSID,AuthMode,FirstSeen,Channel,Frequency,RSSI,CurrentLatitude,CurrentLongitude,Type\n"
            "D2:01:02:03:04:05,Pulsometro,,2026-10-29T12:00:00Z,,,-61,40.4,-3.7,BLE\n"
            "B2:01:02:03:04:05,Altavoz,,2026-10-29T12:00:01Z,,,-70,,,BT\n"
        )
        obs, gps, warning = parse_file("bt_wardrive.csv", content.encode())
        self.assertEqual([x["protocol"] for x in obs], ["BLE", "Bluetooth"])
        self.assertEqual(len(gps), 1)
        self.assertEqual(obs[0]["ssid"], "Pulsometro")
        self.assertEqual(obs[1]["security"], "No aplica")

    def test_bluetooth_log(self):
        log = b'2026-10-29T12:00:00Z BLE MAC=D2:11:22:33:44:55 name="Sensor" RSSI=-62 lat=40.4 lon=-3.7\n'
        obs, fixes, warnings = parse_file("bt_wardrive_001.log", log)
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0]["protocol"], "BLE")
        self.assertEqual(obs[0]["ssid"], "Sensor")
        self.assertEqual(len(fixes), 1)

    def test_same_mac_different_radios_are_distinct(self):
        mac = "D2:11:22:33:44:55"
        a = dict(bssid=mac, ssid="WiFi", protocol="Wi-Fi",
                 security="WPA2", rssi=-50, channel=6, ts=10, lat=None, lon=None)
        b = dict(bssid=mac, ssid="Bluetooth", protocol="BLE",
                 security="No aplica", rssi=-70, channel=None, ts=10, lat=None, lon=None)
        combined = aggregate([a, b], [])
        self.assertEqual(combined["stats"]["networks"], 2)
        self.assertEqual(combined["stats"]["wifi"], 1)
        self.assertEqual(combined["stats"]["ble"], 1)
        self.assertEqual(combined["security"]["WPA2"], 1)

    def test_no_gps_never_inferred_from_mac(self):
        obs, _, _ = parse_file("ble.pcap", pcap(201, [ble_hci()]))
        s = aggregate(obs, [])
        self.assertEqual(s["stats"]["located"], 0)
        self.assertEqual(as_geojson(s)["features"], [])

    def test_csv_formula_protection(self):
        sample = aggregate([
            dict(bssid="02:11:22:33:44:55", ssid="=SUM(1+1)", protocol="Wi-Fi",
                 security="OPEN", rssi=-40, channel=1, ts=None, lat=None, lon=None),
        ], [])
        output = as_csv(sample)
        self.assertIn("'=SUM(1+1)", output)

    def test_malformed_ble_cannot_crash_parser(self):
        for x in (b"", b"\x04", b"\x04\x3e\x05\x02\x01"):
            self.assertEqual(ble_hci_frame(x, 201, 0), [])


if __name__ == "__main__":
    unittest.main()
