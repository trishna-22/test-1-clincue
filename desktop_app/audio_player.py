"""Ambient background-track playback, ported from the hidden <audio> element in procedures/*.html."""

import pygame


class AmbientAudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self._loaded_path = None
        self.volume = 0.15

    def load(self, path):
        if self._loaded_path != path:
            pygame.mixer.music.load(path)
            self._loaded_path = path
        pygame.mixer.music.set_volume(self.volume)

    def play(self):
        try:
            pygame.mixer.music.play(loops=-1)
        except pygame.error:
            pass

    def pause(self):
        pygame.mixer.music.pause()

    def stop(self):
        pygame.mixer.music.stop()
        self._loaded_path = None

    def set_volume(self, volume):
        self.volume = volume
        pygame.mixer.music.set_volume(volume)
