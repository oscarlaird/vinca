from vinca.lib import ansi
import re
import shutil

COLUMNS, LINES = shutil.get_terminal_size()

# A Context Manager for the terminal's alternate screen
class AlternateScreen:
	def __enter__(self):
		ansi.save_cursor()
		ansi.hide_cursor()
		ansi.save_screen()
		ansi.clear()
		ansi.move_to_top()

	def __exit__(self, *exception_args):
		ansi.restore_screen()
		ansi.restore_cursor()


class NoCursor:
	def __enter__(self):
		ansi.hide_cursor()

	def __exit__(self, *exception_args):
		ansi.show_cursor()
		

class LineWrapOff:
	def __enter__(self):
		ansi.line_wrap_off()

	def __exit__(self, *exception_args):
		ansi.line_wrap_on()

def roundup(flt):
	'''
	>>> roundup(5)
	5
	>>> roundup(4.01)
	5
	>>> roundup(5.000)
	5
	'''
	if int(flt) == flt:
		return int(flt)
	return round(flt + 0.5)

def count_screen_lines(text):
	'''
	>>> COLUMNS
	20
	>>> count_screen_lines('the quick fox')
	1
	>>> count_screen_lines('-'*20)
	1
	>>> count_screen_lines('this very long text' * 100)
	95
	>>> count_screen_lines('long'*100 + '\\ris overwritten')
	1
	>>> count_screen_lines('\033[?25l hidden cursor \033[?25h')
	1
	'''
	text = strip_ansi(text)
	lines = text.split('\n')
	# carriage return overwrites the line so we want
	# the text after the last carriage return on the line
	lines = [l.split('\r')[-1] for l in lines] 
	lines = [roundup(len(l) / COLUMNS) for l in lines]
	return sum(lines)

def strip_ansi(text):
	'''
	>>> strip_ansi('the quick fox')
	'the quick fox'
	>>> strip_ansi('\033[1mBOLD')
	'BOLD'
	>>> strip_ansi('\033[?25l hidden cursor \033[?25h')
	' hidden cursor '
	>>> strip_ansi('down\033E line')
	'down line'
	'''
	ansi_escape = re.compile(r'''
	    \x1B  # ESC
	    (?:   # 7-bit C1 Fe (except CSI)
		[@-Z\\-_]
	    |     # or [ for CSI, followed by a control sequence
		\[
		[0-?]*  # Parameter bytes
		[ -/]*  # Intermediate bytes
		[@-~]   # Final byte
	    )
	''', re.VERBOSE)
	result = ansi_escape.sub('', text)
	return result

if __name__ == '__main__':
	import doctest
	COLUMNS = 20
	doctest.testmod(extraglobs = {'COLUMNS': 20})
