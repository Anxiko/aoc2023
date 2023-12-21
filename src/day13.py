import enum
import functools
from pathlib import Path
from typing import Iterable

from framework.day_solver import DaySolver
from shared.extra_itertools import chunk_on
from shared.grid import Grid


class Tile(enum.StrEnum):
	Ash = '.'
	Rock = '#'

	def __str__(self) -> str:
		return self.value


def mirrored_iterator(lines: list[list[Tile]], idx: int) -> Iterable[tuple[list[Tile], list[Tile]]]:
	return zip(lines[idx::-1], lines[idx + 1:])


def line_difference(left: list[Tile], right: list[Tile]) -> int:
	return sum(1 if left_tile != right_tile else 0 for left_tile, right_tile in zip(left, right))


def is_mirrored_image(
	mirror_iter: Iterable[tuple[list[Tile], list[Tile]]], expected_errors: int
) -> bool:
	detected_errors: int = 0
	for left, right in mirror_iter:
		detected_errors += line_difference(left, right)
		if detected_errors > expected_errors:
			return False

	return detected_errors == expected_errors


type Day13Input = list[Grid[Tile]]


def score_for_grid(grid: Grid[Tile], expected_errors: int = 0) -> int | None:
	rows: list[Grid.Line] = list(grid.rows)

	for row_idx in range(grid.height - 1):
		if is_mirrored_image(mirrored_iterator(rows, row_idx), expected_errors):
			return (row_idx + 1) * 100

	columns: list[Grid.Line] = list(grid.columns)

	for column_idx in range(grid.width - 1):
		if is_mirrored_image(mirrored_iterator(columns, column_idx), expected_errors):
			return column_idx + 1


class Day13(DaySolver[Day13Input, int]):
	def __init__(self):
		super().__init__(13)

	def _solve_part1(self, part_input: Day13Input) -> int:
		return sum(map(score_for_grid, part_input))

	def _solve_part2(self, part_input: Day13Input) -> int:
		return sum(map(
			functools.partial(score_for_grid, expected_errors=1),
			part_input
		))

	def _parse_input(self, path: Path) -> Day13Input:
		with open(path) as f:
			lines: list[str] = list(map(str.strip, f.readlines()))
			return list(map(
				functools.partial(Grid.from_raw_lines, tile_parser=Tile),
				chunk_on(lines, lambda s: len(s) == 0)
			))


if __name__ == '__main__':
	Day13().solve()
