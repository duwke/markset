import pygame


class Horn:

	def __init__(self):
		pygame.mixer.init()


	def play(self, song):
		pygame.mixer.music.load("/home/pi/workspace/markset/markset/music/" + song)
		pygame.mixer.music.set_volume(1.0)
		pygame.mixer.music.play()

	def stop(self):
		pygame.mixer.music.stop()

