import enum
import functools
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Mapping, Iterable

from framework.day_solver import DaySolver
from shared.coord import Direction, Coord
from shared.grid import Grid

INSTRUCTION_PATTERN: re.Pattern = re.compile(
	r"(?P<direction>[UDLR]) (?P<length>\d+) \(#(?P<tag>[0-9a-f]{6})\)"
)


@dataclass
class Instruction:
	direction: Direction
	length: int

	def as_delta(self) -> Coord:
		return self.direction.to_delta() * self.length


@dataclass
class FakeColor:
	length: int
	direction: Direction

	@classmethod
	def parse_direction(cls, raw_direction: int) -> Direction:
		return Direction.from_angle(4 - raw_direction)

	@classmethod
	def from_hex(cls, raw_hex: str) -> Self:
		return cls(
			int(raw_hex[:5], 16),
			cls.parse_direction(int(raw_hex[5:], 16))
		)

	def as_instruction(self) -> Instruction:
		return Instruction(self.direction, self.length)


_DIRECTION_MAPPING: Mapping[str, Direction] = {
	'U': Direction.North,
	'D': Direction.South,
	'L': Direction.West,
	'R': Direction.East
}


@dataclass
class InputLine:
	direction: Direction
	length: int
	color: FakeColor

	def stroke_coords(self, pen: Coord) -> tuple[Iterable[Coord], Coord]:
		delta: Coord = self.direction.to_delta()
		return (pen + delta * dist for dist in range(self.length)), pen + delta * self.length

	def as_regular_instruction(self) -> Instruction:
		return Instruction(self.direction, self.length)

	def as_fake_color_instruction(self) -> Instruction:
		return self.color.as_instruction()

	@classmethod
	def from_line(cls, line: str) -> Self:
		if (match := INSTRUCTION_PATTERN.match(line)) is None:
			raise ValueError(f"Invalid instruction line: {line!r}")
		return cls(
			_DIRECTION_MAPPING[match["direction"]],
			int(match["length"]),
			FakeColor.from_hex(match["tag"])
		)


type Day18Input = list[InputLine]


@dataclass
class Polygon:
	points: list[Coord]
	perimeter: int


def instructions_to_polygon(instructions: list[Instruction]) -> Polygon:
	points: list[Coord] = [Coord.at_origin()]
	perimeter: int = 0

	for instruction in instructions:
		perimeter += instruction.length
		next_coord: Coord = points[-1] + instruction.as_delta()
		points.append(next_coord)

	return Polygon(points, perimeter)


def shoelace_formula(polygon: Polygon) -> int:
	def get_point(idx: int) -> Coord:
		if idx > 0:
			idx %= len(polygon.points)

		return polygon.points[idx]

	return sum(
		point.x * (get_point(idx + 1).y - get_point(idx - 1).y) for idx, point in enumerate(polygon.points)
	) // 2


def polygon_area(polygon: Polygon) -> int:
	area: int = shoelace_formula(polygon)
	points_inside: int = area - polygon.perimeter // 2 + 1
	return points_inside + polygon.perimeter


class Day18(DaySolver[Day18Input, int]):
	def __init__(self):
		super().__init__(18)

	def _solve_part1(self, part_input: Day18Input) -> int:
		instructions: list[Instruction] = [line.as_regular_instruction() for line in part_input]
		polygon: Polygon = instructions_to_polygon(instructions)
		return polygon_area(polygon)

	def _solve_part2(self, part_input: Day18Input) -> int:
		instructions: list[Instruction] = [line.as_fake_color_instruction() for line in part_input]
		polygon: Polygon = instructions_to_polygon(instructions)
		return polygon_area(polygon)

	def _parse_input(self, path: Path) -> Day18Input:
		with open(path) as f:
			return [InputLine.from_line(line.strip()) for line in f.readlines()]


if __name__ == "__main__":
	Day18().solve()
