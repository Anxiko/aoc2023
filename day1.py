from shared.files import INPUT_PATH

DIGITS: dict[str, int] = (
	{str(digit): digit for digit in range(1, 10 + 1)}
	| {
		(idx + 1): value for (idx, value) in
		enumerate(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"])
	}
)


def extract_digits(line: str) -> tuple[int, int]:
	first: int | None = None
	last: int | None = None

	for char in line:
		if (digit_value := DIGITS.get(char)) is not None:
			if first is None:
				first = digit_value
			else:
				last = digit_value

	if first is None:
		raise ValueError(f"Couldn't extract digits from {line!r}")

	if last is None:
		last = first

	return first, last


def sum_digits(digits: tuple[int, int]) -> int:
	return digits[0] * 10 + digits[1]


def part1(input_part1: list[str]) -> int:
	return sum(map(
		lambda line: sum_digits(extract_digits(line)),
		input_part1
	))


if __name__ == '__main__':
	with open(INPUT_PATH / "day1" / "part1.txt") as f:
		result_part1: int = part1([line.strip() for line in f.readlines()])
		print(f"Part 1: {result_part1}")
