import os
from pygame import mixer
import logging
import random
from apscheduler.schedulers.background import BackgroundScheduler 



class Horn:

	def __init__(self, ):
		mixer.init()
		self.walking_interval = None
		self.is_walking = False
		self.walking_song = None
		self.walking_song_queue = None
		self.sched = BackgroundScheduler()
		self.sched.start()
		self.tunes_path = "/home/pi/workspace/markset/markset/music/"
		self.tunes = []
		self.job = None

	def play(self, song):
		self.stop()
		mixer.music.load(self.tunes_path + song)
		mixer.music.set_volume(1.0)
		mixer.music.play()

	def test(self):
		self.play("sample.wav")

	def stop(self):
		if self.job != None:
			self.job.remove()
			self.job = None
		mixer.music.stop()
		self.is_walking = False

	def play_walking_music(self):
		logging.warn("play_walking_music")
		if self.is_walking:
			if len(self.tunes) == 0:
				logging.warn("start tunes")
				# start the tunes
				self.tunes = self.getListOfFiles(self.tunes_path + "walking/")
				random.shuffle(self.tunes)
				self.is_playing = True
			if not mixer.music.get_busy():
				song = self.tunes.pop(0)
				logging.warn("playing " + song)
				mixer.music.load(song)
				mixer.music.set_volume(.8)
				mixer.music.play()
			
	def next_song(self):
		mixer.music.stop()
		
	def start_walking_music(self):
		self.is_walking = True
		logging.warn("start_walking_music")
		self.job = self.sched.add_job(self.play_walking_music, 'interval', seconds=1)
		
		



	def getListOfFiles(self, dirName):
		# create a list of file and sub directories 
		# names in the given directory 
		listOfFile = os.listdir(dirName)
		allFiles = list()
		# Iterate over all the entries
		for entry in listOfFile:
			# Create full path
			fullPath = os.path.join(dirName, entry)
			# If entry is a directory then get the list of files in this directory 
			if os.path.isdir(fullPath):
				allFiles = allFiles + self.getListOfFiles(fullPath)
			else:
				allFiles.append(fullPath)
					
		return allFiles