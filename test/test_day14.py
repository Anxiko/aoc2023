from day14 import Tile, measure_weight, Day14, slide_grid_along_direction, Direction, cycle_grid
from shared.grid import Grid


def test_small_grid_slide():
	lines = """\
OOOO.#.O..
OO..#....#
OO..O##..O
O..#.OO...
........#.
..#....#.#
..O..#.O.O
..O.......
#....###..
#....#....\
	"""

	grid = Grid.from_raw_lines(lines.split(), Tile)

	grid = slide_grid_along_direction(grid, Direction.North)

	assert measure_weight(grid) == 136


def test_part_1():
	assert Day14().solve_part1() == 109345


def test_cycle():
	lines = """\
	OOOO.#.O..
	OO..#....#
	OO..O##..O
	O..#.OO...
	........#.
	..#....#.#
	..O..#.O.O
	..O.......
	#....###..
	#....#....\
		"""

	expected_lines = """\
.....#....
....#...O#
...OO##...
.OO#......
.....OOO#.
.O#...O#.#
....O#....
......OOOO
#...O###..
#..OO#....\
	"""
	expected_grid = Grid.from_raw_lines(expected_lines.split(), Tile)

	grid = Grid.from_raw_lines(lines.split(), Tile)
	grid = cycle_grid(grid)

	assert grid == expected_grid


def test_part_2():
	assert Day14().solve_part2() == 112452
