import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Self

from framework.day_solver import DaySolver
from shared.coord import Coord

type Tile = bool
type Line = list[Tile]


def line_is_empty(line: Line) -> bool:
	return not any(line)


def parse_line(raw_line: str) -> Line:
	return [c == '#' for c in raw_line]


class Grid:
	_rows: list[Line]

	def __init__(self, rows: list[Line]):
		self._rows = rows

	@property
	def width(self) -> int:
		match self._rows:
			case []:
				return 0
			case [row, *_]:
				return len(row)

	@property
	def height(self) -> int:
		return len(self._rows)

	@property
	def rows(self) -> Iterable[Line]:
		return self._rows

	def _get_column(self, column: int) -> Line:
		return [row[column] for row in self._rows]

	@property
	def columns(self) -> Iterable[Line]:
		return map(self._get_column, range(self.width))

	def __getitem__(self, coord: Coord) -> Tile:
		return self._rows[coord.y][coord.x]


@dataclass
class Day11Input:
	grid: Grid
	empty_rows: set[int]
	empty_columns: set[int]
	galaxies: set[tuple[Coord]]

	@classmethod
	def from_grid(cls, grid: Grid) -> Self:
		empty_rows = set(idx for idx, row in enumerate(grid.rows) if line_is_empty(row))
		empty_columns = set(idx for idx, column in enumerate(grid.columns) if line_is_empty(column))

		galaxies = set(filter(
			grid.__getitem__,
			map(Coord.from_tuple, itertools.product(range(grid.width), range(grid.height)))
		))

		return cls(grid, empty_rows, empty_columns, galaxies)

	@staticmethod
	def _distance_in_axis(src: int, dst: int, empty_values: set[int], distance_for_empty: int) -> int:
		def value_for_pos(pos: int) -> int:
			return distance_for_empty if pos in empty_values else 1

		return sum(map(value_for_pos, range(dst, src, 1 if src >= dst else -1)))

	def galaxy_distance(self, src: Coord, dst: Coord, distance_for_empty: int = 2) -> int:
		return (
			self._distance_in_axis(src.x, dst.x, self.empty_columns, distance_for_empty)
			+ self._distance_in_axis(src.y, dst.y, self.empty_rows, distance_for_empty)
		)


class Day11(DaySolver[Day11Input, int]):
	def __init__(self):
		super().__init__(11)

	def _solve_part1(self, part_input: Day11Input) -> int:
		return sum(
			part_input.galaxy_distance(src, dst)
			for src, dst in itertools.combinations(part_input.galaxies, 2)
		)

	def _solve_part2(self, part_input: Day11Input) -> int:
		return sum(
			part_input.galaxy_distance(src, dst, 1_000_000)
			for src, dst in itertools.combinations(part_input.galaxies, 2)
		)

	def _parse_input(self, path: Path) -> Day11Input:
		with open(path) as f:
			grid: Grid = Grid(list(map(parse_line, map(str.strip, f.readlines()))))
			return Day11Input.from_grid(grid)


if __name__ == '__main__':
	Day11().solve()
