"""ClinCue desktop app - entry point.

Ports the Test 1 Clinicue web dashboard (index.html + procedures/*.html) into a standalone
Tkinter desktop application. Run with:

    pip install -r requirements.txt
    python main.py
"""

import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import theme as theme_mod
from audio_player import AmbientAudioPlayer
from data import APP_NAME
from narrator import TTSNarrator
from ui.dashboard import build_dashboard
from ui.procedure import build_procedure


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("1200x820")
        self.root.minsize(960, 640)

        self.theme_name = theme_mod.load_theme_name()
        self.theme = theme_mod.get_theme(self.theme_name)
        self.root.configure(bg=self.theme["bg_main"])

        self.narrator = TTSNarrator(self.root)
        self.audio_player = AmbientAudioPlayer()

        self.container = tk.Frame(self.root, bg=self.theme["bg_main"])
        self.container.pack(fill="both", expand=True)

        self._current_view = ("dashboard", None)
        self._current_cleanup = None

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_dashboard()

    def _show(self, view, slug=None):
        if self._current_cleanup:
            self._current_cleanup()
            self._current_cleanup = None
        for widget in self.container.winfo_children():
            widget.destroy()

        self._current_view = (view, slug)
        self.root.configure(bg=self.theme["bg_main"])

        if view == "dashboard":
            frame, cleanup = build_dashboard(self.container, self)
        else:
            frame, cleanup = build_procedure(self.container, self, slug)
        frame.pack(fill="both", expand=True)
        self._current_cleanup = cleanup

    def show_dashboard(self):
        self._show("dashboard")

    def show_procedure(self, slug):
        self._show("procedure", slug)

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        theme_mod.save_theme_name(self.theme_name)
        self.theme = theme_mod.get_theme(self.theme_name)
        view, slug = self._current_view
        self._show(view, slug)

    def _on_close(self):
        if self._current_cleanup:
            self._current_cleanup()
        self.narrator.shutdown()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
