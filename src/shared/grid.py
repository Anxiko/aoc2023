from typing import Iterable, Callable, Self

from shared.coord import Coord


class Grid[T]:
	type Line = list[T]

	_rows: list[Line]

	def __init__(self, rows: list[Line]):
		self._rows = rows

	@property
	def width(self) -> int:
		match self._rows:
			case []:
				return 0
			case [row, *_]:
				return len(row)

	@property
	def height(self) -> int:
		return len(self._rows)

	@property
	def rows(self) -> Iterable[Line]:
		return self._rows

	def _get_column(self, column: int) -> Line:
		return [row[column] for row in self._rows]

	@property
	def columns(self) -> Iterable[Line]:
		return map(self._get_column, range(self.width))

	def __getitem__(self, coord: Coord) -> T:
		if not self.is_valid_coord(coord):
			raise IndexError("Invalid coordinate")

		return self._rows[coord.y][coord.x]

	def __setitem__(self, coord: Coord, value: T) -> None:
		if not self.is_valid_coord(coord):
			raise IndexError("Invalid coordinate")
		self._rows[coord.y][coord.x] = value

	@classmethod
	def from_raw_lines(cls, raw_lines: Iterable[str], tile_parser: Callable[[str], T]) -> Self:
		return cls([
			list(map(tile_parser, raw_line))
			for raw_line in raw_lines
		])

	def transpose(self) -> Self:
		return Grid(list(self.columns))

	def mirror(self) -> Self:
		return Grid(list(map(lambda row: list(reversed(row)), self.rows)))

	@classmethod
	def initialize(cls, width: int, height: int, value_generator: Callable[[], T]) -> Self:
		return cls([
			[value_generator() for _ in range(width)]
			for _ in range(height)
		])

	def map_row[X](self, row_mapper: Callable[[list[T]], list[X]]) -> 'Grid[X]':
		return Grid(list(map(
			row_mapper,
			self.rows
		)))

	def map_tile[X](self, mapper: Callable[[T], X]) -> 'Grid[X]':
		def row_mapper(row: list[T]) -> list[X]:
			return list(map(mapper, row))

		return self.map_row(row_mapper)

	def is_valid_coord(self, coord: Coord) -> bool:
		return 0 <= coord.x < self.width and 0 <= coord.y < self.height

	def __str__(self) -> str:
		return '\n'.join(''.join(map(str, row)) for row in self._rows)

	def __eq__(self, other: Self) -> bool:
		return self._rows == other._rows

	def __hash__(self):
		return hash(tuple(tuple(row) for row in self._rows))
