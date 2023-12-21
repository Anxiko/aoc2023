import pytest

from day12 import Line, solutions_for_line, Day12


@pytest.mark.parametrize(",".join(["raw_line", "expected"]), [
	("???.### 1,1,3", 1),
	(".??..??...?##. 1,1,3", 4),
	("?#?#?#?#?#?#?#? 1,3,1,6", 1),
	("????.######..#####. 1,6,5", 4),
	("??????? 2,1", 10),
	("??? 1", 3),
	("?????? 2,1", 6),
	("?###???????? 3,2,1", 10)
])
def test_line_solutions(raw_line: str, expected: int):
	line: Line = Line.from_raw_line(raw_line)
	assert solutions_for_line(line) == expected


def test_line_unfold():
	assert Line.from_raw_line(".# 1").unfold(5) == Line.from_raw_line(".#?.#?.#?.#?.# 1,1,1,1,1")


@pytest.mark.parametrize(",".join(["raw_line", "expected"]), [
	("???.### 1,1,3", 1),
	(".??..??...?##. 1,1,3", 16384),
	("?#?#?#?#?#?#?#? 1,3,1,6", 1),
	("????.#...#... 4,1,1", 16),
	("????.######..#####. 1,6,5", 2500),
	("?###???????? 3,2,1", 506250),
	(".?????...? 1,1,1", 1316327)
])
def test_line_unfolded_solutions(raw_line: str, expected: int):
	line: Line = Line.from_raw_line(raw_line).unfold(5)
	assert solutions_for_line(line) == expected


def test_parts():
	assert Day12().solve_part1() == 7922
	assert Day12().solve_part2() == 18093821750095
