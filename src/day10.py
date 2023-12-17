import enum
import functools
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Mapping, Iterable

from framework.day_solver import DaySolver
from shared.coord import Coord


class Direction(enum.Enum):
	North = enum.auto()
	East = enum.auto()
	South = enum.auto()
	West = enum.auto()

	def to_delta(self) -> Coord:
		match self:
			case Direction.North:
				return Coord(0, -1)
			case Direction.East:
				return Coord(1, 0)
			case Direction.South:
				return Coord(0, 1)
			case Direction.West:
				return Coord(-1, 0)

	def __neg__(self) -> Self:
		match self:
			case Direction.North:
				return Direction.South
			case Direction.East:
				return Direction.West
			case Direction.South:
				return Direction.North
			case Direction.West:
				return Direction.East


ALL_DIRECTIONS: set[Direction] = set(Direction)

PIPE_CHAR_TO_DIRECTIONS: Mapping[str, set[Direction]] = {
	'|': {Direction.North, Direction.South},
	'-': {Direction.West, Direction.East},
	'L': {Direction.North, Direction.East},
	'J': {Direction.North, Direction.West},
	'7': {Direction.South, Direction.West},
	'F': {Direction.South, Direction.East},
	'S': set(Direction)
}


@dataclass
class Pipe:
	connections: set[Direction]
	is_start: bool

	def is_accessible_from(self, d: Direction) -> bool:
		return -d in self.connections


type Tile = Pipe | None

type Grid = list[list[Tile]]


@dataclass
class Day10Input:
	grid: Grid
	start_coord: Coord

	@property
	def grid_size(self) -> tuple[int, int]:
		if len(self.grid) == 0:
			return 0, 0

		return len(self.grid[0]), len(self.grid)

	@property
	def all_grid_coords(self) -> Iterable[Coord]:
		width, height = self.grid_size
		return map(Coord.from_tuple, itertools.product(range(width), range(height)))


def parse_tile(char: str) -> Tile:
	if (directions := PIPE_CHAR_TO_DIRECTIONS.get(char)) is not None:
		return Pipe(directions, char == 'S')
	return None


def parse_line(line: str) -> tuple[list[Tile], int | None]:
	x_coord: int | None = None
	tiles: list[Tile] = []

	for x, char in enumerate(line):
		tile: Tile = parse_tile(char)
		if tile is not None and tile.is_start:
			x_coord = x

		tiles.append(tile)
	return tiles, x_coord


def parse_input(lines: Iterable[str]) -> Day10Input:
	start_coord: Coord | None = None
	grid: Grid = []
	for y, line in enumerate(lines):
		parsed_line, maybe_x = parse_line(line)
		if maybe_x is not None:
			start_coord = Coord(maybe_x, y)
		grid.append(parsed_line)

	if start_coord is None:
		raise ValueError("Could not find a starting tile")
	return Day10Input(grid, start_coord)


def read_coord(coord: Coord, grid: Grid) -> Tile | None:
	try:
		return grid[coord.y][coord.x]
	except IndexError:
		return None


def write_cord(coord: Coord, grid: Grid, tile: Tile) -> None:
	grid[coord.y][coord.x] = tile


def connected_tiles(coord: Coord, grid: Grid, directions: Iterable[Direction]) -> list[tuple[Direction, Coord, Tile]]:
	result: list[tuple[Direction, Coord, Tile]] = []

	for direction in directions:
		neighbour_coord: Coord = coord + direction.to_delta()

		tile: Tile = read_coord(neighbour_coord, grid)
		if isinstance(tile, Pipe) and tile.is_accessible_from(direction):
			result.append((direction, neighbour_coord, tile))

	return result


def cycle_path(coord: Coord, grid: Grid) -> list[Coord]:
	path: list[Coord] = [coord]
	tile: Tile = read_coord(coord, grid)
	if tile is None:
		raise ValueError("Initial coord is not a pipe")

	prev_direction: Direction
	prev_coord: Coord
	prev_tile: Tile

	[(prev_direction, prev_coord, prev_tile), _] = connected_tiles(coord, grid, tile.connections)

	while True:
		if prev_tile.is_start:
			break

		path.append(prev_coord)

		possible_directions: set[Direction] = prev_tile.connections - {-prev_direction}
		[(prev_direction, prev_coord, prev_tile)] = connected_tiles(prev_coord, grid, possible_directions)

	return path


