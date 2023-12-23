import enum
import functools
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Iterable

from framework.day_solver import DaySolver
from shared.coord import Direction, Coord
from shared.grid import Grid as GenericGrid


class Tile(enum.StrEnum):
	Empty = '.'
	NorthEastMirror = '/'
	NorthWestMirror = '\\'
	VerticalSplitter = '|'
	HorizontalSplitter = '-'

	def outgoing_directions(self, direction: Direction) -> set[Direction]:
		match self, direction:
			case Tile.VerticalSplitter, Direction.East | Direction.West:
				return {Direction.North, Direction.South}

			case Tile.HorizontalSplitter, Direction.North | Direction.South:
				return {Direction.East, Direction.West}

			case Tile.NorthWestMirror, Direction.West | Direction.East as horizontal_direction:
				return {horizontal_direction.rotate(-1)}
			case Tile.NorthWestMirror, Direction.North | Direction.South as vertical_direction:
				return {vertical_direction.rotate(1)}

			case Tile.NorthEastMirror, Direction.West | Direction.East as horizontal_direction:
				return {horizontal_direction.rotate(1)}
			case Tile.NorthEastMirror, Direction.North | Direction.South as vertical_direction:
				return {vertical_direction.rotate(-1)}

			case _, _:
				return {direction}


type Grid = GenericGrid[Tile]


@dataclass(frozen=True)
class Beam:
	position: Coord
	direction: Direction

	def advance(self) -> Self:
		delta: Coord = self.direction.to_delta()
		return Beam(self.position + delta, self.direction)

	def get_position(self) -> Coord:
		return self.position

	def divert(self, direction: Direction) -> Self:
		return Beam(self.position, direction)


def explore_grid(grid: Grid, initial: Beam = Beam(Coord(0, 0), Direction.East)) -> set[Beam]:
	active_beams: set[Beam] = {initial}
	seen_beams: set[Beam] = set()

	while active_beams:
		active_beam: Beam = active_beams.pop()
		seen_beams.add(active_beam)

		tile: Tile = grid[active_beam.position]
		marching_beams: set[Beam] = set(filter(
			lambda beam: grid.is_valid_coord(beam.get_position()),
			map(
				lambda direction: active_beam.divert(direction).advance(),
				tile.outgoing_directions(active_beam.direction)
			)
		))

		active_beams |= marching_beams - seen_beams

	return seen_beams


def exploration_score(beams: set[Beam]) -> int:
	return len(set(map(Beam.get_position, beams)))


def render_energized_grid(width: int, height: int, energized_coords: set[Coord]) -> str:
	return '\n'.join(
		''.join('#' if Coord(x, y) in energized_coords else '.' for x in range(width))
		for y in range(height)
	)


class Day16(DaySolver[Grid, int]):
	def __init__(self):
		super().__init__(16)

	def _solve_part1(self, part_input: Grid) -> int:
		return exploration_score(explore_grid(part_input))

	def _solve_part2(self, part_input: Grid) -> int:
		starts: Iterable[Beam] = itertools.chain.from_iterable(
			map(lambda c: Beam(c, direction), coords) for coords, direction in
			[
				(map(lambda x: Coord(x, 0), range(part_input.width)), Direction.South),
				(map(lambda x: Coord(x, part_input.height - 1), range(part_input.width)), Direction.North),
				(map(lambda y: Coord(0, y), range(part_input.height)), Direction.East),
				(map(lambda y: Coord(part_input.width - 1, y), range(part_input.height)), Direction.West),
			]
		)

		return max(map(
			exploration_score,
			map(functools.partial(explore_grid, part_input), starts),
		))

	def _parse_input(self, path: Path) -> Grid:
		with open(path) as f:
			return GenericGrid.from_raw_lines(map(str.strip, f.readlines()), Tile)


if __name__ == '__main__':
	Day16().solve()
