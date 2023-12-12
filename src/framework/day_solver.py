from abc import abstractmethod
from pathlib import Path

from shared.files import INPUT_PATH


class DaySolver[InputType, OutputType]:
	day: int
	root: Path

	def __init__(self, day: int):
		self.day = day
		self.root = INPUT_PATH

	@abstractmethod
	def _solve_part1(self, part_input: InputType) -> OutputType:
		pass

	@abstractmethod
	def _solve_part2(self, part_input: InputType) -> OutputType:
		pass

	def _input_file(self, testing: bool) -> Path:
		input_for_day: Path = self.root / f"day{self.day}"

		filename: str = "test.txt" if testing else "both.txt"
		return input_for_day / filename

	@abstractmethod
	def _parse_input(self, path: Path) -> InputType:
		pass

	def solve_part1(self, testing: bool = False) -> OutputType:
		return self._solve_part1(self._parse_input(self._input_file(testing)))

	def solve_part2(self, testing: bool = False) -> OutputType:
		return self._solve_part2(self._parse_input(self._input_file(testing)))

	def solve(self, part1: bool = True, part2: bool = True, testing: bool = False) -> None:
		print(f"Day {self.day}")

		if part1:
			input_part1: InputType = self._parse_input(self._input_file(testing))
			output_part1: OutputType = self._solve_part1(input_part1)
			print(f"Part 1: {output_part1}")

		if part2:
			input_part2: InputType = self._parse_input(self._input_file(testing))
			output_part2: OutputType = self._solve_part2(input_part2)
			print(f"Part 2: {output_part2}")
