from day18 import Day18


def test_part_1():
	assert Day18().solve_part1(testing=True) == 62


def test_real_part_1():
	assert Day18().solve_part1() == 49578


def test_real_part_2():
	assert Day18().solve_part2() == 52885384955882
