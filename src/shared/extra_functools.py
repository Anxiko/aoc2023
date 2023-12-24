from typing import Callable, Any


def negated[X](f: Callable[[X], bool]) -> Callable[[X], bool]:
	def f_negated(x: X) -> bool:
		return not (f(x))

	return f_negated


def is_not_none(x: Any) -> bool:
	return x is not None
