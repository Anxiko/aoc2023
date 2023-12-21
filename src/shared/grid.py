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
		return self._rows[coord.y][coord.x]

	@classmethod
	def from_raw_lines(cls, raw_lines: list[str], tile_parser: Callable[[str], T]) -> Self:
		return cls([
			list(map(tile_parser, raw_line))
			for raw_line in raw_lines
		])

	def __str__(self) -> str:
		return '\n'.join(''.join(map(str, row)) for row in self._rows)
