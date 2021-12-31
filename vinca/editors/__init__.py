import datetime
TODAY = datetime.date.today()
import importlib

def edit(card):
	start = datetime.datetime.now()

	m = importlib.import_module('.' + card.editor, package = 'vinca.editors')
	m.edit(card)

	stop = datetime.datetime.now()
	elapsed_time = min(240, (stop - start).seconds)

	card.history.append_entry(TODAY, elapsed_time, 'edit')
	
	card.make_string()
