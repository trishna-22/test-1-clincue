"""Dark/light color palettes, ported from css/styles.css custom properties."""

import colorsys
import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clinicue_settings.json")


def _hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


ACCENT = _hsl(332, 45, 58)
ACCENT_HOVER = _hsl(332, 45, 48)

THEMES = {
    "dark": {
        "bg_main": "#0a0b0e",
        "bg_surface": "#12141c",
        "bg_surface_hover": "#1a1d29",
        "bg_input": "#151821",
        "border": "#2a2d35",
        "text_main": "#f3f4f6",
        "text_muted": "#9ca3af",
        "text_inverse": "#111827",
        "accent": ACCENT,
        "accent_hover": ACCENT_HOVER,
        "success": "#10b981",
        "warning": "#f59e0b",
        "info": "#3b82f6",
    },
    "light": {
        "bg_main": "#f5f6fa",
        "bg_surface": "#ffffff",
        "bg_surface_hover": "#f0f1f5",
        "bg_input": "#ffffff",
        "border": "#e2e3e8",
        "text_main": "#1f2937",
        "text_muted": "#6b7280",
        "text_inverse": "#ffffff",
        "accent": ACCENT,
        "accent_hover": ACCENT_HOVER,
        "success": "#10b981",
        "warning": "#f59e0b",
        "info": "#3b82f6",
    },
}


def load_theme_name():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("theme", "dark")
        except (json.JSONDecodeError, OSError):
            return "dark"
    return "dark"


def save_theme_name(name):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump({"theme": name}, f)


def get_theme(name):
    return THEMES.get(name, THEMES["dark"])
