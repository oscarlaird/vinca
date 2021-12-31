''' This scrollback module is deprecated
The idea was going to be to create a wrapper for a function which would intercept its print statements compute the number of terminal lines printed and scrollback that many lines and clear to bottom. This could be used, for example to show card editing or statistics alongside the browser. However we do have to use a time proxy for interactivity to know whether to continue
'''

import sys
import functools
from vinca.lib import ansi
from vinca.lib.terminal import count_screen_lines
from vinca.lib.readkey import readkey

class Intercepter:
	def __init__(self):
		self.text = ''
	def write(self, text):
		sys.__stdout__.write(text) # echo to terminal
		self.text += text # log the printed text
	def __enter__(self):
		sys.stdout = self # begin intercepting stdout
	def __exit__(self):
		sys.stdout = sys.__stdout__ # reconnect normal stdout

def scrollback(func):
	@functools.wraps(func)
	def modified_func(*args, scrollback = False, **kwargs):
		if not scrollback:
			return func(*args, **kwargs)
		with Intercepter() as i:
			ret = func(*args, **kwargs)
			n = count_screen_lines(i.text)
		ansi.up_line(n)
		ansi.clear_to_end()
		return ret
	return modified_func
