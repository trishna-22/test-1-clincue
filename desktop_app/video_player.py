"""Embedded video playback for the Combined Media tab.

Tkinter has no native video widget, so frames are decoded with OpenCV, converted to
PhotoImage, and pushed into a Label. Playback is driven by recursive `root.after(...)`
scheduling on the main thread (not a background thread) since Tkinter widgets may only be
touched from the thread running mainloop().
"""

import cv2
from PIL import Image, ImageTk


class VideoPlayer:
    def __init__(self, root, label, default_size=(480, 270)):
        self._root = root
        self._label = label
        self._default_size = default_size
        self._cap = None
        self._playing = False
        self._after_id = None
        self._delay_ms = 33
        self._current_image = None  # kept to prevent garbage collection

    def load(self, path):
        self.stop()
        self._cap = cv2.VideoCapture(path)
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 25
        self._delay_ms = max(int(1000 / fps), 15)
        self._render_current_frame()

    def _render_current_frame(self):
        if not self._cap:
            return
        ret, frame = self._cap.read()
        if ret:
            self._render(frame)
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def _render(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        w = self._label.winfo_width() or self._default_size[0]
        h = self._label.winfo_height() or self._default_size[1]
        img = Image.fromarray(frame)
        img.thumbnail((max(w, 10), max(h, 10)))
        self._current_image = ImageTk.PhotoImage(img)
        self._label.configure(image=self._current_image)

    def play(self):
        if not self._cap or self._playing:
            return
        self._playing = True
        self._loop()

    def _loop(self):
        if not self._playing or not self._cap:
            return
        ret, frame = self._cap.read()
        if not ret:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        if ret:
            self._render(frame)
        self._after_id = self._root.after(self._delay_ms, self._loop)

    def pause(self):
        self._playing = False
        if self._after_id is not None:
            self._root.after_cancel(self._after_id)
            self._after_id = None

    def stop(self):
        self.pause()
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def toggle(self):
        if self._playing:
            self.pause()
        else:
            self.play()

    @property
    def is_playing(self):
        return self._playing
