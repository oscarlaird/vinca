import subprocess
import json
import datetime
TODAY = datetime.date.today()
DAY = datetime.timedelta(days=1)
from pathlib import Path
from shutil import copytree

from vinca import _reviewers, _editors, _schedulers 
from vinca._tag_caching import tags_cache
from vinca._config import config
from vinca._lib.vinput import VimEditor
from vinca._lib.random_id import random_id
from vinca._history import History, HistoryEntry

class Card:
	# Card class can load without 
	default_metadata = {'editor': 'base', 'reviewer':'base', 'scheduler':'base',
			    'tags': [], 'history': History([HistoryEntry(TODAY, 0, 'create')]), 'deleted': False,
			    'due_date': TODAY, 'string': ''}

	def __init__(self, path=None, create=False):
		# We must create a new card or load a new card from a path.
		assert bool(path) ^ create
		if path:
			self.init_loaded_card(path)
		elif create:
			self.init_new_card()
		# hotkeys are available from the browser
		self._hotkeys = {'e': self.edit,
				'u': self.undo_history,
				'H': self.edit_history,
				'M': self.edit_metadata,
				't': self.edit_tags,
				'd': self.delete,
				'p': self.preview,
				'+': self.postpone}

	def init_loaded_card(self, path):
		self.path = path
		self.metadata_is_loaded = False

	def init_new_card(self):
		# create card location
		self.path = self.new_path()
		self.path.mkdir()
		# initialize metadata
		self.metadata = Card.default_metadata
		self.metadata_is_loaded = True
		self.save_metadata()
		# easy access to the last created card
		config.last_card_path = self.path


	@property
	def metadata_path(self):
		return self.path / 'metadata.json'

	def load_metadata(self):
		self.metadata = json.load(self.metadata_path.open())
		# dates must be serialized into strings for json
		# I unpack them here
		self.metadata['history'] = History.from_json_list(self.metadata['history'])
		assert self.metadata['history'], f'empty history metadata for {self.path}'
		self.metadata['due_date'] = datetime.date.fromisoformat(self.metadata['due_date'])
		self.metadata_is_loaded = True

	def save_metadata(self):
		json.dump(self.metadata, self.metadata_path.open('w'), default=str, indent=2)

	for m in default_metadata.keys():
		# create getter and setter methods for everything in the metadata dictionary
		exec(f'''
@property
def {m}(self):
	if not self.metadata_is_loaded:
		self.load_metadata()
	return self.metadata["{m}"]''')
		exec(f'''
@{m}.setter
def {m}(self, new_val):
	if not self.metadata_is_loaded:
		self.load_metadata()
	self.metadata["{m}"] = new_val
	self.save_metadata()''')	

	# overwrite the tags setter with one modification
	# we want to update the tags_cache
	@tags.setter
	def tags(self, tags):
		if not self.metadata_is_loaded:
			self.load_metadata()
		self.metadata['tags'] = tags
		self.save_metadata()
		tags_cache.add_tags(tags)

	def __str__(self):
		return self.string

	def review(self):
		_reviewers.review(self)
		# we have probably appended a history entry
		self.save_metadata() 
		self.schedule()

	def preview(self):
		_reviewers.review(self)
		# we have probably appended a history entry
		self.undo_history()

	def undo_history(self):
		# Undo the most recent entry in the card's review history.
		if len(self.history) == 1:
			print('Review history of this card is already at the beginning')
			return
		self.history.pop()
		self.save_metadata()
		self.due_date = TODAY

	def make_string(self):
		self.string = _reviewers.make_string(self)

	def edit(self):
		_editors.edit(self) 
		self.make_string()
		self.save_metadata() # we have probably modified history

	def edit_metadata(self):
		subprocess.run(['vim',self.path/'metadata.json'])
		self.load_metadata()
		self.make_string()
	edit_history = edit_metadata

	def print_metadata(self):
		if not self.metadata_is_loaded:
			self.load_metadata()
		for k,v in self.metadata.items():
			if k == 'history':
				continue
			print(f'{k:20}', v, sep='', end='\n')

	def schedule(self):
		dd = _schedulers.schedule(name=self.scheduler, history=self.history)
		if dd:
			self.due_date = dd

	def new_path(self):
		return config.cards_path / ('card-' + random_id())

	def delete(self):
		self.deleted = True
		print('Card has been deleted. Use `vinca last-card restore` to undo.')

	def restore(self):
		self.deleted = False
		print('Card restored.')

	def due_as_of(self, date):
		return self.due_date <= date

	@property
	def is_due(self):
		return self.due_as_of(TODAY)

	def edit_tags(self):
		self.tags = VimEditor(prompt = 'tags: ', text = ' '.join(self.tags), completions = tags_cache).run().split()

	def postpone(self, n=1):
		tomorrow = TODAY + DAY*n
		self.due_date = tomorrow
		print(f'Postponed until {self.due_date}. (Use `vinca last-card postpone -1` to undo).')

	@property
	def create_date(self):
		return self.history.create_date

	@property
	def seen_date(self):
		return self.history.last_date

	@property
	def new(self):
		return self.history.new


	@property
	def time(self):
		return self.history.time
