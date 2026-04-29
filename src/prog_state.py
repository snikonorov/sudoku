"""
All the functionality for handling program state, including user interaction and rendering
"""
from dataclasses import dataclass
from typing import Mapping, Protocol, Collection

import textwrap

import itertools

import random

import colorama

import src.sudoku as sudoku

from src.utils.command_parser import CommandParser
from src.utils.ansi_style import ANSIStyle
import src.utils as utils

#--------------------------------------------------------------------------

colorama.just_fix_windows_console()

#--------------------------------------------------------------------------

@dataclass
class TState:
	"""
	A consolidated state of the program
	"""
	solution:      sudoku.Grid
	main_grid:     sudoku.Grid
	cmd_parser:    CommandParser
	cl_args:       dict

	prefilled_pos: 'Collection[tuple]' = ...
	reveal_order:  'Collection[tuple]' = ...
	label2pos:	   Mapping[str, tuple] = ...
	pos2label:     Mapping[tuple, str] = ...

	def __post_init__(self):
		g = self.main_grid

		if self.prefilled_pos is ...:
			m = g.data

			self.prefilled_pos = \
			{
				pos
				for pos in g.pos_range()
				if m[pos] != g.EMPTY
			}

		if self.reveal_order is ...:
			m = g.data

			empty_pos = \
			[
				pos
				for pos in g.pos_range()
				if m[pos] == g.EMPTY
			]

			self.reveal_order = utils.shuffled(empty_pos)

		if self.label2pos is ...:
			indexed_row_labels = enumerate(g.row_labels())
			indexed_col_labels = enumerate(g.col_labels())

			base_label = lambda R, C: f"{R}{C}"

			label = \
			(
				(lambda *args: base_label(*args).upper())
					if self.cl_args.get('ignore-case') else
				base_label
			)

			self.label2pos = \
			{
				label(R, C): (r, c)
				for ((r, R), (c, C)) in itertools.product(indexed_row_labels, indexed_col_labels)
			}

			self.pos2label = \
			{
				val: key
				for key, val in self.label2pos.items()
			}

def init(cl_args: dict) -> TState:
	"""Initial state"""

	solution = sudoku.random()
	main_grid = sudoku.Grid()

	pos_range = [*main_grid.pos_range()]

	n_prefilled = cl_args.get('num-prefilled', 30)
	n_prefilled = min(len(pos_range), max(0, n_prefilled))

	prefilled_pos = random.sample(pos_range, k = n_prefilled)

	for pos in prefilled_pos:
		main_grid.data[pos] = solution.data[pos]

	state = TState \
	(
		solution = solution,
		main_grid = main_grid,
		cmd_parser = CommandParser(ignore_empty = True),
		cl_args = cl_args,
		prefilled_pos = set(prefilled_pos)
	)

	return state

#-------------------------------------------------
# input/state handling

class TCommand(Protocol):
	def __call__(self, state: TState, *args):
		...

def _highlight(state: TState, msg):
	if state.cl_args['mode'] == 'text-color':
		msg = ANSIStyle.blue_bold(msg)
	print(msg)

def _warning(state: TState, msg):
	if state.cl_args['mode'] == 'text-color':
		msg = ANSIStyle.yellow(msg)
	print(msg)

def _error(state: TState, msg):
	if state.cl_args['mode'] == 'text-color':
		msg = ANSIStyle.red(msg)
	print(msg)

def _help(_):
	print \
	(
		textwrap.dedent(
		"""
		Supported commands:
		help            Print this message
		put <pos> <val> Put a value <val> at position <pos>, e.g. `put C2 5` will fill cell C2 with 5
		clear <pos>     Clear cell at position <pos>
		hint            Get a hint for one unfilled cell
		check           Check the grid for any conflicts (same-row duplication etc.)
		new             Start a new puzzle
		quit            Quit the program
		"""
		).strip()
	)

