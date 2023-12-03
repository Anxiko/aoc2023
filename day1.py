from shared.files import INPUT_PATH

NUMERIC_DIGITS: dict[str, int] = {str(digit): digit for digit in range(1, 10 + 1)}
SPELT_DIGITS: list[tuple[str, int]] = [
	((idx + 1), value) for (idx, value) in
	enumerate(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"])
]


def parse_spelt_digit(substring: str) -> int | None:
	for (spelt_value, spelt_digit) in SPELT_DIGITS:
		if substring.startswith(spelt_digit):
			return spelt_value
	return None


def digits_to_number(digits: tuple[int, int]) -> int:
	return digits[0] * 10 + digits[1]


def extract_digits(line: str, use_spelt_digits: bool) -> tuple[int, int]:
	digits: list[int] = []
	for idx, char in enumerate(line):
		digit: int | None = NUMERIC_DIGITS.get(char)

		if digit is None and use_spelt_digits:
			digit = parse_spelt_digit(line[idx:])

		if digit is not None:
			digits.append(digit)

	return digits[0], digits[-1]


def calculate_solution(lines: list[str], use_spelt_digits: bool) -> int:
	return sum(map(
		lambda line: digits_to_number(extract_digits(line, use_spelt_digits)),
		lines
	))


def part1(lines: list[str]) -> int:
	return calculate_solution(lines, use_spelt_digits=False)


def part2(lines: list[str]) -> int:
	return calculate_solution(lines, use_spelt_digits=True)


if __name__ == '__main__':
	with open(INPUT_PATH / "day1" / "both.txt") as f:
		lines: list[str] = list(map(str.strip, f.readlines()))

		result_part1: int = part1(lines)
		print(f"Part 1: {result_part1}")

		result_part2: int = part2(lines)
		print(f"Part 2: {result_part2}")
