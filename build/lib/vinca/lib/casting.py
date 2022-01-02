from pathlib import Path
import datetime

TODAY = datetime.date.today()
DAY = datetime.timedelta(days=1)

def to_path(arg):
	''' convert a string to a path and verify it exists
	tests
	>>> to_path('/home')
	PosixPath('/home')
	>>> to_path(Path('/home'))
	PosixPath('/home')
	>>> to_path('/nowhere')
	Traceback (most recent call last):
	...
	FileNotFoundError
	'''
	if type(arg) is Path:
		return arg
	p = Path(arg)
	if not p.exists():
		raise FileNotFoundError(p)
	return p

def to_date(arg):
	''' convert 2021-10-31 to a October 31, 2021
	and convert -7 to one week before today
	>>> to_date('2021-10-31')
	datetime.date(2021, 10, 31)
	>>> TODAY - to_date(-7)
	datetime.timedelta(days=7)
	>>> to_date('10-31-2021')
	Traceback (most recent call last):
	...
	ValueError: Dates must be YYYY-MM-DD
	'''
	if type(arg) is datetime.date:
		return arg
	if type(arg) is str:
		try:
			return datetime.date.fromisoformat(arg)
		except ValueError:
			raise ValueError('Dates must be YYYY-MM-DD')
	if type(arg) is int:
		return TODAY + arg*DAY  # date relative to today


if __name__ == '__main__':
	import doctest
	doctest.testmod()