def _reinit(state: TState):
	new_state = init(state.cl_args)

	state.solution = new_state.solution
	state.main_grid = new_state.main_grid
	state.prefilled_pos = new_state.prefilled_pos
	state.reveal_order = new_state.reveal_order

	state.__post_init__()

def _check_value(state: TState, val):
	value_range = set(state.main_grid.value_range())

	if val not in value_range:
		_warning(state, f"Invalid value for the cell: {val}")
		return False

	return True

def _check_position(state: TState, pos_label):

	if pos_label not in state.label2pos:
		_warning(state, f"Invalid position: {pos_label}")
		return False

	return True

def _check_prefilled(state: TState, pos_label):
	pos = state.label2pos[pos_label]

	if pos in state.prefilled_pos:
		_warning(state, f"Invalid move: {pos_label} is pre-filled")
		return False

	return True

@utils.with_eav
def _put(state: TState, pos_label: str, val):

	if state.cl_args.get('ignore-case'):
		pos_label = pos_label.upper()

	if not _check_value(state, val):
		return

	if not _check_position(state, pos_label):
		return

	if not _check_prefilled(state, pos_label):
		return

	pos = state.label2pos[pos_label]
	state.main_grid.data[pos] = val

	if state.main_grid.is_solved():
		_highlight(state, "Puzzle solved!")
		input("Press Enter to play again...")
		_reinit(state)

@utils.with_eav
def _clear(state: TState, pos_label: str):
	if state.cl_args.get('ignore-case'):
		pos_label = pos_label.upper()

	if not _check_position(state, pos_label):
		return

	if not _check_prefilled(state, pos_label):
		return

	pos = state.label2pos[pos_label]
	state.main_grid.data[pos] = state.main_grid.EMPTY

@utils.with_eav
def _hint(state: TState):
	g = state.main_grid
	m = g.data

	pos = None
	for pos in state.reveal_order:
		if m[pos] == g.EMPTY:
			break

	all_filled = pos is None

	if all_filled and state.main_grid.is_solved():
		print("The puzzle is already solved")
		return None

	if all_filled:
		print("Every cell is already filled")
		return None

	pos_label = state.pos2label[pos]
	val = state.solution.data[pos]

	_highlight(state, f"Hint: {pos_label} is {val}")
	return (pos_label, val)

@utils.with_eav
def _check(state: TState):
	errors = state.main_grid.validate()

	if not isinstance(errors, Exception):
		print("No rule violations")
		return

	if not isinstance(errors, sudoku.ConsolidatedException):
		raise ValueError(f"unexpected validation result: {errors}")

	for e in errors:
		_highlight(state, e)

@utils.with_eav
def _new(state: TState):
	_reinit(state)

def _quit(_):
	exit(0)

_HANDLERS = \
{
	'help':  _help,
	'put':   _put,
	'clear': _clear,
	'hint':  _hint,
	'check': _check,
	'new':   _new,
	'quit':  _quit
}

@utils.with_eav(exception_types = (Exception, KeyboardInterrupt))
def handle_input(state: TState):
	verbose = state.cl_args.get('verbose', False)

	cmd = input()
	cmd_parsed = utils.with_eav(state.cmd_parser)(cmd)

	if isinstance(cmd_parsed, Exception):
		if verbose:
			_error(state, f"Error parsing command: {cmd_parsed}")
		return

	if cmd_parsed is None:
		return

	(name, args) = cmd_parsed

	if name not in _HANDLERS:
		_warning(state, f"Unknown command: {name!r}")
		return

	res = _HANDLERS[name](state, *args)
	return res

#-------------------------------------------------
# rendering

def render_frame(state: TState):
	print()

	grid_rendered = sudoku.render \
	(
		state.main_grid,
		kind = state.cl_args['mode'],
		fixed_pos = state.prefilled_pos
	)

	print(grid_rendered)
	print()

	print("Enter command (enter 'help' for more information)")
	print("> ", end = '')
