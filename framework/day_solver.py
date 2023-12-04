from abc import abstractmethod
from pathlib import Path

from shared.files import INPUT_PATH


class DaySolver[InputType, OutputType]:
	day: int

	def __init__(self, day: int):
		self.day = day

	@abstractmethod
	def _solve_part1(self, part_input: InputType) -> OutputType:
		pass

	@abstractmethod
	def _solve_part2(self, part_input: InputType) -> OutputType:
		pass

	def _input_file(self, part: int) -> Path:
		input_for_day: Path = INPUT_PATH / f"day{self.day}"
		both_file: Path = input_for_day / "both.txt"

		if both_file.is_file():
			return both_file

		return input_for_day / f"part{part}.txt"

	@abstractmethod
	def _parse_input(self, path: Path) -> InputType:
		pass

	def solve(self) -> None:
		print(f"Day {self.day}")

		input_part1: InputType = self._parse_input(self._input_file(1))
		output_part1: OutputType = self._solve_part1(input_part1)
		print(f"Part 1: {output_part1}")

		input_part2: InputType = self._parse_input(self._input_file(2))
		output_part2: OutputType = self._solve_part2(input_part2)
		print(f"Part 2: {output_part2}")
