import re
import datetime
from random import random
from shutil import copytree, rmtree
from pathlib import Path
from vinca.card import Card
from vinca.browser import Browser
from vinca.lib import ansi
from vinca.lib.vinput import VimEditor
from vinca.lib.readkey import readkey
from vinca.lib import casting
from vinca.config import config
from vinca.tag_caching import tags_cache
TODAY = datetime.date.today()

class Cardlist:
	''' this is a collection of cards. most of the user interface takes place through the browser '''

	@classmethod
	def from_directory(cls, directory):
		directory = Path(directory) # I would probably want Python FIRE to automatically cast paths
		return cls([Card(p) for p in directory.iterdir()])


	def __init__(self, _cards):
		# we do not subclass list so that
		# the fire help is not littered
		# with inherited methods (e.g. pop, extend, index)
		# subclassing list would be more natural
		# instead we subclass it manually below
		self._cards = _cards

	def __iter__(self):
		return iter(self._cards)

	def __len__(self):
		return len(self._cards)

	def __getitem__(self, slice):
		return self._cards[slice]

	def _insert_card(self, idx, card):
		self._cards.insert(idx, card)

	def __str__(self):
		s = ''
		l = len(self)
		if l == 0:
			return 'No cards.'
		if l > 6:
			s += f'6 of {l}\n'
		s += ansi.codes['line_wrap_off']
		for card in self[:6]:
			if card.due_as_of(TODAY):
				s += ansi.codes['blue']
			if card.deleted:
				s += ansi.codes['red']
			s += f'{card}\n'
			s += ansi.codes['reset']
		s += ansi.codes['line_wrap_on']
		return s

	def browse(self):
		''' Interactively manage you collection. See the tutorial (man vinca) for help. '''
		Browser(self).browse()

	def review(self):
		''' Review your cards. '''
		due_cards = self.filter(due_only = True)
		Browser(due_cards).review()
				
	def add_tag(self, tag):
		' Add a tag to cards '
		for card in self:
			card.tags += [tag]

	def remove_tag(self, tag):
		' Remove a tag from cards '
		for card in self:
			if tag in card.tags:
				card.tags.remove(tag)
			# TODO do this with set removal
			card.save_metadata()  # metadata ops should be internal TODO

	# @property
	def count(self):
		''' simple summary statistics '''
	#	total_count = len(self)
	#	due_count = len(self.filter(due_only=True))
	#	print(f'total	{total_count}')
	#	print(f'due	{due_count}')
		return {'total': len(self), 'due': len(self.filter(due_only=True))}

	def save(self, save_path):
		''' Save cards to a specified folder '''
		save_path = casting.to_path(save_path)
		for card in self:
			copytree(card.path, save_path / card.path.name)

	def purge(self):
		''' Permanently delete cards marked for deletion. '''
		deleted_cards = self.filter(deleted_only = True)
		if not deleted_cards:
			print('No cards are marked for deletion.')
			return
		print(f'delete {len(deleted_cards)} cards? (y/n)')
		if readkey() == 'y':
			for card in deleted_cards:
				rmtree(card.path)

	def delete(self):
		'delete cards'
		for card in self:
			card.delete()
		print(f'{len(self)} cards deleted')

	def restore(self):
		'restore (undelete) cards'
		for card in self:
			card.restore()
		print(f'{len(self)} cards restored')


	def filter(self, *,
		   tag = None,
		   created_after=None, created_before=None,
		   seen_after=None, seen_before=None,
		   due_after=None, due_before=None,
		   editor=None, reviewer=None, scheduler=None,
		   deleted_only=False, due_only=False, new_only=False,
		   invert=False):
		''' Filter the collection. Consult `vinca filter --help` for a full list of predicates.  '''
		if not any((tag,
		   created_after, created_before,
		   seen_after, seen_before,
		   due_after, due_before,
		   editor, reviewer, scheduler,
		   deleted_only, due_only, new_only)):
			print('You must specify a filtering predicate. For example:\n'
			      'vinca filter --new                       New Cards\n'
			      'vinca filter --editor verses             Poetry Cards\n'
			      'vinca filter --created-after -7          Cards created in the last week.\n'
			      'Consult `vinca filter --help` for a complete list of predicates')
			exit()
		
		# cast dates to dates
		created_after = casting.to_date(created_after)
		created_before = casting.to_date(created_before)
		seen_after = casting.to_date(seen_after)
		seen_before = casting.to_date(seen_before)
		due_after = casting.to_date(due_after)
		due_before = casting.to_date(due_before)

		if due_only: due_before = TODAY

		f = lambda card: (((not tag or tag in card.tags) and
				(not created_after or created_after <= card.create_date) and
				(not created_before or created_before >= card.create_date) and 
				(not seen_after or seen_after <= card.seen_date) and
				(not seen_before or seen_before >= card.seen_date) and 
				(not due_after or due_after <= card.due_date) and
				(not due_before or due_before >= card.due_date) and 
				(not editor or editor == card.editor) and
				(not reviewer or reviewer == card.reviewer) and
				(not scheduler or scheduler == card.scheduler) and
				(not deleted_only or card.deleted ) and
				(not new_only or card.new)) ^
				invert)
		
		return self.__class__([c for c in self if f(c)])

	def find(self, pattern):
		''' return the first card containing a search pattern '''
		matches = self.findall(pattern)
		matches.sort(criterion = 'seen')
		return matches[0] if matches else 'no match found'

	def findall(self, pattern):
		''' return all cards containing a search-pattern '''
		try:
			p = re.compile(f'({pattern})')  # wrap in parens to create regex group \1
		except re.error:
			print(f'The pattern {p} is invalid regex')
			return
		contains_pattern = lambda card: p.search(card.string)
		return self.__class__([c for c in self if contains_pattern(c)])

	def sort(self, criterion=None, *, reverse=False):
		''' sort the collection. criterion
		should be (due | seen | created | time | random) '''
		crit_dict = {
			'due': lambda card: card.due_date,
			'seen': lambda card: card.seen_date,
			'created': lambda card: card.create_date,
			'time': lambda card: card.time,
			'random': lambda card: random()} # random sort
		# E.g. we want to see the cards that have taken the most time first
		if criterion not in crit_dict:
			print('supply a sort criterion: (due | seen | created | time | random)')
			exit()
		# For some criteria it is natural to see the highest value first
		# switch reverse boolean flag iff it is a reverse crit
		reverse ^= criterion in ('created', 'seen', 'time') 
		sort_function = crit_dict[criterion]
		self._cards.sort(key = sort_function, reverse = reverse)
		return self

	def time(self):
		''' Total time spend studying these cards. '''
		return sum([card.history.time for card in self], start=datetime.timedelta(0))

