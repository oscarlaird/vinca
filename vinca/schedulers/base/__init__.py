import datetime
DAY = datetime.timedelta(days=1)

def schedule(history):
	'''
	>>> import sys
	>>> sys.path.append('/home/oscar/vinca/vinca')
	>>> from history import test1, test2, test3, test4, test5
	>>> test1
	DATE          TIME    GRADE
	2021-11-07       0    create
	>>> schedule(test1)
	>>> test2
	DATE          TIME    GRADE
	2021-11-01       0    create
	2021-11-01      99    edit
	2021-11-01      11    exit
	2021-11-01     133    edit
	2021-11-01       9    good
	2021-11-02       9    good
	2021-11-05       2    exit
	2021-11-05       9    good
	>>> schedule(test2)
	datetime.date(2021, 11, 12)
	>>> test3
	DATE          TIME    GRADE
	2021-11-01       0    create
	2021-11-01      99    edit
	2021-11-05       9    hard
	>>> schedule(test3)
	datetime.date(2021, 11, 7)
	>>> test4
	DATE          TIME    GRADE
	2021-11-01       0    create
	2021-11-01      11    exit
	2021-11-01       9    good
	2021-11-05       9    again
	>>> schedule(test4)
	datetime.date(2021, 11, 5)
	>>> test5
	DATE          TIME    GRADE
	2021-11-01       0    create
	2021-11-01      11    edit
	2021-11-01       9    good
	2021-11-05       9    easy
	>>> schedule(test5)
	datetime.date(2021, 11, 18)
	'''


	if history.last_grade in history.admin_grades:
		return
	if history.last_grade == 'again':
		return history.last_date 
	if history.last_grade == 'hard':
		return history.last_date + DAY * (history.last_interval / 2).days
	if history.last_grade == 'good':
		return history.last_date + (history.last_interval * 2) + DAY
	if history.last_grade == 'easy':
		return history.last_date + (history.last_interval * 3) + DAY
	# TODO: An idea for grouping cards of a similar subject i.e. made on the same day
	# Round to the nearest multiple of 100 days after card creation if this is within 5% of the interval

if __name__ == '__main__':
	import doctest
	doctest.testmod()
