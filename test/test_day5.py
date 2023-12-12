import pytest

from day5 import IntegerRange, Day5, RangeMappingEntry, mapping_entry_sorting_key, RangeMapping


class TestIntegerRange:
	def test_constructor(self):
		assert IntegerRange.from_limits(10, 20) == IntegerRange(range(10, 20))
		with pytest.raises(ValueError):
			IntegerRange.from_limits(20, 10)
		with pytest.raises(ValueError):
			IntegerRange.from_limits(10, 10)

		assert IntegerRange.maybe_empty(10, 20) == IntegerRange(range(10, 20))
		assert IntegerRange.maybe_empty(20, 10) is None
		assert IntegerRange.maybe_empty(10, 10) is None

		assert IntegerRange.from_start_and_length(10, 10) == IntegerRange(range(10, 20))
		with pytest.raises(ValueError):
			IntegerRange.from_start_and_length(10, 0)
		with pytest.raises(ValueError):
			IntegerRange.from_start_and_length(10, -10)

	def test_basics(self):
		assert IntegerRange(range(10, 20)).start == 10
		assert IntegerRange(range(10, 20)).stop == 20

		assert IntegerRange(range(10, 20)).offset(25) == IntegerRange(range(35, 45))

		assert 10 in IntegerRange(range(10, 20))
		assert 15 in IntegerRange(range(10, 20))
		assert 20 not in IntegerRange(range(10, 20))
		assert 5 not in IntegerRange(range(10, 20))
		assert 25 not in IntegerRange(range(10, 20))

		assert str(IntegerRange(range(10, 20))) == "[10, 20)"

	def test_intersection(self):
		# Disjoint
		assert IntegerRange(range(10, 20)) & IntegerRange(range(30, 40)) is None
		assert IntegerRange(range(10, 20)) & IntegerRange(range(20, 30)) is None
		assert IntegerRange(range(10, 20)) & IntegerRange(range(20, 30)) is None

		# Contained
		assert IntegerRange(range(10, 20)) & IntegerRange(range(12, 18)) == IntegerRange(range(12, 18))
		assert IntegerRange(range(12, 18)) & IntegerRange(range(10, 20)) == IntegerRange(range(12, 18))
		assert IntegerRange(range(10, 20)) & IntegerRange(range(10, 20)) == IntegerRange(range(10, 20))

		# Left and right
		assert IntegerRange(range(10, 20)) & IntegerRange(range(15, 25)) == IntegerRange(range(15, 20))
		assert IntegerRange(range(15, 25)) & IntegerRange(range(10, 20)) == IntegerRange(range(15, 20))


