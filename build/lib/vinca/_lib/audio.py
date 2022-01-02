# try vlc or playsound modules (or mixer from pygame)

class Recording:
	''' There are two methods: play and stop.
	It can also be invoked as a context manager.'''

	def __init__(self, audio_path):
		self.audio_path = audio_path

	def play(self):
		pass

	def stop(self):
		pass


	def __enter__(self):
		if self.audio_path.exists():
			self.play()

	def __exit__(self, *exception_args):
		if self.audio_path.exists():
			self.stop()
