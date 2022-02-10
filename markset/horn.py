import pygame
import numpy


class Horn:

	def __init__(self):
		self.sampleRate_ = 44100
		# 44.1kHz, 16-bit signed, mono
		pygame.mixer.pre_init(self.sampleRate_, -16, 1) 
		pygame.mixer.init()


	def play_song(self, timeout):
		pygame.mixer.music.load("/home/pi/workspace/markset/markset/sample.wav")
		pygame.mixer.music.set_volume(1.0)
		pygame.mixer.music.play()

	def stop(self):
		pygame.mixer.music.stop()

	def play_tone(self):

		pygame.init()
		# 4096 : the peak ; volume ; loudness
		# 440 : the frequency in hz
		# ?not so sure? if astype int16 not specified sound will get very noisy, because we have defined it as 16 bit mixer at mixer.pre_init()
		# ( probably due to int overflow resulting in non continuous sound data)
		arr = numpy.array([4096 * numpy.sin(2.0 * numpy.pi * 440 * x / self.sampleRate_) for x in range(0, self.sampleRate_)]).astype(numpy.int16)
		sound = pygame.sndarray.make_sound(arr)
		# ?not so sure? -1 means loop unlimited times
		sound.play(-1)