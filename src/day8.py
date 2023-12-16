import functools
import itertools
import math
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from re import Pattern
from typing import Mapping, Iterable, Callable

from framework.day_solver import DaySolver

type Node = str
type MapEntry = tuple[Node, [Node, Node]]

START_NODE: Node = "AAA"
END_NODE: Node = "ZZZ"

ENTRY_PATTERN: Pattern = re.compile(r"^(?P<src>\w+) = \((?P<left>\w+), (?P<right>\w+)\)$")


def parse_entry(entry: str) -> MapEntry:
	match: re.Match = ENTRY_PATTERN.match(entry)
	return match["src"], (match["left"], match["right"])


class Direction(StrEnum):
	Left = 'L'
	Right = 'R'

	def next_node(self, left_right: tuple[Node, Node]) -> Node:
		left, right = left_right
		match self:
			case Direction.Left:
				return left
			case Direction.Right:
				return right


def step_node(node: Node, direction: Direction, mapping: Mapping[Node, tuple[Node, Node]]) -> Node:
	return direction.next_node(mapping[node])


def path_length(
	node: Node, path: list[Direction], mapping: Mapping[Node, tuple[Node, Node]], is_end: Callable[[Node], bool]
) -> int:
	steps: int = 0

	for d in itertools.cycle(path):
		if is_end(node):
			return steps
		bifurcation: tuple[Node, Node] = mapping[node]
		node = d.next_node(bifurcation)
		steps += 1


def is_singular_end_node(node: Node) -> bool:
	return node == END_NODE


def is_shared_end_node(node: Node) -> bool:
	return node.endswith("Z")


def is_shared_start_node(node: Node) -> bool:
	return node.endswith("A")


def path_length_for_nodes(
	nodes: list[Node], path: Iterable[Direction], mapping: Mapping[Node, tuple[Node, Node]]
) -> int:
	steps: int = 0
	for d in itertools.cycle(path):
		if all(map(is_shared_end_node, nodes)):
			return steps

		nodes = list(map(functools.partial(step_node, direction=d, mapping=mapping), nodes))
		steps += 1


@dataclass
class Day8Input:
	path: list[Direction]
	map_entries: list[MapEntry]


class Day8(DaySolver[Day8Input, int]):
	def __init__(self):
		super().__init__(8)

	def _solve_part1(self, part_input: Day8Input) -> int:
		mapping: Mapping[Node, tuple[Node, Node]] = {
			k: v for (k, v) in part_input.map_entries
		}
		return path_length(START_NODE, part_input.path, mapping, is_singular_end_node)

	def _solve_part2(self, part_input: Day8Input) -> int:
		mapping: Mapping[Node, tuple[Node, Node]] = {
			k: v for (k, v) in part_input.map_entries
		}
		start_nodes: list[Node] = list(filter(is_shared_start_node, mapping.keys()))
		path_lengths: list[int] = list(map(
			functools.partial(path_length, path=part_input.path, mapping=mapping, is_end=is_shared_end_node),
			start_nodes
		))

		return math.lcm(*path_lengths)

	def _parse_input(self, path: Path) -> Day8Input:
		with open(path) as f:
			lines: list[str] = list(filter(len, map(str.strip, f.readlines())))
			path: list[Direction] = list(map(Direction, lines[0]))
			map_entries: list[MapEntry] = list(map(parse_entry, lines[1:]))
			return Day8Input(path, map_entries)


if __name__ == '__main__':
	Day8().solve()
