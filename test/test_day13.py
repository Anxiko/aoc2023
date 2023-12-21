import pytest

from day13 import Tile, score_for_grid
from shared.grid import Grid


@pytest.mark.parametrize(','.join(["raw_grid", "expected"]), [
	(
		"""\
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.\
		""",
		5
	)
])
def test_grid_score(raw_grid: str, expected: int):
	grid: Grid[Tile] = Grid.from_raw_lines(raw_grid.split(), Tile)
	print(grid)
	assert score_for_grid(grid) == expected