class TestRangeMappingEntry:
	def test_constructors(self):
		assert RangeMappingEntry.from_starts(10, 50, 10) == RangeMappingEntry(IntegerRange(range(10, 20)), 40)
		assert RangeMappingEntry.from_starts(10, 0, 40) == RangeMappingEntry(IntegerRange(range(10, 50)), -10)
		assert RangeMappingEntry.from_line("35 20 30") == RangeMappingEntry(IntegerRange(range(20, 50)), 15)

	def test_basics(self):
		assert RangeMappingEntry(IntegerRange(range(20, 30)), -30).dst == IntegerRange(range(-10, 0))
		assert 15 in RangeMappingEntry(IntegerRange(range(10, 20)), 10)
		assert 25 not in RangeMappingEntry(IntegerRange(range(10, 20)), 10)
		assert str(RangeMappingEntry(IntegerRange(range(20, 30)), -30)) == "<[20, 30) => [-10, 0)>"

	def test_map_value(self):
		assert RangeMappingEntry(IntegerRange(range(10, 20)), -10).map_value(15) == 5
		assert RangeMappingEntry(IntegerRange(range(10, 20)), -10).map_value(25) is None

	def test_map_range(self):
		entry: RangeMappingEntry = RangeMappingEntry(IntegerRange(range(10, 20)), -10)

		# Disjoint range mappings
		assert entry.map_range(IntegerRange(range(30, 40))) is None
		assert entry.map_range(IntegerRange(range(-10, 0))) is None

		# Range starts before mapping src
		assert (
			entry.map_range(IntegerRange(range(0, 10))) is None
		)
		assert (
			entry.map_range(IntegerRange(range(0, 11))) == (IntegerRange(range(0, 10)), IntegerRange(range(0, 1)), None)
		)
		assert (
			entry.map_range(IntegerRange(range(0, 15))) == (IntegerRange(range(0, 10)), IntegerRange(range(0, 5)), None)
		)
		assert (
			entry.map_range(IntegerRange(range(0, 20)))
			== (IntegerRange(range(0, 10)), IntegerRange(range(0, 10)), None)
		)
		assert (
			entry.map_range(IntegerRange(range(0, 30)))
			== (IntegerRange(range(0, 10)), IntegerRange(range(0, 10)), IntegerRange(range(20, 30)))
		)

		# Range start same as mapping src
		assert (
			entry.map_range(IntegerRange(range(10, 15)))
			== (None, IntegerRange(range(0, 5)), None)
		)
		assert (
			entry.map_range(IntegerRange(range(10, 20)))
			== (None, IntegerRange(range(0, 10)), None)
		)
		assert (
			entry.map_range(IntegerRange(range(10, 25)))
			== (None, IntegerRange(range(0, 10)), IntegerRange(range(20, 25)))
		)

		# Range starts after mapping src
		assert (
			entry.map_range(IntegerRange(range(12, 15)))
			== (None, IntegerRange(range(2, 5)), None)
		)
		assert (
			entry.map_range(IntegerRange(range(12, 20)))
			== (None, IntegerRange(range(2, 10)), None)
		)
		assert (
			entry.map_range(IntegerRange(range(12, 25)))
			== (None, IntegerRange(range(2, 10)), IntegerRange(range(20, 25)))
		)

		# Range starts at the end of the mapping src
		assert (
			entry.map_range(IntegerRange(range(20, 30))) is None
		)


class TestRangeMapping:
	def test_constructor(self):
		assert (
			RangeMapping([
				RangeMappingEntry(IntegerRange.from_limits(10, 20), 10),
				RangeMappingEntry(IntegerRange.from_limits(0, 40), 10),
				RangeMappingEntry(IntegerRange.from_limits(20, 30), 10),
			])
			==
			RangeMapping([
				RangeMappingEntry(IntegerRange.from_limits(0, 40), 10),
				RangeMappingEntry(IntegerRange.from_limits(10, 20), 10),
				RangeMappingEntry(IntegerRange.from_limits(20, 30), 10),
			])
		)

	def test_map_range_disjoint(self):
		range_mapping: RangeMapping = RangeMapping([
			RangeMappingEntry(IntegerRange.from_limits(0, 10), 10),
			RangeMappingEntry(IntegerRange.from_limits(10, 20), -5),
			RangeMappingEntry(IntegerRange.from_limits(40, 50), 20),
		])

		assert range_mapping.map_range(IntegerRange.from_limits(-20, -10)) == [IntegerRange.from_limits(-20, -10)]
		assert range_mapping.map_range(IntegerRange.from_limits(20, 30)) == [IntegerRange.from_limits(20, 30)]
		assert range_mapping.map_range(IntegerRange.from_limits(50, 60)) == [IntegerRange.from_limits(50, 60)]

	def test_map_range(self):
		range_mapping: RangeMapping = RangeMapping([
			RangeMappingEntry(IntegerRange.from_limits(0, 10), 10),
			RangeMappingEntry(IntegerRange.from_limits(10, 20), -5),
			RangeMappingEntry(IntegerRange.from_limits(40, 50), 20),
		])

		assert range_mapping.map_range(IntegerRange.from_limits(0, 10)) == [IntegerRange.from_limits(10, 20)]
		assert range_mapping.map_range(IntegerRange.from_limits(0, 20)) == [
			IntegerRange.from_limits(10, 20),
			IntegerRange.from_limits(5, 15)
		]
		assert range_mapping.map_range(IntegerRange.from_limits(-5, 25)) == [
			IntegerRange.from_limits(-5, 0),
			IntegerRange.from_limits(10, 20),
			IntegerRange.from_limits(5, 15),
			IntegerRange.from_limits(20, 25)
		]


class TestDay5Solver:
	def test_part1(self):
		assert Day5().solve_part1(testing=True) == 35

	def test_part2(self):
		assert Day5().solve_part2(testing=True) == 46
