"""
Entry point
"""
import sys
import argparse

import src.prog_state as ps

#--------------------------------------------------------------------------
# command line parser

def get_cl_parser():
	p = argparse.ArgumentParser \
	(
		prog = '',
		description = 'A command-line sudoku'
	)

	p.add_argument \
	(
		'--mode',
		default = 'text-color',
		choices = ['text-plain', 'text-color'],
		help =
		(
			"Grid rendering mode - either plain text or colored text (default: 'text-color'); "
			"select 'text-plain' option if you see weird strings of symbols in the middle of the grid and no color"
		)
	)

	p.add_argument \
	(
		'--num-prefilled',
		dest = 'num-prefilled',
		type = int,
		default = 30,
		help =
		(
			"Number of the pre-filled cells at the start of the game (default: 30); "
			"negative values or values greater than the total number of cells will be capped appropriately"
		)
	)

	p.add_argument \
	(
		'--ignore-case',
		dest = 'ignore-case',
		action = 'store_true',
		help =
		(
			"Make sudoku command arguments case-insensitive (case-sensitive by default)"
			", e.g. when specifying a cell position, with this flag 'C5' and 'c5' are equivalent"
		)
	)

	p.add_argument \
	(
		'--verbose',
		action = 'store_true',
		help = "Print all information/debug messages"
	)

	return p

#--------------------------------------------------------------------------

if __name__ == "__main__":

	#-------------------------------------------------------
	# command line

	cl_parser = get_cl_parser()
	cl_ns = cl_parser.parse_args(sys.argv[1:])
	cl_args = dict(cl_ns.__dict__)

	#-------------------------------------------------------
	# initialization

	state = ps.init(cl_args)

	#-------------------------------------------------------
	# main loop

	print()
	print("Welcome to Sudoku!")

	while True:
		ps.render_frame(state)
		res = ps.handle_input(state)

		if isinstance(res, KeyboardInterrupt):
			exit(0)

		if isinstance(res, BaseException) and cl_args.get('verbose'):
			ps._error(state, f"An unexpected error occurred while handling the input: {res!r}")
