from typing import Iterable, Callable, Generator


def chunk_on[X](iterable: Iterable[X], sep_detector: Callable[[X], bool]) -> Generator[list[X], None, None]:
	current_chunk: list[X] = []
	for element in iterable:
		if sep_detector(element):
			yield current_chunk
			current_chunk = []
		else:
			current_chunk.append(element)
	yield current_chunk


def unzip[X](tuples_iterable: Iterable[tuple[X, ...]]) -> tuple[list[X], ...]:
	return tuple(zip(*tuples_iterable))
