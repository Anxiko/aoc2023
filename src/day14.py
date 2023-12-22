import enum
import functools
import itertools
from pathlib import Path
from typing import Self, Callable, Mapping

from framework.day_solver import DaySolver
from shared.grid import Grid


class Tile(enum.StrEnum):
	Empty = '.'
	Fixed = '#'
	Movable = 'O'

	def __str__(self) -> str:
		return self.value


class Direction(enum.Enum):
	North = enum.auto()
	West = enum.auto()
	South = enum.auto()
	East = enum.auto()


type Day14Input = Grid[Tile]


def row_for_weight(factor: int, row: list[Tile]) -> int:
	return len(list(filter(
		lambda t: t == Tile.Movable,
		row
	))) * factor


def measure_weight(rows: list[list[Tile]] | Grid) -> int:
	if isinstance(rows, Grid):
		rows = list(rows.rows)

	return sum(itertools.starmap(
		row_for_weight,
		enumerate(reversed(rows), 1)
	))


def compress_line_reducer(
	compressed_line: list[tuple[int, Tile]], tile: Tile
) -> list[tuple[int, Tile]]:
	match compressed_line:
		case [*heads, (tail_count, tail_tile)] if tail_tile == tile:
			return [*heads, (tail_count + 1, tail_tile)]
		case _:
			return compressed_line + [(1, tile)]


def compress_line(line: list[Tile]) -> list[tuple[int, Tile]]:
	return functools.reduce(compress_line_reducer, line, [])


def decompress_line(compressed_line: list[tuple[int, Tile]]) -> list[Tile]:
	return list(itertools.chain.from_iterable(
		[tile] * tile_count for tile_count, tile in compressed_line
	))


class CompressedLineBuffer:
	result: list[tuple[int, Tile]]
	movable_in_buffer: int
	empty_in_buffer: int

	def __init__(self):
		self.result = []
		self.movable_in_buffer = 0
		self.empty_in_buffer = 0

	def _commit(self) -> None:
		if self.movable_in_buffer > 0:
			self.result.append((self.movable_in_buffer, Tile.Movable))
			self.movable_in_buffer = 0

		if self.empty_in_buffer > 0:
			self.result.append((self.empty_in_buffer, Tile.Empty))
			self.empty_in_buffer = 0

	def add_to_buffer(self, tile_count: int, tile: Tile) -> Self:
		match tile:
			case Tile.Fixed:
				self._commit()
				self.result.append((tile_count, tile))
			case Tile.Movable:
				self.movable_in_buffer += tile_count
			case Tile.Empty:
				self.empty_in_buffer += tile_count

		return self

	def get_result(self) -> list[tuple[int, Tile]]:
		self._commit()
		return self.result


def slide_compressed_line(compressed_line: list[tuple[int, Tile]]) -> list[tuple[int, Tile]]:
	return functools.reduce(
		lambda buffer, t: buffer.add_to_buffer(t[0], t[1]),
		compressed_line,
		CompressedLineBuffer()
	).get_result()


def slide_line_through_compression(line: list[Tile]) -> list[Tile]:
	return decompress_line(slide_compressed_line(compress_line(line)))


class CompoundTransformation[X]:
	type Transformation = Callable[[X], X]
	transformations: list[Transformation]

	def __init__(self, transformations: list[Transformation]):
		self.transformations = transformations

	@classmethod
	def identity(cls) -> Self:
		return CompoundTransformation([])

	def __call__(self, value: X) -> X:
		return functools.reduce(lambda v, f: f(v), self.transformations, value)

	def inverse(self) -> Self:
		return CompoundTransformation(list(reversed(self.transformations)))


def transpose_grid[X](grid: Grid[X]) -> Grid[X]:
	return grid.transpose()


def mirror_grid[X](grid: Grid[X]) -> Grid[X]:
	return grid.mirror()


def transformation_for_direction(direction: Direction) -> CompoundTransformation[Grid[Tile]]:
	match direction:
		case Direction.West:
			return CompoundTransformation.identity()
		case Direction.East:
			return CompoundTransformation([
				mirror_grid
			])
		case Direction.North:
			return CompoundTransformation([
				transpose_grid
			])
		case Direction.South:
			return CompoundTransformation([
				transpose_grid, mirror_grid
			])


def apply_oriented_grid(
	grid: Grid[Tile], f: Callable[[Grid[Tile]], Grid[Tile]], direction: Direction
) -> Grid[Tile]:
	transformation: CompoundTransformation[Grid[Tile]] = transformation_for_direction(direction)

	grid = transformation(grid)
	grid = f(grid)

	transformation = transformation.inverse()
	grid = transformation(grid)

	return grid


def slide_grid_rows(grid: Grid[Tile]) -> Grid[Tile]:
	rows: list[list[Tile]] = list(grid.rows)
	rows = list(map(slide_line_through_compression, rows))

	return Grid(rows)


def slide_grid_along_direction(grid: Grid[Tile], direction: Direction) -> Grid[Tile]:
	return apply_oriented_grid(grid, slide_grid_rows, direction)


def cycle_grid(grid: Grid[Tile]) -> Grid[Tile]:
	return functools.reduce(
		lambda g, d: slide_grid_along_direction(g, d),
		[Direction.North, Direction.West, Direction.South, Direction.East],
		grid
	)


def cycle_until_stable(grid: Grid[Tile], max_cycles: int) -> Grid[Tile]:
	seen_states: Mapping[Grid[Tile], int] = {grid: 0}

	for current_cycle in range(1, max_cycles + 1):
		grid = cycle_grid(grid)

		if (previous_cycle := seen_states.get(grid)) is not None:
			cycles_left = max_cycles - current_cycle
			loop_periodity: int = current_cycle - previous_cycle

			return cycle_until_stable(grid, cycles_left % loop_periodity)

		seen_states[grid] = current_cycle

	return grid


class Day14(DaySolver[Day14Input, int]):
	def __init__(self):
		super().__init__(14)

	def _solve_part1(self, part_input: Day14Input) -> int:
		grid: Grid = slide_grid_along_direction(part_input, Direction.North)

		return measure_weight(grid)

	def _solve_part2(self, part_input: Day14Input) -> int:
		grid = part_input
		grid = cycle_until_stable(grid, 1_000_000_000)

		return measure_weight(grid)

	def _parse_input(self, path: Path) -> Day14Input:
		with open(path) as f:
			return Grid.from_raw_lines(map(str.strip, f.readlines()), Tile)


if __name__ == '__main__':
	Day14().solve()
