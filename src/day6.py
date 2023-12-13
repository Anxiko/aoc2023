import itertools
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from framework.day_solver import DaySolver


@dataclass
class Race:
	time: int
	distance: int

	@classmethod
	def from_tuple(cls, t: tuple[int, int]) -> Self:
		(time, distance) = t
		return cls(time, distance)


@dataclass
class Day6Input:
	races: list[Race]


def parse_values(line: str) -> list[int]:
	_label, values = line.split(":")
	return list(map(int, values.strip().split()))


def solve_quadratic(race: Race) -> tuple[float, float]:
	discriminant: float = race.time ** 2 - 4 * race.distance
	if discriminant < 0:
		raise ValueError("Race has no real solutions")
	sqrt_discriminant = math.sqrt(discriminant)

	return (-race.time + sqrt_discriminant) / (-2), (-race.time - sqrt_discriminant) / (-2)


def count_reals_between(min_charge: float, max_charge: float) -> int:
	if min_charge > max_charge:
		raise ValueError("Expected left <= right")

	int_min: int = math.ceil(min_charge)
	if int_min == min_charge:
		int_min += 1

	int_max: int = math.floor(max_charge)
	if int_max == max_charge:
		int_max -= 1

	return max(1 + int_max - int_min, 0)


def combine_digits(values: list[int]) -> int:
	return int("".join(map(str, values)))


def combine_races(races: list[Race]) -> Race:
	time_values: list[int] = [r.time for r in races]
	distance_values: list[int] = [r.distance for r in races]

	return Race(combine_digits(time_values), combine_digits(distance_values))


class Day6(DaySolver[Day6Input, int]):
	def __init__(self):
		super().__init__(6)

	def _solve_part1(self, part_input: Day6Input) -> int:
		quadratic_solutions: list[tuple[float, float]] = list(map(solve_quadratic, part_input.races))
		solution_counts: list[int] = list(map(lambda s: count_reals_between(s[0], s[1]), quadratic_solutions))
		return math.prod(solution_counts)

	def _solve_part2(self, part_input: Day6Input) -> int:
		combined_race: Race = combine_races(part_input.races)
		min_charge, max_charge = solve_quadratic(combined_race)
		return count_reals_between(min_charge, max_charge)

	def _parse_input(self, path: Path) -> Day6Input:
		with open(path) as f:
			[time_series, distance_series] = list(map(parse_values, f.readlines()))
			if len(time_series) != len(distance_series):
				raise ValueError("Mismatch between amount of values in time and distance series")

			races: list[Race] = list(map(Race.from_tuple, zip(time_series, distance_series)))
			return Day6Input(races)


if __name__ == '__main__':
	Day6().solve()
