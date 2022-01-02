import importlib
from importlib import import_module

def schedule(name, history):

	# import the specific scheduler module
	m = importlib.import_module('.' + name, package = 'vinca.schedulers')
	# invoke the specific scheduler
	return m.schedule(history)
