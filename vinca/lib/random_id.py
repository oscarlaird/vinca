import random
import string

def random_id():
	'''
	>>> len(random_id())
	8
	>>> type(random_id())
	<class 'str'>
	>>> 'AAAAAAAA' < random_id() < 'zzzzzzzz'
	True
	'''
	return ''.join(random.choices(string.ascii_letters, k=8))


if __name__ == '__main__':
	import doctest
	doctest.testmod()
