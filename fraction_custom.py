from fractions import Fraction
from decimal import Decimal
import numbers, re

Rational = numbers.Rational


_RATIONAL_FORMAT = re.compile(r"""
	\A\s*					  # optional whitespace at the start, then
	(?P<sign>[-+]?)			# an optional sign, then
	(?=\d|\.\d)				# lookahead for digit or .digit
	(?P<num>\d*)			   # numerator (possibly empty)
	(?:						# followed by
	   (?:/(?P<denom>\d+))?	# an optional denominator
	|						  # or
	   (?:\.(?P<decimal>\d*))? # an optional fractional part
	   (?:E(?P<exp>[-+]?\d+))? # and optional exponent
	)
	\s*\Z					  # and optional whitespace to finish
""", re.VERBOSE | re.IGNORECASE)


class NonreducedFraction(Fraction):
	"""This class implements rational numbers.

	In the two-argument form of the constructor, Fraction(8, 6) will
	produce a rational number equivalent to 4/3. Both arguments must
	be Rational. The numerator defaults to 0 and the denominator
	defaults to 1 so that Fraction(3) == 3 and Fraction() == 0.

	Fractions can also be constructed from:

	  - numeric strings similar to those accepted by the
		float constructor (for example, '-2.3' or '1e10')

	  - strings of the form '123/456'

	  - float and Decimal instances

	  - other Rational instances (including integers)

	"""

	__slots__ = ('_numerator', '_denominator')

	# We're immutable, so use __new__ not __init__
	def __new__(cls, numerator=0, denominator=None):
		"""Constructs a Fraction.

		Takes a string like '3/2' or '1.5', another Rational instance, a
		numerator/denominator pair, or a float.

		Examples
		--------

		>>> Fraction(10, -8)
		Fraction(-5, 4)
		>>> Fraction(Fraction(1, 7), 5)
		Fraction(1, 35)
		>>> Fraction(Fraction(1, 7), Fraction(2, 3))
		Fraction(3, 14)
		>>> Fraction('314')
		Fraction(314, 1)
		>>> Fraction('-35/4')
		Fraction(-35, 4)
		>>> Fraction('3.1415') # conversion from numeric string
		Fraction(6283, 2000)
		>>> Fraction('-47e-2') # string may include a decimal exponent
		Fraction(-47, 100)
		>>> Fraction(1.47)  # direct construction from float (exact conversion)
		Fraction(6620291452234629, 4503599627370496)
		>>> Fraction(2.25)
		Fraction(9, 4)
		>>> Fraction(Decimal('1.47'))
		Fraction(147, 100)

		"""
		self = super(Fraction, cls).__new__(cls)

		if denominator is None:
			if isinstance(numerator, Rational):
				self._numerator = numerator.numerator
				self._denominator = numerator.denominator
				return self

			elif isinstance(numerator, float):
				# Exact conversion from float
				value = Fraction.from_float(numerator)
				self._numerator = value._numerator
				self._denominator = value._denominator
				return self

			elif isinstance(numerator, Decimal):
				value = Fraction.from_decimal(numerator)
				self._numerator = value._numerator
				self._denominator = value._denominator
				return self

			elif isinstance(numerator, basestring):
				# Handle construction from strings.
				m = _RATIONAL_FORMAT.match(numerator)
				if m is None:
					raise ValueError('Invalid literal for Fraction: %r' %
									 numerator)
				numerator = int(m.group('num') or '0')
				denom = m.group('denom')
				if denom:
					denominator = int(denom)
				else:
					denominator = 1
					decimal = m.group('decimal')
					if decimal:
						scale = 10**len(decimal)
						numerator = numerator * scale + int(decimal)
						denominator *= scale
					exp = m.group('exp')
					if exp:
						exp = int(exp)
						if exp >= 0:
							numerator *= 10**exp
						else:
							denominator *= 10**-exp
				if m.group('sign') == '-':
					numerator = -numerator

			else:
				raise TypeError("argument should be a string "
								"or a Rational instance")

		elif (isinstance(numerator, Rational) and
			isinstance(denominator, Rational)):
			numerator, denominator = (
				numerator.numerator * denominator.denominator,
				denominator.numerator * numerator.denominator
				)
		else:
			raise TypeError("both arguments should be "
							"Rational instances")

		#if denominator == 0:
		#	raise ZeroDivisionError('Fraction(%s, 0)' % numerator)
		self._numerator = numerator
		self._denominator = denominator
		return self

	def __or__(a, b):
		return NonreducedFraction(
			a._numerator + b._numerator, 
			a._denominator + b._denominator
		)