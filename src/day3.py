import itertools
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Self

from framework.day_solver import DaySolver


@dataclass(frozen=True)
class Coord:
	x: int
	y: int

	@classmethod
	def from_tuple(cls, t: tuple[int, int]) -> Self:
		x, y = t
		return cls(x, y)


class NumberRow:
	value: int
	digit_count: int
	position: Coord

	def __init__(self, digit: int, position: Coord):
		self.value = digit
		self.position = position
		self.digit_count = 1

	def add_digit(self, digit: int) -> None:
		self.value = 10 * self.value + digit
		self.digit_count += 1

	def neighbour_coords(self) -> Iterable[Coord]:
		return map(Coord.from_tuple, itertools.product(
			range(self.position.x - 1, self.position.x + self.digit_count + 1),
			range(self.position.y - 1, self.position.y + 2)
		))

	def is_neighbour_to(self, neighbour: Coord) -> bool:
		return neighbour in self.neighbour_coords()


class NumberRowsBuilder:
	number_rows: list[NumberRow]
	current_number: NumberRow | None

	def __init__(self):
		self.number_rows = []
		self.current_number = None

	def finish_current_number(self) -> None:
		if self.current_number is not None:
			self.number_rows.append(self.current_number)
			self.current_number = None

	def get_numbers(self) -> list[NumberRow]:
		self.finish_current_number()
		return self.number_rows

	def add_digit(self, digit: int, coord: Coord) -> None:
		if self.current_number is None:
			self.current_number = NumberRow(digit, coord)
		else:
			self.current_number.add_digit(digit)


@dataclass
class Day3Input:
	number_rows: list[NumberRow]
	symbols: dict[Coord, str]


_GEAR_NEIGHBOURS: int = 2


class Day3(DaySolver):
	def __init__(self):
		super().__init__(3)

	def _solve_part1(self, part_input: Day3Input) -> int:
		return sum(
			number_row.value for number_row in part_input.number_rows
			if any(n in part_input.symbols for n in number_row.neighbour_coords())
		)

	def _solve_part2(self, part_input: Day3Input) -> int:
		gear_positions: Iterable[Coord] = (pos for pos, char in part_input.symbols.items() if char == "*")
		return sum(
			filter(
				lambda pos: pos is not None,
				map(lambda pos: _maybe_gear_ratio(part_input, pos), gear_positions)
			)
		)

	def _parse_input(self, path: Path) -> Day3Input:
		numbers: list[NumberRow] = []
		symbols: dict[Coord, str] = {}

		with open(path) as f:
			row: int
			column: int
			line: str
			character: str

			for row, line in enumerate(f.readlines()):
				row_builder: NumberRowsBuilder = NumberRowsBuilder()
				for column, character in enumerate(line.rstrip("\n")):
					coord: Coord = Coord(column, row)

					if character.isdigit():
						digit: int = int(character)
						row_builder.add_digit(digit, coord)
					else:
						row_builder.finish_current_number()

						if character != ".":
							symbols[coord] = character
				numbers.extend(row_builder.get_numbers())

		return Day3Input(numbers, symbols)


def _maybe_gear_ratio(part_input: Day3Input, position: Coord) -> int | None:
	neighbour_numbers: list[int] = []
	for number in part_input.number_rows:
		if number.is_neighbour_to(position):
			neighbour_numbers.append(number.value)
			if len(neighbour_numbers) > _GEAR_NEIGHBOURS:
				break

	if len(neighbour_numbers) == _GEAR_NEIGHBOURS:
		return math.prod(neighbour_numbers)
	return None


if __name__ == '__main__':
	Day3().solve()