def verify_path(path: Iterable[Coord], grid: Grid) -> None:
	for prev_coord, next_coord in itertools.pairwise(path):
		prev_tile: Tile = read_coord(prev_coord, grid)
		if not isinstance(prev_tile, Pipe):
			raise ValueError(f"Non-pipe in path at {prev_coord}: {prev_tile}")

		neighbours: set[Coord] = set(prev_coord + d.to_delta() for d in prev_tile.connections)

		if next_coord not in neighbours:
			raise ValueError("Invalid transition from {prev_coord} to {next_coord}")


def all_coords(grid: Grid) -> set[Coord]:
	height: int = len(grid)
	width: int = len(grid[0])

	return set(map(Coord.from_tuple, itertools.product(range(width), range(height))))


def coord_is_inside_grid(grid: Grid, coord: Coord) -> bool:
	height: int
	width: int

	if len(grid) == 0:
		height, width = 0, 0
	else:
		height = len(grid)
		width = len(grid[0])

	return 0 <= coord.y < height and 0 <= coord.x < width


def explore_region(coord: Coord, grid: Grid, path: set[Coord]) -> tuple[set[Coord], bool]:
	region: set[Coord] = set()
	unexplored_coords: set[Coord] = {coord}

	is_outside: bool = False

	while unexplored_coords:
		coord: Coord = unexplored_coords.pop()
		neighbours: set[Coord] = set(coord.neighbours()) - path
		valid_neighbours: set[Coord] = set(filter(functools.partial(coord_is_inside_grid, grid), neighbours))

		if len(valid_neighbours) < len(neighbours):
			is_outside = True

		unexplored_coords |= valid_neighbours - region
		region.add(coord)

	return region, is_outside


def draw_grid(grid: Grid, path: set[Coord], inside_coords: set[Coord]) -> None:
	def render_coord(c: Coord) -> str:
		if c in path:
			return 'X'
		elif c in inside_coords:
			return 'I'
		else:
			return ' '

	height: int
	width: int

	if len(grid) == 0:
		height, width = 0, 0
	else:
		height = len(grid)
		width = len(grid[0])

	for y in range(height):
		for x in range(width):
			print(render_coord(Coord(x, y)), end='')
		print()


def replacement_pipe(coord: Coord, grid: Grid) -> Pipe:
	coord_connections: set[Coord] = set(
		direction for (direction, _coord, _tile) in connected_tiles(coord, grid, ALL_DIRECTIONS)
	)
	if len(coord_connections) != 2:
		raise ValueError(f"Unexpected amount of connections from coord: {coord_connections}")
	for pipe, pipe_connections in PIPE_CHAR_TO_DIRECTIONS.items():
		if pipe_connections == coord_connections:
			return Pipe(pipe_connections, False)


def scan_line(row: list[Tile]) -> int:
	inside_count: int = 0
	is_inside: bool = False

	for tile in row:
		if isinstance(tile, Pipe):
			if Direction.North in tile.connections:  # Should also work if only counting down connections
				is_inside = not is_inside
		else:
			if is_inside:
				inside_count += 1

	return inside_count


class Day10(DaySolver[Day10Input, int]):
	def __init__(self):
		super().__init__(10)

	def _solve_part1(self, part_input: Day10Input) -> int:
		path: list[Coord] = cycle_path(part_input.start_coord, part_input.grid)

		verify_path(path, part_input.grid)
		verify_path(reversed(path), part_input.grid)

		path_length: int = len(path[1:])

		return path_length // 2 + path_length % 2

	def _solve_part2(self, part_input: Day10Input) -> int:
		path: set[Coord] = set(cycle_path(part_input.start_coord, part_input.grid))
		replacement_start: Pipe = replacement_pipe(part_input.start_coord, part_input.grid)
		write_cord(part_input.start_coord, part_input.grid, replacement_start)

		for coord in set(part_input.all_grid_coords) - path:
			write_cord(coord, part_input.grid, None)

		return sum(map(scan_line, part_input.grid))

	def _parse_input(self, path: Path) -> Day10Input:
		with open(path) as f:
			lines: Iterable[str] = map(str.strip, f.readlines())
			return parse_input(lines)


if __name__ == '__main__':
	Day10().solve()
