import datetime
from collections import namedtuple
to_date = datetime.date.fromisoformat

HistoryEntry = namedtuple('HistoryEntry', ['date','time','grade'])

class History(list):
	admin_grades = ('create', 'edit','exit','preview')

	@classmethod
	def from_json_list(cls, entries):
		'''
		>>> History.from_json_list([['2021-11-07',0,'create']])
		DATE          TIME    GRADE
		2021-11-07       0    create
		'''
		return cls([HistoryEntry(to_date(d), t, g) for d, t, g in entries])

	@property
	def create_date(self):
		'''
		>>> test2.create_date
		datetime.date(2021, 11, 1)
		'''
		assert self[0].grade == 'create'
		return self[0].date

	@property
	def time(self):
		'''
		>>> test2.time
		272
		'''
		return datetime.timedelta(seconds = sum([entry.time for entry in self]))

	@property
	def pure(self):
		'''
		>>> test2.pure
		DATE          TIME    GRADE
		2021-11-01       9    good
		2021-11-02       9    good
		2021-11-05       9    good
		'''
		# exclude administrative entries; only keep actual reviewing grades
		return History([entry for entry in self if entry.grade not in self.admin_grades])

	@property
	def last_interval(self):
		'''
		>>> test1.last_interval
		datetime.timedelta(0)
		>>> test3.last_interval
		datetime.timedelta(days=4)
		>>> test2.last_interval
		datetime.timedelta(days=3)
		'''
		pure = self.pure
		if len(pure) == 0:
			return datetime.timedelta(days=0)
		if len(pure) == 1:
			return pure[-1].date - self.create_date
		return pure[-1].date - pure[-2].date


	@property
	def last_grade(self):
		'''
		>>> test2.last_grade
		'good'
		'''
		return self[-1].grade

	@property
	def last_date(self):
		'''
		>>> test2.last_date
		datetime.date(2021, 11, 5)
		'''
		return self[-1].date

	def append_entry(self, date, time, grade):
		'''
		>>> test1
		DATE          TIME    GRADE
		2021-11-07       0    create
		>>> test1.append_entry(datetime.date(2021, 11, 1), 99, 'edit')
		>>> test1
		DATE          TIME    GRADE
		2021-11-07       0    create
		2021-11-01      99    edit
		'''
		assert type(date) is datetime.date	
		NewEntry = HistoryEntry(date, time, grade)
		self.append(NewEntry)

	@property
	def new(self):
		'''
		>>> test1.new
		True
		'''
		return len(self.pure) == 0

	def __repr__(self):
		s =  'DATE          TIME    GRADE\n'
		s += '\n'.join([f'{d}{t:8d}    {g}' for d, t, g in self])
		return s
	__str__ = __repr__

test1 = History([HistoryEntry('2021-11-07',0,'create')])
test2 = History([
	HistoryEntry(date=datetime.date(2021, 11, 1), time=0, grade='create'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=99, grade='edit'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=11, grade='exit'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=133, grade='edit'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=9, grade='good'),
	HistoryEntry(date=datetime.date(2021, 11, 2), time=9, grade='good'),
	HistoryEntry(date=datetime.date(2021, 11, 5), time=2, grade='exit'),
	HistoryEntry(date=datetime.date(2021, 11, 5), time=9, grade='good')])
test3 = History([
	HistoryEntry(date=datetime.date(2021, 11, 1), time=0, grade='create'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=99, grade='edit'),
	HistoryEntry(date=datetime.date(2021, 11, 5), time=9, grade='hard')])
test4 = History([
	HistoryEntry(date=datetime.date(2021, 11, 1), time=0, grade='create'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=11, grade='exit'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=9, grade='good'),
	HistoryEntry(date=datetime.date(2021, 11, 5), time=9, grade='again')])
test5 = History([
	HistoryEntry(date=datetime.date(2021, 11, 1), time=0, grade='create'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=11, grade='edit'),
	HistoryEntry(date=datetime.date(2021, 11, 1), time=9, grade='good'),
	HistoryEntry(date=datetime.date(2021, 11, 5), time=9, grade='easy')])

if __name__ == '__main__':
	import doctest
	doctest.testmod()


