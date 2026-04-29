import pytest

from src.utils import *

from src.utils.ansi_style import ANSIStyle
from src.utils.command_parser import CommandParser

#--------------------------------------------------------------------------

class CustomIterable:
	def __iter__(self):
		return (_ for _ in ())

class CustomSequence:
	def __getitem__(self, _):
		return 0

class InvalidCustomIterable:
	def __iter__(self):
		return None

@pytest.mark.parametrize \
(
	"a,expected",
	[
		pytest.param([],                         True, id = 'list'),
		pytest.param((),                         True, id = 'tuple'),
		pytest.param({},                         True, id = 'dict'),
		pytest.param((_ for _ in range(1)),      True, id = 'generator'),
		pytest.param(map(lambda _: _, range(1)), True, id = 'map'),
		pytest.param(CustomIterable(),           True, id = 'custom iterable'),
		pytest.param(CustomSequence(),           True, id = 'custom sequence'),
		pytest.param(1,                          False, id = 'int'),
		pytest.param(1.2,                        False, id = 'float'),
		pytest.param("",                         False, id = 'string'),
		pytest.param(b"",                        False, id = 'bytes'),
		pytest.param(type('', (), {})(),         False, id = 'custom non-iterable'),
		pytest.param(InvalidCustomIterable(),    False, id = 'invalid custom iterable'),
	]
)
def test_collection_like(a, expected):
	assert collection_like(a) == expected

#--------------------------------------------------------------------------

@pytest.mark.parametrize \
(
	"a,expected",
	[
		pytest.param([1],                   1,   id = 'list'),
		pytest.param((1,),                  1,   id = 'tuple'),
		pytest.param({1,},                  1,   id = 'set'),
		pytest.param("a",                   'a', id = 'string'),
		pytest.param((_ for _ in [1]),      1,   id = 'generator'),
		pytest.param(map(lambda _: _, [1]), 1,   id = 'map'),
		pytest.param(1,                     TypeError,  id = 'non-iterable'),
		pytest.param([],                    ValueError, id = 'empty iterable'),
		pytest.param([1, 2],                ValueError, id = 'multiple values'),

	]
)
def test_single_value(a, expected):

	if isinstance(expected, type) and issubclass(expected, Exception):
		with pytest.raises(expected):
			single_value(a)
	else:
		assert single_value(a) == expected

#--------------------------------------------------------------------------

@pytest.mark.parametrize \
(
	"a,expected",
	[
		pytest.param([1, 2, 3],       {},                     id = 'all unique'),
		pytest.param([1, 5, 1, 2, 5], {1: [0, 2], 5: [1, 4]}, id = 'base case'),
	]
)
def test_duplicates_indexed(a, expected):
	assert duplicates_indexed(a) == expected

#--------------------------------------------------------------------------

@pytest.mark.parametrize \
(
	"a,expected",
	[
		pytest.param
		(
			[5, None, -1, None, 5, 5, '#', None, 5],
			[5, None, -1, '#'],
			id = 'base case'
		),
		pytest.param
		(
			[None, {'a': 1}, [0], {'b': 2}, [0], [1], {'a': 1}, {}],
			[None, {'a': 1}, [0], {'b': 2}, [1], {}],
			id = 'non-hashable elements'
		),
	]
)
def test_unique(a, expected):
	assert [*unique(a)] == expected

def test_len_plaintext():
	b1 = bytearray(random.randrange(256) for _ in range(10))

	s1 = b1.decode('utf-8', errors = 'backslashreplace')
	s2 = ANSIStyle.bold_blue(s1)

	assert len_plaintext(s2) == len(s1)

#--------------------------------------------------------------------------

def test_array_slice():
	a = list(range(10))
	s = ArraySlice(a)

	assert s == a
	assert s[1:5] == a[1:5]
	assert s[1:5][::-1][:2] == [4, 3]

	s[1:5][::-1][1] = -1
	assert a[3] == -1

def test_matrix():
	m = Matrix([[1, 2, 3], [4, 5, 6]])

	assert m.dim == (2, 3)
	assert [*m.rows] == [[1, 2, 3], [4, 5, 6]]
	assert [*m.cols] == [[1, 4], [2, 5], [3, 6]]
	assert m[0, 2] == 3
	assert m[1, 0] == 4

	with pytest.raises(IndexError):
		m[0, 3]

	with pytest.raises(IndexError):
		m[2, 0]

	assert Matrix.const((3, 2), '?') == Matrix([['?', '?'], ['?', '?'], ['?', '?']])

	assert [*m.ravel()] == [1, 2, 3, 4, 5, 6]

	assert m.transpose() == Matrix([[1, 4], [2, 5], [3, 6]])
	assert m.flatmap(lambda x: 2*x+1) == Matrix([[3, 5, 7], [9, 11, 13]])

#--------------------------------------------------------------------------

def test_command_parser():
	p = CommandParser(ignore_empty = True)

	assert p("") is None
	assert p("   ") is None
	assert p.parse("   ") is None

	assert p("   a   ")     == ('a', ())
	assert p("b")           == ('b', ())
	assert p("c 0")         == ('c', ('0',))
	assert p("f   x y z  ") == ('f', ('x', 'y', 'z'))

	with pytest.raises(AssertionError):
		p(5)
		p(None)
		p([])

	p1 = CommandParser(ignore_empty = False)

	with pytest.raises(ValueError):
		p1("")
		p1("   ")
