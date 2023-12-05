import itertools
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
	number: int
	digit_count: int
	position: Coord

	def __init__(self, digit: int, position: Coord):
		self.number = digit
		self.position = position
		self.digit_count = 1

	def add_digit(self, digit: int) -> None:
		self.number = 10 * self.number + digit
		self.digit_count += 1

	def neighbour_coords(self) -> Iterable[Coord]:
		return map(Coord.from_tuple, itertools.product(
			range(self.position.x - 1, self.position.x + self.digit_count + 1),
			range(self.position.y - 1, self.position.y + 2)
		))


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
	symbol_positions: set[Coord]


_SYMBOLS: set[str] = {""}


class Day3(DaySolver):
	def __init__(self):
		super().__init__(3)

	def _solve_part1(self, part_input: Day3Input) -> int:
		return sum(
			number_row.number for number_row in part_input.number_rows
			if any(n in part_input.symbol_positions for n in number_row.neighbour_coords())
		)

	def _solve_part2(self, part_input: Day3Input) -> int:
		return 0

	def _parse_input(self, path: Path) -> Day3Input:
		numbers: list[NumberRow] = []
		symbol_positions: set[Coord] = set()

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
							symbol_positions.add(coord)
				numbers.extend(row_builder.get_numbers())

		return Day3Input(numbers, symbol_positions)


if __name__ == '__main__':
	Day3().solve()
