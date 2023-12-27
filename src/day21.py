import enum
import functools
import operator
from collections import deque
from pathlib import Path
from typing import MutableMapping, Iterable

from framework.day_solver import DaySolver
from shared.coord import Coord, Direction
from shared.grid import Grid


class InputTile(enum.StrEnum):
	Plot = '.'
	Rock = '#'
	Start = 'S'


def input_tile_is_obstacle(tile: InputTile) -> bool:
	return tile == InputTile.Rock


def find_start(grid: Grid[InputTile]) -> Coord:
	for coord, tile in grid.tiles_with_position():
		if tile == InputTile.Start:
			return coord


def valid_neighbours(coord: Coord, grid: Grid[bool]) -> list[Coord]:
	return list(
		filter(
			lambda c: grid.is_valid_coord(c) and not grid[c],
			map(functools.partial(operator.add, coord), map(Direction.to_delta, Direction))
		)
	)


def navigate(grid: Grid[bool], start: Coord, max_steps: int) -> set[Coord]:
	frontier: deque[tuple[Coord, int]] = deque([(start, 0)])

	seen_states: set[tuple[Coord, int]] = set()

	reached_coords: set[Coord] = set()

	while frontier:
		coord, step = state = frontier.popleft()
		if state in seen_states:
			continue
		seen_states.add(state)

		if step < max_steps:
			neighbours: Iterable[Coord] = valid_neighbours(coord, grid)
			frontier.extend([(n, step + 1) for n in neighbours])
		else:
			reached_coords.add(coord)

	return reached_coords


type Day21Input = Grid[InputTile]


class Day21(DaySolver[Day21Input, int]):
	def __init__(self):
		super().__init__(21)

	def _solve_part1(self, part_input: Day21Input) -> int:
		start: Coord = find_start(part_input)
		obstacle_grid: Grid[bool] = part_input.map_tile(input_tile_is_obstacle)
		return len(navigate(obstacle_grid, start, 64))

	def _solve_part2(self, part_input: Day21Input) -> int:
		pass

	def _parse_input(self, path: Path) -> Day21Input:
		with open(path) as f:
			return Grid.from_raw_lines(map(str.strip, f.readlines()), InputTile)


if __name__ == '__main__':
	Day21().solve(testing=False, part2=False)
