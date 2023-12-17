import itertools
from dataclasses import dataclass
from pathlib import Path

from framework.day_solver import DaySolver

type Series = list[int]


@dataclass
class Day9Input:
	series_list: list[Series]


def parse_series(line: str) -> Series:
	return list(map(int, line.split()))


def tuple_difference(t: tuple[int, int]) -> int:
	t0, t1 = t
	return t1 - t0


def extrapolate(s: Series) -> Series:
	return list(map(tuple_difference, itertools.pairwise(s)))


def is_final_series(s: Series) -> bool:
	return all(v == 0 for v in s)


def series_extension(s: Series) -> tuple[int, int]:
	if is_final_series(s):
		return 0, 0

	previous_delta, next_delta = series_extension(extrapolate(s))
	return s[0] - previous_delta, s[-1] + next_delta


def select_next_value(t: tuple[int, int]) -> int:
	return t[1]


def select_previous_value(t: tuple[int, int]) -> int:
	return t[0]


class Day9(DaySolver[Series, int]):
	def __init__(self) -> None:
		super().__init__(9)

	def _solve_part1(self, part_input: Day9Input) -> int:
		return sum(map(select_next_value, map(series_extension, part_input.series_list)))

	def _solve_part2(self, part_input: Day9Input) -> int:
		return sum(map(select_previous_value, map(series_extension, part_input.series_list)))

	def _parse_input(self, path: Path) -> Day9Input:
		with open(path) as f:
			return Day9Input(
				series_list=list(map(parse_series, f.readlines()))
			)


if __name__ == '__main__':
	Day9().solve()
