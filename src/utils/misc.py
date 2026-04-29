"""
General utilities and helpers
"""
from functools import wraps

from typing import Iterable

import re

import pickle

import random

#--------------------------------------------------------------------------

def collection_like(a):
	"""
	Checks whether `a` is an iterable, but treats bytes and strings as atomic
	"""
	try:
		if isinstance(a, (str, bytes)):
			raise TypeError
		iter(a)
		return True
	except TypeError:
		return False

def single_value \
(
	a: Iterable,
	*,
	error_empty = ValueError("an iterable is empty"),
	error_multi = ValueError("an iterable contains multiple values")
):
	"""
	Checks that an iterable contains one and only one value and returns it.
	Examples:
	>>> single_value([1])
	1
	>>> single_value({2})
	2
	>>> single_value(range(2, 3))
	2
	>>> single_value([1, 2])
	Traceback (most recent call last):
	...
	ValueError: an iterable contains multiple values
	>>> single_value([])
	Traceback (most recent call last):
	...
	ValueError: an iterable is empty
	"""
	class UNDEFINED: pass
	res = UNDEFINED

	for v in a:
		if res is not UNDEFINED:
			raise error_multi
		res = v

	if res is UNDEFINED:
		raise error_empty

	return res

def duplicates_indexed(a: Iterable) -> dict:
	"""
	Returns a dictionary `{<duplicate value>: [<duplicate indices...>]}`.
	Examples:
	>>> duplicates_indexed([1, 2, 3])
	{}
	>>> duplicates_indexed([5, 2, 5, 1, 3, 2])
	{5: [0, 2], 2: [1, 5]}
	"""
	g = {}
	for idx, v in enumerate(a):
		g.setdefault(v, []).append(idx)

	res = {key: val for key, val in g.items() if len(val) > 1}
	return res

def shuffled(a: Iterable):
	a = list(a)
	random.shuffle(a)
	return a

def hashable_repr(obj):
	"""
	Returns a unique (*) hashable representation of `obj`;
	if `obj` is already hashable returns `obj` itself

	(*) s.t. uniqueness of the `pickle.dumps` transformation
	"""

	try:
		if isinstance(obj, bytes):
			# because `pickle.dumps` returns `bytes`, so there could be a clash (see below)
			raise TypeError

		hash(obj)
		return obj

	except Exception:
		return pickle.dumps(obj)

def unique(L: Iterable) -> Iterable:
	"""
	Like `set(L)`, but preserves the original element order
	and allows unhashable (but pickleable) items to be present in `L`

	Examples:

	>>> [*unique([5, None, -1, None, 5, 5, '#', None, 5])]
	[5, None, -1, '#']

	>>> [*unique([None, {'a': 1}, [0], {'b': 2}, {'a': 1}, {}])]
	[None, {'a': 1}, [0], {'b': 2}, {}]
	"""

	seen = set()

	for obj in L:
		if (h := hashable_repr(obj)) not in seen:
			seen.add(h)
			yield obj

def dot_apply(*F):
	"""
	reverse function composition, i.e.:
	   `dot_apply(f1, f2, f3) == x -> f3(f2(f1(x)))`

	the name comes from the fact that the result resembles a chain method call:
	   `x -> x.f1().f2().f3()`
	"""

	if not F:
		return lambda x: x

	(head, tail) = (F[0], F[1:])

	def __f(*args, **kwargs):
		nonlocal head, tail

		x = head(*args, **kwargs)

		for f in tail:
			x = f(x)

		return x

	return __f

def len_plaintext(s: str):
	"""
	length of `s` with ANSI control sequences stripped
	"""
	ansi_escape = r"\x1b\[[0-?]*[ -/]*[@-~]"
	return len(re.sub(ansi_escape, '', s))

def with_eav(f = ..., *, exception_types = (Exception,)):
	"""
	'With Exceptions As Value' function wrapper - if any exceptions occur, catches all and returns them as a result
	"""
	if f is ...:
		return lambda f: with_eav(f, exception_types = exception_types)

	@wraps(f)
	def _f(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except exception_types as e:
			return e

		return Exception("unexpected execution branch")

	return _f
