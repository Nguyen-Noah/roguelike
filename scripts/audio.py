import pygame

AUDIO_PATH = './data/sounds/'

class Audio:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        self.sounds = {}

    def clear(self, path):
        if path in self.sounds:
            del self.sounds[path]

    def clear_all(self):
        self.sounds = {}

    def change_volume(self, sound, vol):
        self.sounds[sound].set_volume(vol)

    def add(self, sound, volume):
        if not sound in self.sounds:
            py_sound = pygame.mixer.Sound(AUDIO_PATH + sound)
            py_sound.set_volume(volume)
            sound_name = sound.split('.')[0]
            self.sounds[sound_name] = py_sound

    def play(self, sound, loop=0):
        self.sounds[sound].play(loop)