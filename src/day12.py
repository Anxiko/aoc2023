import enum
import functools
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Iterable, Callable

from tqdm import tqdm

from framework.day_solver import DaySolver


def repeat_iterable[X](iterable: Iterable[X], n: int) -> Iterable[X]:
	return itertools.chain.from_iterable(itertools.repeat(iterable, n))


def join_with[X](separator: X) -> Callable[[list[X], list[X]], list[X]]:
	def joiner(left: list[X], right: list[X]) -> list[X]:
		return left + [separator] + right

	return joiner


class Tile(enum.StrEnum):
	Working = '.'
	Broken = '#'
	Unknown = '?'

	def __str__(self) -> str:
		return self.value


@dataclass
class Line:
	tiles: list[Tile]
	groups: list[int]

	@classmethod
	def from_raw_line(cls, raw_line: str) -> Self:
		raw_tiles, raw_groups = raw_line.split(' ')
		tiles = list(map(Tile, raw_tiles))
		groups = list(map(int, raw_groups.split(',')))

		return cls(tiles, groups)

	def __str__(self) -> str:
		tiles: str = "".join(map(str, self.tiles))
		groups: str = ",".join(map(str, self.groups))

		return f"<Line: {tiles} => {groups}>"

	def unfold(self, factor: int) -> Self:
		tiles: list[Tile] = list(functools.reduce(
			join_with(Tile.Unknown),
			itertools.repeat(self.tiles, factor)
		))
		groups: list[int] = list(repeat_iterable(self.groups, factor))

		return Line(tiles, groups)


@dataclass
class Day12Input:
	lines: list[Line]


def solutions_for_line(line: Line) -> int:
	return _line_solutions(tuple(line.tiles), tuple(line.groups), 0)


@functools.cache
def _line_solutions(tiles: tuple[Tile, ...], groups: tuple[int, ...], buffer: int) -> int:
	match (tiles, groups, buffer):
		case (), (), 0:
			return 1
		case (), (group, ), buffer if group == buffer:
			return 1
		case (), _, _:
			return 0

		case (Tile.Working, *t_tiles), groups, 0:
			return _line_solutions(tuple(t_tiles), groups, 0)
		case [Tile.Working | Tile.Unknown, *t_tiles], (), 0:
			return _line_solutions(tuple(t_tiles), (), 0)
		case [Tile.Working | Tile.Unknown, *t_tiles], (group, *t_groups), buffer if group == buffer:
			return _line_solutions(tuple(t_tiles), tuple(t_groups), 0)
		case [Tile.Working, *_tiles], *_groups, _buffer:
			return 0

		case (Tile.Broken, *t_tiles), (group, *_) as groups, buffer if buffer < group:
			return _line_solutions(tuple(t_tiles), tuple(groups), buffer + 1)
		case [Tile.Broken, *_tiles], _groups, _buffer:
			return 0

		case (Tile.Unknown, *t_tiles), (_, *_) as groups, 0:
			t_tiles = tuple(t_tiles)
			solutions_for_working: int = _line_solutions(t_tiles, groups, 0)
			solutions_for_broken: int = _line_solutions(t_tiles, groups, 1)
			return solutions_for_working + solutions_for_broken
		case (Tile.Unknown, *t_tiles), (group, *_) as groups, buffer if buffer < group:
			return _line_solutions(tuple(t_tiles), groups, buffer + 1)
		case (Tile.Unknown, *_), _groups, _buffer:
			return 0

		case tiles, groups, buffer:
			raise ValueError(f"Unhandled case: {tiles=}, groups={groups=}, buffer={buffer}")


class Day12(DaySolver[Day12Input, int]):
	def __init__(self):
		super().__init__(12)

	def _solve_part1(self, part_input: Day12Input) -> int:
		solutions_list: list[int] = []

		for line in part_input.lines:
			solutions: int = solutions_for_line(line)
			# print(f"{line} => {solutions}")
			solutions_list.append(solutions)

		return sum(solutions_list)

	def _solve_part2(self, part_input: Day12Input) -> int:
		solutions_list: list[int] = []
		unfolded_lines: list[Line] = list(map(functools.partial(Line.unfold, factor=5), part_input.lines))

		for line in unfolded_lines:
			solutions: int = solutions_for_line(line)
			# print(f"{line} => {solutions}")
			solutions_list.append(solutions)

		return sum(solutions_list)

	def _parse_input(self, path: Path) -> Day12Input:
		with open(path) as f:
			return Day12Input(list(map(Line.from_raw_line, map(str.strip, f.readlines()))))


if __name__ == "__main__":
	Day12().solve()
