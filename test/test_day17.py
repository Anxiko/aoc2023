from day17 import Day17


def test_part_1():
	assert Day17().solve_part1(testing=True) == 102
	assert Day17().solve_part1(testing=False) == 855


def test_part_2():
	assert Day17().solve_part2(testing=True) == 94
	assert Day17().solve_part2(testing=False) == 980
