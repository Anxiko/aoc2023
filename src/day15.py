import functools
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from framework.day_solver import DaySolver

N_BOXES: int = 256

OPERATION_PATTERN: re.Pattern = re.compile(
	r"(?P<tag>\w+)(?P<operation>[-=])(?P<focal_length>\d*)"
)


def add_char_to_hash(hash_value: int, char: str) -> int:
	return ((hash_value + ord(char)) * 17) % N_BOXES


def hash_str(s: str) -> int:
	return functools.reduce(add_char_to_hash, s, 0)


type Day15Input = list[str]


@dataclass
class Lens:
	tag: str
	focal_length: int


class LensBox:
	lenses: list[Lens]

	def __init__(self):
		self.lenses = []

	def add_lens(self, lens: Lens):
		if (idx := self._find_tag(lens.tag)) is not None:
			self.lenses[idx] = lens
		else:
			self.lenses.append(lens)

	def remove_tag(self, tag: str) -> None:
		if (idx := self._find_tag(tag)) is not None:
			self.lenses.pop(idx)

	def _find_tag(self, tag: str) -> int | None:
		for (idx, lens) in enumerate(self.lenses):
			if lens.tag == tag:
				return idx
		return None

	def focusing_power(self) -> int:
		return sum(idx * lens.focal_length for idx, lens in enumerate(self.lenses, start=1))


@dataclass
class AddLensOperation:
	lens: Lens
	box_number: int

	@classmethod
	def from_parsed_operation(cls, tag: str, focal_length: int) -> Self:
		return cls(Lens(tag, focal_length), hash_str(tag))


@dataclass
class RemoveTagOperation:
	tag: str
	box_number: int

	@classmethod
	def from_parse_operation(cls, tag: str) -> Self:
		return cls(tag, hash_str(tag))


type LensOperation = AddLensOperation | RemoveTagOperation


def parse_operation(raw_operation: str) -> LensOperation:
	if (op := OPERATION_PATTERN.match(raw_operation)) is not None:
		match op.groupdict():
			case {'tag': tag, 'operation': '=', 'focal_length': focal_length} if len(focal_length) > 0:
				return AddLensOperation.from_parsed_operation(tag, int(focal_length))
			case {'tag': tag, 'operation': '-', 'focal_length': ''}:
				return RemoveTagOperation.from_parse_operation(tag)
			case _:
				raise ValueError(f"Invalid parsed operation: {op}")
	raise ValueError(f"Invalid operation: {raw_operation}")


class BoxStack:
	boxes: list[LensBox]

	def __init__(self):
		self.boxes = [LensBox() for _ in range(N_BOXES)]

	def focusing_power(self) -> int:
		return sum(
			idx * box.focusing_power()
			for idx, box in enumerate(self.boxes, start=1)
		)

	def add_lens(self, lens: Lens, box_number: int) -> None:
		self.boxes[box_number].add_lens(lens)

	def remove_tag(self, tag: str, box_number: int) -> None:
		self.boxes[box_number].remove_tag(tag)


def handle_operation(box_stack: BoxStack, op: LensOperation) -> BoxStack:
	match op:
		case AddLensOperation(lens=lens, box_number=box_number):
			box_stack.add_lens(lens, box_number)
		case RemoveTagOperation(tag=tag, box_number=box_number):
			box_stack.remove_tag(tag=tag, box_number=box_number)
		case _:
			raise ValueError(f"Invalid operation: {op}")

	return box_stack


class Day15(DaySolver[Day15Input, int]):
	def __init__(self):
		super().__init__(15)

	def _solve_part1(self, part_input: Day15Input) -> int:
		return sum(map(hash_str, part_input))

	def _solve_part2(self, part_input: Day15Input) -> int:
		operations: list[LensOperation] = list(map(parse_operation, part_input))

		box_stack: BoxStack = functools.reduce(
			handle_operation,
			operations,
			BoxStack()
		)

		return box_stack.focusing_power()

	def _parse_input(self, path: Path) -> Day15Input:
		with open(path) as f:
			line: str
			[line] = list(map(str.strip, f.readlines()))
			return line.split(',')


if __name__ == '__main__':
	Day15().solve()
