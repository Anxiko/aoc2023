import enum
import functools
import itertools
import math
import operator
import re
from abc import abstractmethod, ABC
from collections import defaultdict, deque, Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Self, MutableMapping, Protocol, Iterable

from framework.day_solver import DaySolver


class ModulatorType(enum.StrEnum):
	FlipFlop = '%'
	Conjunction = '&'
	Receiver = 'RX'
	Broadcaster = ''


MODULATOR_PATTERN: re.Pattern = re.compile(
	r"(?P<type>[%&]?)(?P<tag>[a-z]+) -> (?P<connections>(?:[a-z]+, )*[a-z]+)"
)


@dataclass
class ModulatorData:
	tag: str
	type: ModulatorType
	outputs: list[str]

	@classmethod
	def parse_modulator(cls, raw_line: str) -> Self:
		named_groups = MODULATOR_PATTERN.match(raw_line).groupdict()
		type_: ModulatorType = ModulatorType(named_groups['type'])
		tag: str = named_groups['tag']
		connections: list[str] = named_groups['connections'].split(', ')

		return cls(tag, type_, connections)

	@classmethod
	def rx(cls) -> Self:
		return cls('rx', ModulatorType.Receiver, [])


type Day20Input = list[ModulatorData]


@dataclass
class Signal:
	src: str
	dst: str
	value: bool


class Modulator(ABC):
	tag: str
	inputs: list[str]
	outputs: list[str]

	def __init__(self, tag: str):
		self.tag = tag
		self.inputs = []
		self.outputs = []

	def register_input(self, tag: str) -> None:
		self.inputs.append(tag)

	def register_output(self, tag: str) -> None:
		self.outputs.append(tag)

	@abstractmethod
	def process_signal(self, signal: Signal) -> list[Signal]:
		pass

	def _send_to(self, value: bool, dst: str) -> Signal:
		return Signal(self.tag, dst, value)

	def _send_to_all(self, value: bool) -> list[Signal]:
		return [self._send_to(value, output) for output in self.outputs]


class Broadcaster(Modulator):
	def process_signal(self, signal: Signal) -> list[Signal]:
		return self._send_to_all(signal.value)


class FlipFlop(Modulator):
	state: bool

	def __init__(self, tag: str):
		super().__init__(tag)
		self.state = False

	def process_signal(self, signal: Signal) -> list[Signal]:
		if not signal.value:
			self.state = not self.state
			return self._send_to_all(self.state)
		return []


class Conjunction(Modulator):
	memory: MutableMapping[str, bool]

	def __init__(self, tag: str):
		super().__init__(tag)
		self.memory = defaultdict(bool)

	def _all_true(self) -> bool:
		return all(self.memory[i] for i in self.inputs)

	def process_signal(self, signal: Signal) -> list[Signal]:
		self.memory[signal.src] = signal.value

		output: bool = not self._all_true()
		return self._send_to_all(output)


class Receiver(Modulator):
	counter: Counter[bool]

	def __init__(self, tag: str):
		super().__init__(tag)
		self.counter = Counter()

	def reset(self) -> None:
		self.counter = Counter()

	def process_signal(self, signal: Signal) -> list[Signal]:
		self.counter[signal.value] += 1
		return []

	def transmitting(self) -> bool:
		return self.counter[False] == 1 and self.counter[True] == 0


def create_modulator(tag: str, modulator_type: ModulatorType) -> Modulator:
	match modulator_type:
		case ModulatorType.Broadcaster:
			return Broadcaster(tag)
		case ModulatorType.FlipFlop:
			return FlipFlop(tag)
		case ModulatorType.Conjunction:
			return Conjunction(tag)
		case ModulatorType.Receiver:
			return Receiver(tag)
		case _:
			raise ValueError("Unknown modulator")


def create_circuit(modulator_data_list: list[ModulatorData]) -> dict[str, Modulator]:
	circuit: dict[str, Modulator] = {
		modulator_data.tag: create_modulator(modulator_data.tag, modulator_data.type)
		for modulator_data in modulator_data_list
	}

	for modulator_data in modulator_data_list:
		for output_tag in modulator_data.outputs:
			circuit[modulator_data.tag].register_output(output_tag)
			circuit[output_tag].register_input(modulator_data.tag)

	return circuit


class SignalObserver(Protocol):
	def observe(self, signal: Signal) -> None:
		pass


