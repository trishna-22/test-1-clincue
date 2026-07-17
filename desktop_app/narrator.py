"""Text-to-speech narration engine, ported from the SpeechNarrator class in js/shared.js.

pyttsx3's engine object is not safe to drive from multiple threads at once, so all speech
happens on a single dedicated worker thread. `engine.stop()` is called from whichever thread
invokes pause()/stop() (usually the Tk main thread) to interrupt a blocking runAndWait() call
on the worker thread -- this cross-thread stop() call is the standard workaround for making
pyttsx3 interruptible.
"""

import queue
import threading

import pyttsx3


class TTSNarrator:
    def __init__(self, root):
        self._root = root
        self.steps = []
        self.current_step_idx = -1
        self.is_playing = False
        self.on_step_change = None
        self.on_state_change = None
        self.rate = 0.95

        self._engine = None
        self._queue = queue.Queue()
        self._stopped_flag = False
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        self._ready.wait()

    def _worker(self):
        self._engine = pyttsx3.init()
        base_rate = self._engine.getProperty("rate") or 200
        self._engine.setProperty("rate", int(base_rate * self.rate))
        voices = self._engine.getProperty("voices") or []
        english = next((v for v in voices if "english" in (v.name or "").lower()), None)
        if not english:
            english = next((v for v in voices if "en" in (v.id or "").lower()), None)
        if english:
            self._engine.setProperty("voice", english.id)
        self._ready.set()

        while True:
            idx = self._queue.get()
            if idx is None:
                break
            self._stopped_flag = False
            text = self.steps[idx]
            self.current_step_idx = idx
            self._notify_step(idx)

            self._engine.say(text)
            self._engine.runAndWait()

            if self._stopped_flag:
                continue

            if self.is_playing and idx < len(self.steps) - 1:
                self._queue.put(idx + 1)
            else:
                self._finish()

    def _notify_step(self, idx):
        if self.on_step_change:
            self._root.after(0, self.on_step_change, idx)

    def _notify_state(self, playing):
        if self.on_state_change:
            self._root.after(0, self.on_state_change, playing)

    def _finish(self):
        self.is_playing = False
        self.current_step_idx = -1
        self._notify_state(False)
        self._notify_step(-1)

    # ---- public API, mirrors SpeechNarrator ----
    def set_steps(self, steps):
        self.steps = steps
        self.current_step_idx = -1

    def speak_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return
        self._queue.put(idx)

    def play(self):
        if not self.steps:
            return
        self.is_playing = True
        self._notify_state(True)
        if self.current_step_idx == -1 or self.current_step_idx == len(self.steps) - 1:
            self.speak_step(0)
        else:
            self.speak_step(self.current_step_idx)

    def pause(self):
        self.is_playing = False
        self._stopped_flag = True
        if self._engine:
            self._engine.stop()
        self._notify_state(False)

    def stop(self):
        self.is_playing = False
        self.current_step_idx = -1
        self._stopped_flag = True
        if self._engine:
            self._engine.stop()
        self._notify_state(False)
        self._notify_step(-1)

    def shutdown(self):
        self._queue.put(None)
