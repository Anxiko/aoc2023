import enum
import re
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from math import prod
from typing import Self, Iterable

from shared.files import INPUT_PATH

GAME_REGEX: re.Pattern = re.compile(r"Game (?P<game_id>\d+): (?P<draws>.*)")


class Color(enum.StrEnum):
	Red = "red"
	Green = "green"
	Blue = "blue"


type Draw = Counter[Color]

LIMITS_DRAW_1: Draw = Counter({Color.Red: 12, Color.Green: 13, Color.Blue: 14})


def parse_pair(raw_pair: str) -> tuple[Color, int]:
	raw_count, raw_color = raw_pair.split()
	return Color(raw_color), int(raw_count)


def parse_draw(raw_draw: str) -> Draw:
	pairs: Iterable[tuple[Color, int]] = map(parse_pair, raw_draw.split(","))

	draw: Draw = Counter()

	for color, count in pairs:
		draw[color] += count

	return draw


def draw_le(left: Draw, right: Draw) -> bool:
	return left <= right


def max_draw(left: Draw, right: Draw) -> Draw:
	return left | right


@dataclass
class Game:
	game_id: int
	draws: list[Draw]

	def __init__(self, game_id: int, draws: list[Draw]):
		self.game_id = game_id
		self.draws = draws

	@classmethod
	def from_line(cls, line: str) -> Self:
		match: re.Match = GAME_REGEX.match(line)

		game_id: int = int(match["game_id"])
		draws = list(map(parse_draw, match["draws"].split(";")))

		return cls(game_id, draws)

	def is_possible(self, limit: Draw) -> bool:
		return draw_le(self.min_blocks(), limit)

	def get_id(self) -> int:
		return self.game_id

	def min_blocks(self) -> Draw:
		return reduce(max_draw, self.draws, Counter())

	def power(self) -> int:
		min_blocks: Draw = self.min_blocks()
		if len(min_blocks) < len(Color):
			return 0
		return prod(min_blocks.values())


def part1(games: list[Game]) -> int:
	return sum(map(Game.get_id, filter(lambda g: g.is_possible(LIMITS_DRAW_1), games)))


def part2(games: list[Game]) -> int:
	return sum(map(Game.power, games))


def main() -> None:
	with open(INPUT_PATH / "day2" / "part1.txt") as file_part1:
		games: list[Game] = list(map(Game.from_line, file_part1.readlines()))

		part1_solution: int = part1(games)
		print(f"Part 1: {part1_solution}")

		part2_solution: int = part2(games)
		print(f"Part 2: {part2_solution}")


if __name__ == '__main__':
	main()
