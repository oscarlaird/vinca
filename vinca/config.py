import json
from pathlib import Path

class Config(dict):
	path = Path(__file__).parent / 'config.json'
	
	def __init__(self):
		dict.__init__(self, self.load())
	
	def load(self):
		with open(self.path) as f:
			return json.load(f)

	def save(self):
		with open(self.path,'w') as f:
			json.dump(self, f)

	def set_cards_path(self, path):
		''' vinca will look for cards in the chosen directory '''
		self['cards_path'] = str(path)
		self.save()

	@property
	def last_card_path(self):
		return Path(self['last_card_path'])

	@last_card_path.setter
	def last_card_path(self, card_path):
		self['last_card_path'] = str(card_path)
		self.save()

	@property
	def cards_path(self):
		return Path(self['cards_path'])

config = Config()
