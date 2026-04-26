import unittest
from unittest.mock import patch

import brightness_app

from brightness_app import (
    Display,
    MIN_BRIGHTNESS,
    get_displays,
    normalize_settings_payload,
    normalize_state_payload,
)


class NormalizePayloadTests(unittest.TestCase):
    def test_normalize_state_legacy_format(self):
        payload = {"\\\\.\\DISPLAY1": 75, "\\\\.\\DISPLAY2": "60", "bad": "x"}
        normalized = normalize_state_payload(payload)
        self.assertEqual(normalized["\\\\.\\DISPLAY1"], 75)
        self.assertEqual(normalized["\\\\.\\DISPLAY2"], 60)
        self.assertNotIn("bad", normalized)

    def test_normalize_state_v2_format_and_clamp(self):
        payload = {
            "version": 2,
            "values": {
                "\\\\.\\DISPLAY1": 5,
                "\\\\.\\DISPLAY2": 120,
            },
        }
        normalized = normalize_state_payload(payload)
        self.assertEqual(normalized["\\\\.\\DISPLAY1"], MIN_BRIGHTNESS)
        self.assertEqual(normalized["\\\\.\\DISPLAY2"], 100)

    def test_normalize_settings_defaults(self):
        normalized = normalize_settings_payload({})
        self.assertFalse(normalized["hotkeys_enabled"])
        self.assertFalse(normalized["dark_mode_enabled"])

    def test_normalize_settings_values(self):
        payload = {
            "settings": {
                "hotkeys_enabled": True,
                "dark_mode_enabled": True,
            }
        }
        normalized = normalize_settings_payload(payload)
        self.assertTrue(normalized["hotkeys_enabled"])
        self.assertTrue(normalized["dark_mode_enabled"])


class DisplayModelTests(unittest.TestCase):
    def test_display_position_subtitle(self):
        display = Display(index=0, device="\\\\.\\DISPLAY1", rect=(-1920, 0, 0, 1080), primary=False)
        self.assertIn("left of primary", display.subtitle)
        self.assertEqual(display.width, 1920)
        self.assertEqual(display.height, 1080)

    def test_get_displays_returns_list(self):
        displays = get_displays()
        self.assertIsInstance(displays, list)

    def test_get_displays_returns_empty_when_win32_unavailable(self):
        with patch.object(brightness_app, "win32api", None), patch.object(brightness_app, "win32con", None):
            self.assertEqual(get_displays(), [])


if __name__ == "__main__":
    unittest.main()
