import enum
import functools
import itertools
import operator
from dataclasses import dataclass
from typing import Self, Iterable, Mapping

from day3 import Coord


@dataclass(frozen=True)
class Coord:
	x: int
	y: int

	@classmethod
	def at_origin(cls) -> Self:
		return cls(0, 0)

	def __add__(self, other: Self) -> Self:
		return Coord(self.x + other.x, self.y + other.y)

	def __sub__(self, other: Self) -> Self:
		return Coord(self.x - other.x, self.y - other.y)

	def __mul__(self, other: int) -> Self:
		return Coord(self.x * other, self.y * other)

	def __neg__(self) -> Coord:
		return Coord(-self.x, -self.y)

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


class Direction(enum.IntEnum):
	East = 0
	North = 1
	West = 2
	South = 3

	@classmethod
	def from_angle(cls, angle: int) -> Self:
		return cls(angle % 4)

	def to_delta(self) -> Coord:
		return _DIRECTION_TO_COORD[self]

	def rotate(self, rotation: int) -> Self:
		return Direction((self.value + rotation) % 4)

	@property
	def is_vertical(self) -> bool:
		return self in {Direction.North, Direction.South}

	@property
	def is_horizontal(self) -> bool:
		return self in {Direction.East, Direction.West}

	def __neg__(self) -> Self:
		return self.rotate(2)


_DIRECTION_TO_COORD: Mapping[Direction, Coord] = {
	Direction.North: Coord(0, -1),
	Direction.South: Coord(0, 1),
	Direction.West: Coord(-1, 0),
	Direction.East: Coord(1, 0)
}
