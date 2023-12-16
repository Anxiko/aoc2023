import functools
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping, Self

from framework.day_solver import DaySolver

type RawKind = Literal['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
type DecayedJoker = Literal['j']

SORTED_KINDS: list[RawKind] = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
KIND_TO_SCORE: Mapping[RawKind | DecayedJoker, int] = {
	kind: idx for (idx, kind) in enumerate(['j'] + SORTED_KINDS[::-1])
}
type HandKinds = tuple[SortableKind, SortableKind, SortableKind, SortableKind, SortableKind]


@functools.total_ordering
@dataclass(frozen=True)
class SortableKind:
	raw_kind: RawKind | Literal['j']

	def __post_init__(self):
		if self.raw_kind not in KIND_TO_SCORE:
			raise ValueError(f"Invalid kind: {self.raw_kind}")

	def __lt__(self, other: Self) -> bool:
		return KIND_TO_SCORE[self.raw_kind] < KIND_TO_SCORE[other.raw_kind]

	def __eq__(self, other: Self) -> bool:
		return self.raw_kind == other.raw_kind

	def joker_decay(self) -> Self:
		if self.raw_kind == 'J':
			return SortableKind('j')
		return self


@dataclass
class FiveOfAKind:
	kind: SortableKind


@dataclass
class FourOfAKind:
	kind: SortableKind


@dataclass
class FullHouse:
	triplet: SortableKind
	pair: SortableKind


@dataclass
class ThreeOfAKind:
	kind: SortableKind


@dataclass
class TwoPair:
	pairs: tuple[SortableKind, SortableKind]


@dataclass
class OnePair:
	pair: SortableKind


@dataclass
class HighCard:
	kind: SortableKind


type HandType = FiveOfAKind | FourOfAKind | FullHouse | ThreeOfAKind | TwoPair | OnePair | HighCard

SORTED_HAND_TYPES: list[type[HandType]] = [
	FiveOfAKind, FourOfAKind, FullHouse, ThreeOfAKind, TwoPair, OnePair, HighCard
]
HAND_TYPE_TO_SCORE: Mapping[type[HandType], int] = {type_: idx for (idx, type_) in enumerate(SORTED_HAND_TYPES[::-1])}


def reverse_tuple[X, Y](t: tuple[X, Y]) -> tuple[Y, X]:
	x, y = t
	return y, x


def hand_type_for_kinds(hand_kinds: HandKinds) -> HandType:
	counter: Counter[SortableKind] = Counter(hand_kinds)

	joker_count: int = counter.pop(SortableKind('j'), 0)

	tuple_counts: list[tuple[int, SortableKind]] = sorted(map(reverse_tuple, counter.items()), reverse=True)

	if joker_count > 0:
		if len(tuple_counts) == 0:
			tuple_counts.append((0, SortableKind('K')))  # Necessary for a full hand of jokers to become five of a kind
		most_repeated_count, most_repeated_kind = tuple_counts[0]
		tuple_counts[0] = (most_repeated_count + joker_count, most_repeated_kind)

	match tuple_counts:
		case [(5, kind)]:
			return FiveOfAKind(kind)
		case [(4, kind), _]:
			return FourOfAKind(kind)
		case [(3, triplet), (2, pair)]:
			return FullHouse(triplet, pair)
		case [(3, triplet), *_]:
			return ThreeOfAKind(triplet)
		case [(2, first_pair), (2, second_pair), _]:
			return TwoPair((first_pair, second_pair))
		case [(2, pair), *_]:
			return OnePair(pair)
		case _:
			highest_kind: SortableKind = max(hand_kinds)
			return HighCard(highest_kind)


@functools.total_ordering
@dataclass
class Hand:
	kinds: HandKinds
	type_: HandType

	def __lt__(self, other: Self) -> bool:
		self_type_score: int = HAND_TYPE_TO_SCORE[type(self.type_)]
		other_type_score: int = HAND_TYPE_TO_SCORE[type(other.type_)]

		if self_type_score == other_type_score:
			return self.kinds < other.kinds

		return self_type_score < other_type_score

	def __eq__(self, other: Self) -> bool:
		self_type_score: int = HAND_TYPE_TO_SCORE[type(self.type_)]
		other_type_score: int = HAND_TYPE_TO_SCORE[type(other.type_)]

		return self_type_score == other_type_score and self.kinds == other.kinds


type Round = tuple[Hand, int]
type RawRound = tuple[HandKinds, int]


def kind_list_to_hand_kinds(kind_list: list[SortableKind]) -> HandKinds:
	k1, k2, k3, k4, k5 = kind_list
	return k1, k2, k3, k4, k5


def parse_raw_round(line: str) -> RawRound:
	raw_kinds, raw_bet = line.split()

	kinds: HandKinds = kind_list_to_hand_kinds(list(map(SortableKind, raw_kinds)))

	bet: int = int(raw_bet)

	return kinds, bet


def calculate_round(raw_round: RawRound, use_joker: bool) -> Round:
	kinds, bet = raw_round
	if use_joker:
		kinds = kind_list_to_hand_kinds(list(map(SortableKind.joker_decay, kinds)))

	type_: HandType = hand_type_for_kinds(kinds)
	return Hand(kinds, type_), bet


def ranked_round_score(t: tuple[int, Round]) -> int:
	rank, (_, bet) = t
	return rank * bet


@dataclass
class Day7Input:
	raw_rounds: list[RawRound]


class Day7(DaySolver[Day7Input, int]):
	def __init__(self):
		super().__init__(7)

	def _solve_part1(self, part_input: Day7Input) -> int:
		rounds = list(map(functools.partial(calculate_round, use_joker=False), part_input.raw_rounds))
		sorted_rounds = sorted(rounds, key=lambda r: r[0])
		return sum(map(ranked_round_score, enumerate(sorted_rounds, start=1)))

	def _solve_part2(self, part_input: Day7Input) -> int:
		rounds = list(map(functools.partial(calculate_round, use_joker=True), part_input.raw_rounds))
		sorted_rounds = sorted(rounds, key=lambda r: r[0])
		return sum(map(ranked_round_score, enumerate(sorted_rounds, start=1)))

	def _parse_input(self, path: Path) -> Day7Input:
		with open(path) as f:
			hand_and_best_list: list[RawRound] = list(map(parse_raw_round, f.readlines()))
			return Day7Input(hand_and_best_list)


if __name__ == '__main__':
	Day7().solve()
