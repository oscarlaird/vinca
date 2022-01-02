# The metareviewer which implements specific reviewers
import importlib
import time, datetime

TODAY = datetime.date.today()
	
GRADE_DICT = {'x': 'delete', 'd': 'delete',
	      'q': 'exit', '\x1b': 'exit',
	      'p': 'preview', '0': 'preview',
	      '1': 'again',
	      '2': 'hard',
	      '3': 'good', ' ': 'good', '\r': 'good', '\n': 'good',
	      '4': 'easy'}

def review(card):

	start = time.time()

	# dynamically import the required reviewer module
	# a specifc reviewer is responsible for returning a key to the generic reviewer
	m = importlib.import_module('.'+card.reviewer, package = 'vinca.reviewers')
	key = m.review(card)  # the reviewer gives back the key

	stop = time.time()
	elapsed = int(stop - start)

	grade = GRADE_DICT[key] if key in GRADE_DICT else 'exit'

	card.history.append_entry(TODAY, elapsed, grade)

def make_string(card):
	m = importlib.import_module('.'+card.reviewer, package = 'vinca.reviewers')
	assert hasattr(m, 'make_string'), f'{card.reviewer} must implement \
		the make_string method to represent this card on the command line'
	return m.make_string(card)
	
