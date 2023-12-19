import functools
import itertools
import operator
from dataclasses import dataclass
from typing import Self, Iterable

from day3 import Coord


@dataclass(frozen=True)
class Coord:
	x: int
	y: int

	def __add__(self, other: Self) -> Self:
		return Coord(self.x + other.x, self.y + other.y)

	def __bool__(self) -> bool:
		return self.x != 0 or self.y != 0

	@classmethod
	def from_tuple(cls, t: tuple[int, int]) -> Self:
		x, y = t
		return cls(x, y)

	def neighbours(self) -> Iterable[Self]:
		return filter(
			None,
			map(
				functools.partial(operator.add, self),
				map(
					Coord.from_tuple,
					itertools.product(range(-1, 2), range(-1, 2))
				)
			)
		)

	def manhattan(self) -> int:
		return abs(self.x) + abs(self.y)
