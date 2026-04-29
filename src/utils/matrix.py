from collections.abc import Sequence
from dataclasses import dataclass
from typing import Collection, MutableSequence

from .misc import single_value

#--------------------------------------------------------------------------

@dataclass(repr = False)
class ArraySlice(MutableSequence):
	"""
	A *mutable* array slice
	"""
	root:  MutableSequence
	range: range           = ...

	def __post_init__(self):
		if self.range is ...:
			self.range = range(0, len(self.root))

		assert isinstance(self.range, range)

	def _resolve_index(self, idx) -> 'int | range':
		assert isinstance(idx, (int, slice))
		return self.range[idx]

	def __getitem__(self, idx):
		r = self._resolve_index(idx)

		if isinstance(r, range):
			return ArraySlice(self.root, r)

		return self.root[r]

	def __setitem__(self, idx, val):
		r = self._resolve_index(idx)

		if isinstance(r, range):
			for k, v in zip(r, val):
				self.root[k] = v
			return

		self.root[r] = val

	def __delitem__(self, _):
		raise NotImplementedError

	def insert(self, *_):
		raise NotImplementedError

	def __len__(self):
		return len(self.range)

	def __iter__(self):
		return (self.root[idx] for idx in self.range)

	def __eq__(self, other: Sequence):
		return \
		(
			len(self) == len(other) and
			all(a == b for a, b in zip(self, other))
		)

	def __repr__(self):
		return f"{list(self)}"

class Matrix:
	"""
	A light-weight matrix class using native Python types and minimal interface
	(as using numpy may or may not be an overkill for this project).
	Values are mutable but the dimensions are not.
	"""
	__slots__ = ('_dim', '_buffer')

	def __init_unchecked__(self, dim, buffer):
		self._dim = dim
		self._buffer = buffer

	def __init__(self, rows: 'Collection | Matrix' = None):
		if not rows:
			rows = [[]]

		if isinstance(rows, type(self)):
			rows = rows.rows

		l1 = len(rows)

		l2 = single_value \
		(
			set(map(len, rows)),
			error_multi = ValueError("cannot construct a matrix from a ragged array")
		)

		self.__init_unchecked__ \
		(
			dim = (l1, l2),
			buffer = [val for row in rows for val in row]
		)

	@classmethod
	def const(cls, dim: tuple, val = 0):
		"""
		Creates a new matrix given the dimensions and fills it with `val`
		"""
		assert len(dim) == 2
		N = dim[0] * dim[1]

		res = object.__new__(cls)
		res.__init_unchecked__(dim = dim, buffer = [val]*N)
		return res

	@property
	def dim(self):
		return self._dim

	def __len__(self):
		return len(self._buffer)

	def pos2index(self, pos: tuple):
		assert isinstance(pos, tuple)
		assert len(pos) == 2
		assert all(isinstance(k, int) for k in pos)

		if any(p >= d for p, d in zip(pos, self.dim)):
			raise IndexError("index out of range")

		return pos[0]*self.dim[1] + pos[1]

	def index2pos(self, idx: int):
		return divmod(idx, self.dim[1])

	def __getitem__(self, pos):
		return self._buffer[self.pos2index(pos)]

	def __setitem__(self, pos, val):
		self._buffer[self.pos2index(pos)] = val

	@property
	def rows(self):
		l1 = self.dim[0]
		l2 = self.dim[1]
		root = self._buffer

		return \
		[
			ArraySlice(root, range(k*l2, (k + 1)*l2))
			for k in range(l1)
		]

	@property
	def cols(self):
		l2 = self.dim[1]
		N = len(self)
		root = self._buffer

		return \
		[
			ArraySlice(root, range(k, N-l2+k+1, l2))
			for k in range(l2)
		]

	def ravel(self):
		return iter(self._buffer)

	def flatmap(self, f, inplace = False):
		if inplace:
			res = self
		else:
			res = type(self)(self)

		for k in range(len(res._buffer)):
			res._buffer[k] = f(res._buffer[k])

		return res

	def transpose(self, inplace = False):
		res = type(self)(self.cols)

		if inplace:
			self.__init_unchecked__(dim = res._dim, buffer = res._buffer)
			res = self

		return res

	def __eq__(self, other):
		assert isinstance(other, type(self))
		return self._dim == other._dim and self._buffer == other._buffer

	def __repr__(self):
		_tab = lambda k: '' if k == 0 else ' '

		row_reprs = \
		[
			_tab(k) + repr(row)
			for k, row in enumerate(self.rows)
		]

		return '[' + ',\n'.join(row_reprs) + ']'
