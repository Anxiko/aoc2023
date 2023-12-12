import re
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from framework.day_solver import DaySolver

_CARD_PATTERN: re.Pattern = re.compile(r"Card\s*\d+:(?P<winners>[^|]+)\|(?P<numbers>[^|]+)\n?")


@dataclass
class Card:
	winners: list[int]
	numbers: list[int]

	@staticmethod
	def parse_numbers(raw_numbers: str) -> list[int]:
		return list(map(int, raw_numbers.split()))

	@classmethod
	def from_line(cls, line: str) -> Self:
		match = _CARD_PATTERN.match(line)
		return cls(cls.parse_numbers(match["winners"]), cls.parse_numbers(match["numbers"]))

	def numbers_won(self) -> int:
		return len(set(self.winners) & set(self.numbers))


@dataclass
class Day4Input:
	cards: list[Card]


def _card_score(card: Card) -> int:
	count: int = card.numbers_won()
	if count > 0:
		return 2 ** (count - 1)
	return 0


class Day4(DaySolver[Day4Input, int]):
	def __init__(self):
		super().__init__(4)

	def _solve_part1(self, part_input: Day4Input) -> int:
		return sum(map(
			_card_score,
			part_input.cards
		))

	def _solve_part2(self, part_input: Day4Input) -> int:
		card_owned: list[int] = [1 for _ in part_input.cards]

		for idx, card in enumerate(part_input.cards):
			amount_of_card: int = card_owned[idx]

			won_count: int = card.numbers_won()
			for extra_card_idx in range(idx + 1, idx + 1 + won_count):
				card_owned[extra_card_idx] += amount_of_card

		return sum(card_owned)

	def _parse_input(self, path: Path) -> Day4Input:
		with open(path) as f:
			cards = list(map(Card.from_line, f.readlines()))
			return Day4Input(cards)


if __name__ == '__main__':
	Day4().solve()