class SignalCounter:
	counter: Counter[bool]

	def __init__(self):
		self.counter = Counter()

	def observe(self, signal: Signal) -> None:
		self.counter[signal.value] += 1

	def value(self) -> int:
		return math.prod(self.counter.values())


class CycleCalculator:
	max_cycle_counts: int
	watched_dst: str
	sources: set[str]
	cycles: defaultdict[str, list[int]]

	def __init__(self, sources: set[str], watched_dst: str, max_cycle_counts: int):
		self.max_cycle_counts = max_cycle_counts
		self.sources = sources
		self.watched_dst = watched_dst
		self.cycles = defaultdict(list)

	@classmethod
	def for_circuit(cls, circuit: dict[str, Modulator], max_cycle_count: int) -> Self:
		rx: Modulator = circuit['rx']
		[rx_input_tag] = rx.inputs
		rx_feeder: Modulator = circuit[rx_input_tag]

		return cls(set(rx_feeder.inputs), rx_feeder.tag, max_cycle_count)

	def process_signal(self, signal: Signal, cycle: int) -> None:
		if signal.dst != self.watched_dst:
			return

		if signal.src not in self.sources:
			raise ValueError(f"Unexpected source detected: {signal}")

		if signal.value:
			self.cycles[signal.src].append(cycle)

	def samples_collected(self) -> bool:
		return all(len(self.cycles[c]) >= self.max_cycle_counts for c in self.sources)

	def observer_for_cycle(self, cycle: int) -> 'CycleObserver':
		return CycleObserver(self, cycle)

	@staticmethod
	def _derive_cycle(values: list[int]) -> int:
		[cycle] = list(set(itertools.starmap(operator.sub, itertools.pairwise(values))))
		return cycle

	def get_cycle(self) -> int:
		if not self.samples_collected():
			raise Exception("Not enough samples collected")

		cycles: list[int] = list(map(self._derive_cycle, self.cycles.values()))
		return math.lcm(*cycles)


class CycleObserver:
	cycle_calculator: CycleCalculator
	cycle: int

	def __init__(self, cycle_calculator: CycleCalculator, cycle: int):
		self.cycle_calculator = cycle_calculator
		self.cycle = cycle

	def observe(self, signal: Signal) -> None:
		self.cycle_calculator.process_signal(signal, self.cycle)


def process_impulses(circuit: dict[str, Modulator], initial_signal: Signal, observer: SignalObserver) -> None:
	pending_signals: deque[Signal] = deque([initial_signal])

	signal_count: Counter[bool] = Counter()

	while pending_signals:
		signal: Signal = pending_signals.popleft()
		observer.observe(signal)

		signal_count[signal.value] += 1

		modulator: Modulator = circuit[signal.dst]
		new_signals: list[Signal] = modulator.process_signal(signal)
		pending_signals.extend(new_signals)


def receiver_triggered(circuit: dict[str, Modulator]) -> bool:
	match circuit['rx']:
		case Receiver() as rx:
			return rx.transmitting()
		case _:
			raise ValueError("rx not a receiver")


class Day20(DaySolver[Day20Input, int]):
	def __init__(self):
		super().__init__(20)

	def _solve_part1(self, part_input: Day20Input) -> int:
		circuit: dict[str, Modulator] = create_circuit(part_input + [ModulatorData.rx()])
		signal_counter: SignalCounter = SignalCounter()

		for _ in range(1_000):
			process_impulses(circuit, Signal('button', 'broadcaster', False), signal_counter)

		return signal_counter.value()

	def _solve_part2(self, part_input: Day20Input) -> int:
		circuit: dict[str, Modulator] = create_circuit(part_input + [ModulatorData.rx()])
		cycle_calculator: CycleCalculator = CycleCalculator.for_circuit(circuit, 2)

		for cycle in itertools.count(0):
			if cycle_calculator.samples_collected():
				break

			if receiver_triggered(circuit):
				return cycle

			process_impulses(
				circuit, Signal('button', 'broadcaster', False), cycle_calculator.observer_for_cycle(cycle)
			)
		return cycle_calculator.get_cycle()

	def _parse_input(self, path: Path) -> Day20Input:
		with open(path) as f:
			return list(map(ModulatorData.parse_modulator, map(str.strip, f.readlines())))


if __name__ == '__main__':
	Day20().solve()
