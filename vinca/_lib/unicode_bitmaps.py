quads_to_unicode = {((0,0),
 (0,0)):' ',
((0,0),
 (0,1)):'▗',
((0,0),
 (1,0)):'▖',
((0,0),
 (1,1)):'▄',
((0,1),
 (0,0)):'▝',
((0,1),
 (0,1)):'▐',
((0,1),
 (1,0)):'▞',
((0,1),
 (1,1)):'▟',
((1,0),
 (0,0)):'▘',
((1,0),
 (0,1)):'▚',
((1,0),
 (1,0)):'▌',
((1,0),
 (1,1)):'▙',
((1,1),
 (0,0)):'▀',
((1,1),
 (0,1)):'▜',
((1,1),
 (1,0)):'▛',
((1,1),
 (1,1)):'█'}

class Bitmap(list):
	def __init__(self, l):
		list.__init__(self, l)
		self.rows = len(self)
		self.cols = len(self[0])
		assert all((len(row) == self.cols for row in self))  # all rows of equal length

	@staticmethod
	def grouped_into_pairs(l):
		'''
		>>> Bitmap.grouped_into_pairs([1,2,3,4,5,6])
		[(1, 2), (3, 4), (5, 6)]
		'''
		return list(zip(l[::2], l[1::2]))

	@staticmethod
	def transposed(m):
		'''
		>>> Bitmap.transposed([[1,2], [3,4]])
		[[1, 3], [2, 4]]
		'''
		return [list(col) for col in zip(*m)]

	def has_even_rows_and_cols(self):
		'''
		>>> Bitmap([[0,1,0,1],[1,1,0,1]]).has_even_rows_and_cols()
		True
		'''
		return self.rows % 2 == 0 and self.cols % 2 == 0

	def group_quadrants(self):
		'''
		>>> Bitmap([[0,1,0,1],[1,1,0,1]]).group_quadrants()
		[[((0, 1), (1, 1)), ((0, 1), (0, 1))]]
		'''
		assert self.has_even_rows_and_cols()
		m = self
		m = [self.grouped_into_pairs(row) for row in m]
		m = self.transposed(m)
		m = [self.grouped_into_pairs(col) for col in m]
		m = self.transposed(m)
		return m

	def to_unicode(self):
		'''
		>>> Bitmap([[0,1,0,1],[1,1,0,1]]).to_unicode()
		'▟▐'
		'''
		m = self.group_quadrants()
		m = [[quads_to_unicode[q] for q in row] for row in m]
		m = [''.join(row) for row in m]
		m = '\n'.join(m)
		return m


if __name__ == '__main__':
	import doctest
	doctest.testmod()

