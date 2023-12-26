from typing import Callable, Any


def negate[X](f: Callable[[X], bool]) -> Callable[[X], bool]:
	def f_negated(x: X) -> bool:
		return not (f(x))

	return f_negated


def is_not_none(x: Any) -> bool:
	return x is not None


def lazify[X](value: X) -> Callable[[], X]:
	def lazified():
		return value

	return lazified()
