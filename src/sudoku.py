"""
Implementation of a Sudoku grid and some utilities to work with it (e.g. generating a random puzzle)
"""
from dataclasses import dataclass
from typing import Iterable, Literal, Collection

import itertools

from copy import deepcopy

from src.utils import Matrix
import src.utils as utils

from src.utils.ansi_style import ANSIStyle

#--------------------------------------------------------------------------

class ExceptionExt(Exception):
	"""(just an Exception with a `kwargs` attribute)"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args)
		self.kwargs = kwargs

class ValidationError(Exception):
	"""(a root for all exceptions emitted by `Grid.validate`)"""
	...

class DuplicatedNumberError(ExceptionExt, ValidationError):
	REQUIRED_KWARGS = {'value', 'loc'}
	OPTIONAL_KWARGS = {'loc_labels'}

	@classmethod
	def kwargs_validated(cls, **kwargs):
		if missing := cls.REQUIRED_KWARGS - kwargs.keys():
			raise ValueError(f"missing required arguments: {missing}")

		kwargs.setdefault('loc_labels', [*map(str, kwargs['loc'])])
		return kwargs

	@classmethod
	def format_message(cls, *, value, loc_labels, **_):
		return f"{value} is duplicated at: ({', '.join(loc_labels)})"

	def __init__(self, **kwargs):
		kwargs = self.kwargs_validated(**kwargs)
		msg = self.format_message(**kwargs)
		super().__init__(msg, **kwargs)

class DuplicatedNumberInRow(DuplicatedNumberError):
	@classmethod
	def format_message(cls, **kwargs):
		return "invalid row: " + super().format_message(**kwargs)

class DuplicatedNumberInColumn(DuplicatedNumberError):
	@classmethod
	def format_message(cls, **kwargs):
		return "invalid column: " + super().format_message(**kwargs)

class DuplicatedNumberInSubgrid(DuplicatedNumberError):
	@classmethod
	def format_message(cls, *, value, loc_labels, **_):
		return f"invalid subgrid: {value} is duplicated in: ({', '.join(loc_labels)})"

class ConsolidatedException(Exception):
	"""Represents a collection of exceptions"""
	def __iter__(self):
		return iter(self.args)

#--------------------------------------------------------------------------

@dataclass(repr = False)
class Grid:
	EMPTY = '_'
	SIZE = 9
	SUBGRID_SIZE = 3

	data: Matrix = None

	def __post_init__(self):
		valid_dim = (self.SIZE, self.SIZE)

		if self.data is None:
			self.data = Matrix.const(valid_dim, val = self.EMPTY)

		if not isinstance(self.data, Matrix):
			self.data = Matrix(self.data)

		if self.data.dim != valid_dim:
			raise ValueError(f"invalid grid size, expected: {valid_dim}, got: {self.data.dim}")

	@classmethod
	def value_range(cls):
		return map(str, range(1, cls.SIZE + 1))

	@classmethod
	def pos_range(cls):
		N = cls.SIZE
		return itertools.product(range(N), range(N))

	@classmethod
	def row_labels(cls) -> 'list[str]':
		return [chr(ord('A') + k) for k in range(cls.SIZE)]

	@classmethod
	def col_labels(cls) -> 'list[str]':
		return [*map(str, range(1, cls.SIZE + 1))]

	@classmethod
	def subgrid_labels(cls) -> 'list[str]':
		N = cls.SIZE
		n = cls.SUBGRID_SIZE
		R = cls.row_labels()
		C = cls.col_labels()

		return \
		[
			f"{R[X]}{C[Y]}..{R[X+n-1]}{C[Y+n-1]}"
			for X, Y in itertools.product(range(0, N, n), range(0, N, n))
		]

	def subgrid_at(self, X, Y):
		n = self.SUBGRID_SIZE
		return \
		[
			self.data[x, y]
			for x, y in itertools.product(range(n*X, n*(X+1)), range(n*Y, n*(Y+1)))
		]

	def subgrids(self):
		n = self.SUBGRID_SIZE
		return \
		(
			self.subgrid_at(X, Y)
			for X, Y in itertools.product(range(n), range(n))
		)

	def valid_values_at(self, pos):
		m = self.data

		if m[pos] != self.EMPTY:
			return set()

		n = self.SUBGRID_SIZE
		(r, c) = pos

		res = \
		(
			set(self.value_range())
			- set(m.rows[r])
			- set(m.cols[c])
			- set(self.subgrid_at(r // n, c // n))
		)

		return res

	def validate(self) -> 'Any | ConsolidatedException':
		"""
		Checks the grid for rule violations and wraps them in `ConsolidatedException` if any
		"""
		def _duplicates(s: Iterable):
			d = utils.duplicates_indexed(s)
			res = {key: val for key, val in d.items() if key != self.EMPTY}
			return res

		def _exceptions(s: Iterable, exception_type, index_to_pos, index_to_label):
			return \
			(
				exception_type
				(
					value      = val,
					loc        = [*utils.unique(map(index_to_pos, idxs))],
					loc_labels = [*utils.unique(map(index_to_label, idxs))]
				)
				for val, idxs in _duplicates(s).items()
			)

		def _subgrid2pos(subgrid_idx, val_idx):
			N = self.SIZE
			n = self.SUBGRID_SIZE

			m = N // n

			x = (subgrid_idx // m) * n + val_idx // n
			y = (subgrid_idx % m) * n + val_idx % n

			return (x, y)

		#-------------------------------------------------

		row_labels = self.row_labels()
		col_labels = self.col_labels()

		res = []

		for row_idx, (label, s) in enumerate(zip(row_labels, self.data.rows)):
			e = _exceptions \
			(
				s,
				DuplicatedNumberInRow,
				lambda idx: (row_idx, idx),
				lambda idx: f"{label}{col_labels[idx]}"
			)
			res.extend(e)

		for col_idx, (label, s) in enumerate(zip(col_labels, self.data.cols)):
			e = _exceptions \
			(
				s,
				DuplicatedNumberInColumn,
				lambda idx: (idx, col_idx),
				lambda idx: f"{row_labels[idx]}{label}"
			)
			res.extend(e)

		for subgrid_idx, (label, s) in enumerate(zip(self.subgrid_labels(), self.subgrids())):
			e = _exceptions \
			(
				s,
				DuplicatedNumberInSubgrid,
				lambda idx: _subgrid2pos(subgrid_idx, idx),
				lambda idx: label
			)
			res.extend(e)

		if res:
			return ConsolidatedException(*res)

		return None

	def is_solved(self):
		val_range = set(self.value_range())

		any_empty = lambda: any(v == self.EMPTY for v in self.data.ravel())
		valid_rows = lambda: all(set(row) == val_range for row in self.data.rows)
		valid_cols = lambda: all(set(col) == val_range for col in self.data.cols)
		valid_subgrids = lambda: all(set(g) == val_range for g in self.subgrids())

		if not any_empty() and valid_rows() and valid_cols() and valid_subgrids():
			return True

		return False

	def __str__(self):
		return render('text-plain')

#--------------------------------------------------------------------------

def random(grid_class: 'type[Grid]' = Grid) -> Grid:
	"""
	Returns a new randomly generated solved `Grid`
	"""
	N = grid_class.SIZE
	EMPTY = grid_class.EMPTY

	g = grid_class()
	m = g.data

	#-------------------------------------------------------
	# pre-fill

	m.rows[0][:] = utils.shuffled(grid_class.value_range())

	#-------------------------------------------------------
	# filling the rest

	# _pos_sequence = shuffled(grid_class.pos_range())
	_pos_sequence = [*grid_class.pos_range()]

	n_cells = N*N

	def _complete(_idx = 0):
		nonlocal g
		nonlocal m

		if _idx == n_cells:
			return True

		pos = _pos_sequence[_idx]

		if m[pos] != EMPTY:
			return _complete(_idx+1)

		vals = g.valid_values_at(pos)

		for val in utils.shuffled(vals):
			m[pos] = val

			if _complete(_idx+1):
				return True

		m[pos] = EMPTY
		return False

	_complete()

	#-------------------------------------------------------

	return g

#--------------------------------------------------------------------------

def render(g: Grid, *, kind: Literal['text-plain', 'text-color'] = 'text-color', **kwargs):
	"""
	Renders a Grid based on the `kind`. Currently, the following values of `kind` are supported:
	  - 'text-plain': render a Grid as plain text
	  - 'text-color': similar to 'text-plain', but with the addition of highlight color to prefilled and conflicting cells
	"""
	return \
	{
		'text-plain': _render_text_plain,
		'text-color': _render_text_color
	} \
	[kind](g, **kwargs)

#-------------------------------------------------------

def _render_text_plain(g: Grid, *, row_sep = '-', col_sep = '|', cross = '+', **_):
	row_labels = g.row_labels()
	col_labels = g.col_labels()

	m = g.data.flatmap(str)

	max_len = lambda _: max(map(utils.len_plaintext, _))

	N = g.SIZE
	n = g.SUBGRID_SIZE

	col_widths = \
	[
		max(utils.len_plaintext(label), max_len(col))
		for label, col in zip(col_labels, m.cols)
	]

	row_label_width = max_len(row_labels)

	#-------------------------------------------------------

	def band_separator():
		sep_parts = \
		[
			row_sep * (sum(col_widths[i:i+3]) + 4)
			for i in range(0, N, 3)
		]
		return row_sep * (row_label_width + 1) + cross + cross.join(sep_parts)

	def is_at_band_border(idx):
		return (idx + 1) % n == 0 and idx < N - 1

	def format_row(row, label):
		return \
		(
			f"{label.ljust(row_label_width)} {col_sep} " +
			''.join
			(
				f"{val.ljust(col_widths[col_idx])} " +
				(
					col_sep + ' '
						if is_at_band_border(col_idx) else
					''
				)
				for col_idx, val in enumerate(row)
			)
		)

	#-------------------------------------------------------

	lines = \
	[
		format_row(col_labels, ' ' * row_label_width),
		band_separator(),
		*(
			format_row(row, row_labels[row_idx]) +
			(
				'\n' + band_separator()
					if is_at_band_border(row_idx) else
				''
			)
			for row_idx, row in enumerate(m.rows)
		)
	]

	return '\n'.join(lines)

def _render_text_color(g: Grid, *, fixed_pos: Collection[tuple] = (), **_):
	g = deepcopy(g)
	m = g.data

	#-------------------------------------------------------
	# highlighting conflicting cells

	errors = g.validate()

	if isinstance(errors, ConsolidatedException):

		for e in errors:
			loc = e.kwargs.get('loc')
			if not loc:
				continue

			for pos in loc:
				m[pos] = ANSIStyle.bold_blue(m[pos])

	#-------------------------------------------------------
	# highlighting pre-filled cells

	for pos in fixed_pos:
		m[pos] = ANSIStyle.bold(m[pos])

	#-------------------------------------------------------

	return _render_text_plain(g)
