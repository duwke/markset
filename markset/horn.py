import asyncio
import pygame
import numpy
import time


class Horn:

	def __init__(self):
		self.sampleRate_ = 44100
		# 44.1kHz, 16-bit signed, mono
		pygame.mixer.pre_init(self.sampleRate_, -16, 1) 
		pygame.mixer.init()


	async def play_song(self, timeout):
		pygame.mixer.music.load("/home/pi/workspace/markset/markset/sample.wav")
		pygame.mixer.music.set_volume(1.0)
		pygame.mixer.music.play()


		start = time.time()
		elapsed_time = time.time() - start

		while pygame.mixer.music.get_busy() == True and elapsed_time < timeout:
			await asyncio.sleep(0.5)
			elapsed_time = time.time() - start
		
		pygame.mixer.music.stop()

	def stop(self):
		pygame.mixer.music.stop()

	async def play_tone(self, timeout):

		# 4096 : the peak ; volume ; loudness
		# 440 : the frequency in hz
		# ?not so sure? if astype int16 not specified sound will get very noisy, because we have defined it as 16 bit mixer at mixer.pre_init()
		# ( probably due to int overflow resulting in non continuous sound data)
		arr = numpy.array([4096 * numpy.sin(2.0 * numpy.pi * 440 * x / self.sampleRate_) for x in range(0, self.sampleRate_)]).astype(numpy.int16)
		sound = pygame.sndarray.make_sound(arr)
		# ?not so sure? -1 means loop unlimited times
		sound.play(-1)
		
		start = time.time()
		elapsed_time = time.time() - start

		while pygame.mixer.music.get_busy() == True and elapsed_time < timeout:
			await asyncio.sleep(0.5)
			elapsed_time = time.time() - start
		
		pygame.mixer.music.stop()
