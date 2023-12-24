import functools
import heapq
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Hashable

from framework.day_solver import DaySolver
from shared.coord import Coord, Direction
from shared.extra_functools import is_not_none
from shared.grid import Grid as GenericGrid

type Grid = GenericGrid[int]

_MAX_REGULAR_STRAIGHT_LINE: int = 3

_MIN_ULTRA_STRAIGHT_LINE: int = 4
_MAX_ULTRA_STRAIGHT_LINE: int = 10


@functools.total_ordering
@dataclass
class State:
	pos: Coord
	_end_pos: Coord
	cost: int
	last_direction: Direction | None
	repeated_last_direction: int
	_ultra_crucible: bool

	@classmethod
	def initial(cls, grid: Grid, ultra_crucible: bool) -> Self:
		return cls(Coord.at_origin(), Coord(grid.width - 1, grid.height - 1), 0, None, 0, ultra_crucible)

	def seen_key(self) -> Hashable:
		return self.pos, self.last_direction, self.repeated_last_direction

	def neighbours(self, grid: Grid) -> list[Self]:
		possible_directions: list[Direction]
		if self.last_direction is None:
			possible_directions = list(Direction)
		else:
			possible_directions = list(map(self.last_direction.rotate, [-1, 0, 1]))

		return list(filter(
			is_not_none,
			map(
				functools.partial(self._move_in_direction, grid=grid),
				possible_directions
			)
		))

	def _move_in_direction(self, direction: Direction, grid: Grid) -> Self | None:
		new_repeated_last_direction: int
		if direction == self.last_direction:
			max_straight_line: int = _MAX_ULTRA_STRAIGHT_LINE if self._ultra_crucible else _MAX_REGULAR_STRAIGHT_LINE

			new_repeated_last_direction = self.repeated_last_direction + 1
			if new_repeated_last_direction > max_straight_line:
				return None
		else:
			if (
				self._ultra_crucible
				and self.last_direction is not None
				and self.repeated_last_direction < _MIN_ULTRA_STRAIGHT_LINE
			):
				return None

			new_repeated_last_direction = 1

		new_position: Coord = self.pos + direction.to_delta()

		try:
			added_cost: int = grid[new_position]
			return State(
				new_position, self._end_pos, self.cost + added_cost, direction, new_repeated_last_direction,
				self._ultra_crucible
			)
		except IndexError:
			return None

	def _heuristic(self) -> int:
		return (self._end_pos - self.pos).manhattan()

	@property
	def estimate(self) -> int:
		return self.cost + self._heuristic()

	def __lt__(self, other: Self) -> bool:
		return self.estimate < other.estimate

	def __eq__(self, other: Self) -> bool:
		return self.estimate == other.estimate

	def is_end_state(self) -> bool:
		return (
			(self.pos == self._end_pos)
			and (not self._ultra_crucible or self.repeated_last_direction >= _MIN_ULTRA_STRAIGHT_LINE)
		)


def shortest_path(grid: Grid, ultra_crucible: bool = False) -> int:
	open_states: list[State] = [State.initial(grid, ultra_crucible)]
	seen_states: set[Hashable] = set()

	while open_states:
		state: State = heapq.heappop(open_states)

		if state.is_end_state():
			return state.cost

		if state.seen_key() in seen_states:
			continue

		seen_states.add(state.seen_key())

		for neighbour in state.neighbours(grid):
			heapq.heappush(open_states, neighbour)

	raise ValueError("Failed to find a path")


class Day17(DaySolver[Grid, int]):
	def __init__(self):
		super().__init__(17)

	def _solve_part1(self, part_input: Grid) -> int:
		return shortest_path(part_input)

	def _solve_part2(self, part_input: Grid) -> int:
		return shortest_path(part_input, ultra_crucible=True)

	def _parse_input(self, path: Path) -> Grid:
		with open(path) as f:
			return GenericGrid.from_raw_lines(map(str.strip, f.readlines()), int)


if __name__ == '__main__':
	Day17().solve()
