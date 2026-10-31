"""Comprobación de identidad y versión única en todos los puntos de entrada."""
import subprocess
import sys
import unittest
from pathlib import Path

from wardrive_track import APP_NAME, CREATOR, __version__, metadata
from wardrive_track.server import WEB, EXAMPLES


class VersionTests(unittest.TestCase):
    def test_metadata(self):
        about = metadata()
        self.assertEqual(about["version"], __version__)
        self.assertEqual(about["creator"], CREATOR)
        self.assertEqual(about["name"], APP_NAME)

    def test_cli_version(self):
        root = Path(__file__).resolve().parent.parent
        result = subprocess.run([sys.executable, str(root / "run.py"), "--version"],
                                capture_output=True, text=True, check=True, timeout=10)
        self.assertIn(__version__, result.stdout)
        self.assertIn(CREATOR, result.stdout)

    def test_cli_diagnostico(self):
        root = Path(__file__).resolve().parent.parent
        result = subprocess.run([sys.executable, str(root / "run.py"), "--diagnostico"],
                                capture_output=True, text=True, check=True, timeout=10)
        self.assertIn("Diagnóstico correcto", result.stdout)
        self.assertIn(__version__, result.stdout)
        self.assertIn(CREATOR, result.stdout)

    def test_resources_and_placeholders(self):
        self.assertTrue((WEB / "index.html").is_file())
        self.assertTrue((EXAMPLES / "ejemplo_bluetooth.csv").is_file())
        html = (WEB / "index.html").read_text(encoding="utf-8")
        self.assertIn("__WARDRIVE_VERSION__", html)
        self.assertIn("__WARDRIVE_CREATOR__", html)
        self.assertNotIn("v0.2", html)


if __name__ == "__main__":
    unittest.main()
