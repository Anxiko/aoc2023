from day10 import Tile, parse_tile, scan_line


def test_scan_line():
	row: list[Tile] = list(map(parse_tile, ".|.|L---J..F---7|.|L7.F-J...|..|"))
	assert scan_line(row) == 5
