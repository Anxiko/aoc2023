from typing import Callable


def negated[X](f: Callable[[X], bool]) -> Callable[[X], bool]:
	def f_negated(x: X) -> bool:
		return not (f(x))

	return f_negated
