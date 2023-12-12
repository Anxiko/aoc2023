import bisect
import functools
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO, Self, Iterable

from framework.day_solver import DaySolver


@dataclass
class IntegerRange:
	values: range

	@classmethod
	def from_limits(cls, start: int, stop: int) -> Self:
		if stop <= start:
			raise ValueError("Invalid limits for a non-empty range")
		return cls(range(start, stop))

	@classmethod
	def maybe_empty(cls, start: int, stop: int) -> Self | None:
		if start < stop:
			return cls.from_limits(start, stop)
		return None

	@classmethod
	def from_start_and_length(cls, start: int, length: int):
		if length <= 0:
			raise ValueError("Invalid length for range")

		return cls(range(start, start + length))

	def offset(self, offset: int) -> Self:
		return IntegerRange.from_limits(self.start + offset, self.stop + offset)

	@property
	def start(self) -> int:
		return self.values.start

	@property
	def stop(self) -> int:
		return self.values.stop

	def __and__(self, other: Self) -> Self | None:
		start: int = max(self.values.start, other.values.start)
		stop: int = min(self.values.stop, other.values.stop)

		return IntegerRange.maybe_empty(start, stop)

	def __contains__(self, value: int) -> bool:
		return value in self.values

	def __repr__(self) -> str:
		return f"[{self.start}, {self.stop})"


@dataclass
class RangeMappingEntry:
	src: IntegerRange
	offset: int

	@classmethod
	def from_starts(cls, src_start: int, dst_start: int, length: int) -> Self:
		return cls(IntegerRange.from_start_and_length(src_start, length), dst_start - src_start)

	@classmethod
	def from_line(cls, line: str) -> Self:
		dst, src, length = map(int, line.split())
		return cls.from_starts(src, dst, length)

	@property
	def dst(self) -> IntegerRange:
		return self.src.offset(self.offset)

	def map_value(self, v: int) -> int | None:
		if v in self:
			return v + self.offset
		return None

	def map_range(self, r: IntegerRange) -> tuple[IntegerRange | None, IntegerRange, IntegerRange | None] | None:
		src_intersection: IntegerRange | None = self.src & r
		if src_intersection is None:
			return

		left_unmapped: IntegerRange | None
		if src_intersection.start > r.start:
			left_unmapped = IntegerRange.from_limits(r.start, src_intersection.start)
		else:
			left_unmapped = None

		right_unmapped: IntegerRange | None
		if src_intersection.stop < r.stop:
			right_unmapped = IntegerRange.from_limits(src_intersection.stop, r.stop)
		else:
			right_unmapped = None

		mapped_intersection: IntegerRange = src_intersection.offset(self.offset)

		return left_unmapped, mapped_intersection, right_unmapped

	def __contains__(self, v: int) -> bool:
		return v in self.src

	def __repr__(self) -> str:
		return f"<{self.src} => {self.dst}>"


def mapping_entry_sorting_key(entry: RangeMappingEntry) -> int:
	return entry.src.start


@dataclass
class RangeMapping:
	entries: list[RangeMappingEntry]

	def __post_init__(self):
		self.entries.sort(key=mapping_entry_sorting_key)

	def _closest_le_entry_index(self, v: int) -> int | None:
		if idx := bisect.bisect_right(self.entries, v, key=mapping_entry_sorting_key):
			return idx - 1

		return None

	def _get_entry_for_value(self, v: int) -> RangeMappingEntry | None:
		closest_le_idx: int | None = self._closest_le_entry_index(v)
		if closest_le_idx is not None:
			entry: RangeMappingEntry = self.entries[closest_le_idx]
			if v in entry:
				return entry

		return None

	def map_range(self, values: IntegerRange) -> list[IntegerRange]:
		leftmost_idx: int = self._closest_le_entry_index(values.start)

		if leftmost_idx is None:
			leftmost_idx = 0

		mapped_ranges: list[IntegerRange] = []

		for entry in self.entries[leftmost_idx:]:
			match entry.map_range(values):
				case None:
					if entry.src.start >= values.stop:
						break

				case (left_unmapped, mapped, right_unmapped):
					if left_unmapped is not None:
						mapped_ranges.append(left_unmapped)

					mapped_ranges.append(mapped)

					values = right_unmapped
					if values is None:
						break

		if values is not None:
			mapped_ranges.append(values)

		return mapped_ranges

	def map_value(self, v: int) -> int:
		result: int | None = None
		if (entry := self._get_entry_for_value(v)) is not None:
			result = entry.map_value(v)

		return result if result is not None else v

	@classmethod
	def from_lines(cls, lines: list[str]) -> Self:
		_header, *raw_entries = lines
		return cls(
			list(map(RangeMappingEntry.from_line, raw_entries))
		)


@dataclass
class Day5Input:
	seeds: list[int]
	mappings: list[RangeMapping]

	@classmethod
	def from_file(cls, f: TextIO) -> Self:
		raw_seeds: str
		raw_mappings: list[list[str]]

		[raw_seeds], *raw_mappings = _chunk_on_empty(f)

		seeds: list[int] = list(map(int, raw_seeds.removeprefix("seeds:").split()))
		mappings: list[RangeMapping] = list(map(RangeMapping.from_lines, raw_mappings))

		return cls(seeds, mappings)


def _chunk_on_empty(f: TextIO) -> list[list[str]]:
	chunks: list[list[str]] = []
	current_chunk: list[str] = []

	line: str
	for line in f.readlines():
		line = line.rstrip("\n")

		if line != "":
			current_chunk.append(line)
		else:
			chunks.append(current_chunk)
			current_chunk = []

	chunks.append(current_chunk)

	return chunks


def _map_value_through(mappings: list[RangeMapping], v: int) -> int:
	for mapping in mappings:
		v = mapping.map_value(v)

	return v


def _min_position(seeds: Iterable[int], mappings: list[RangeMapping]) -> int:
	return min(map(functools.partial(_map_value_through, mappings), seeds))


def _pair_to_range(pair: tuple[int, int]) -> IntegerRange:
	start, length = pair
	return IntegerRange.from_start_and_length(start, length)


class Day5(DaySolver[Day5Input, int]):
	def __init__(self):
		super().__init__(5)

	def _solve_part1(self, part_input: Day5Input) -> int:
		return _min_position(part_input.seeds, part_input.mappings)

	def _solve_part2(self, part_input: Day5Input) -> int:
		values_list: list[IntegerRange] = list(map(_pair_to_range, itertools.batched(part_input.seeds, 2)))
		for mapping in part_input.mappings:
			mapped_values_list: list[IntegerRange] = []
			for values in values_list:
				mapped_values_list.extend(mapping.map_range(values))
			values_list = mapped_values_list

		return min(map(lambda r: r.start, values_list))

	def _parse_input(self, path: Path) -> Day5Input:
		with open(path) as f:
			return Day5Input.from_file(f)


if __name__ == '__main__':
	Day5().solve()
