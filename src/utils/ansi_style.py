from src.utils import dot_apply

#--------------------------------------------------------------------------------

class ANSIStyleMeta(type):
	"""
	This metaclass will instantiate methods based on the `CODES.keys()`.
	It also allows to 'chain' the names together on attribute access, e.g. 'bold_blue', 'green_italic' etc.
	"""

	CODES = \
	{
		#'reset':     '0',
		'bold':      '1',
		'dim':       '2',
		'italic':    '3',
		'underline': '4',
		'blink':     '5',
		'reverse':   '7',
		'hidden':    '8',
		'strike':    '9',
		'black':     '30',
		'red':       '31',
		'green':     '32',
		'yellow':    '33',
		'blue':      '34',
		'magenta':   '35',
		'cyan':      '36',
		'white':     '37',
	}

	@classmethod
	def instantiate_method(cls, name, color_code):

		@classmethod
		def method_template(_, s: str):
			return f"\033[{color_code}m{s}\033[0m"

		method_template.__name__ = name

		return method_template

	def __new__(cls, cls_name, bases, namespace):
		namespace.update \
		(
			(name, cls.instantiate_method(name, code))
			for name, code in cls.CODES.items()
		)

		return super().__new__(cls, cls_name, bases, namespace)

	def __getattr__(cls, attr):
		return dot_apply(*map(super().__getattribute__, attr.split('_')))

class ANSIStyle(metaclass = ANSIStyleMeta):
	"""
	Usage examples:
	>>> ANSIStyle.bold("!")
	>>> ANSIStyle.blue("!")
	>>> ANSIStyle.bold_blue("!!")
	>>> ANSIStyle.blue_bold("!!")
	"""
	pass
