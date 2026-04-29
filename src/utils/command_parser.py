from dataclasses import dataclass

import re

#--------------------------------------------------------------------------

@dataclass
class CommandParser:
	"""
	A simple command parser. Command strings of form `command_name args1 arg2 ...` are expected.

	Params:
		ignore_empty: bool (default: False)
			Specifies whether (effectively) empty command line should be ignored or treated as an error
	"""

	ignore_empty: bool = True

	def __call__(self, raw_cmd: str) -> 'tuple[str, tuple[str]] | None':
		assert isinstance(raw_cmd, str)

		raw_parts = re.split(r"\s+", raw_cmd)
		parts = [p for p in raw_parts if p]

		if len(parts) == 0:
			if self.ignore_empty:
				return None
			raise ValueError("empty command")

		name = parts[0]
		args = tuple(parts[1:])

		return (name, args)

	def parse(self, raw_cmd):
		return self(raw_cmd)
