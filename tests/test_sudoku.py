import pytest

import src.sudoku as sudoku

#--------------------------------------------------------------------------

def test_invalid_sudoku():
	with pytest.raises(ValueError):
		sudoku.Grid([])

	with pytest.raises(ValueError):
		sudoku.Grid([[1, 2], [3, 4]])

def test_random_sudoku():

	for _ in range(20):
		s = sudoku.random()

		assert not isinstance(s.validate(), Exception)
		assert s.is_solved()

		m = s.data

		v0 = m[3, 3]
		m[3, 3] = m[4, 4]

		assert isinstance(s.validate(), Exception)
		assert not s.is_solved()

		m[3, 3] = v0
