import enum
import functools
import math
import re
from abc import abstractmethod, ABC
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Mapping, Iterable

from framework.day_solver import DaySolver
from shared.extra_itertools import chunk_on

WORKFLOW_PATTERN: re.Pattern = re.compile(
	r"(?P<tag>[a-z]+)\{(?P<rules>[^}]+)}"
)

RULE_PATTERN: re.Pattern = re.compile(
	r"((?P<condition>[^:]+):)?(?P<result>[a-z]+|A|R)"
)

CONDITION_PATTERN: re.Pattern = re.compile(r"(?P<attribute>[xmas])(?P<comparator>[><])(?P<value>\d+)")

MACHINE_PART_PATTERN: re.Pattern = re.compile(
	r"\{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)}"
)


class Attribute(enum.StrEnum):
	X = 'x'
	M = 'm'
	A = 'a'
	S = 's'


@dataclass
class MachinePart:
	attributes: dict[Attribute, int]

	def __getitem__(self, key: Attribute) -> int:
		return self.attributes[key]

	@classmethod
	def from_dict(cls, d: Mapping[str, int | str]) -> Self:
		attributes: dict[Attribute, int] = {Attribute(k): int(v) for k, v in d.items()}
		if set(d.keys()) != set(Attribute):
			raise ValueError(f"Missing values in raw dictionary: {d}")

		return cls(attributes)

	@classmethod
	def parse_machine_part(cls, raw_machine_part: str) -> Self:
		match: re.Match | None = MACHINE_PART_PATTERN.match(raw_machine_part)
		if match is None:
			raise ValueError(f"Invalid machine part {raw_machine_part!r}")

		return cls.from_dict(match.groupdict())

	def total_value(self) -> int:
		return sum(self.attributes.values())


@dataclass(frozen=True)
class Range:
	left: int
	right: int

	def __post_init__(self):
		if self.left > self.right:
			raise ValueError("Invalid range")

	def __len__(self):
		return self.right - self.left + 1


@dataclass
class RangeMachinePart:
	attributes: dict[Attribute, Range]

	@classmethod
	def initial(cls, r: Range) -> Self:
		return cls({a: r for a in Attribute})

	def __getitem__(self, item: Attribute) -> Range:
		return self.attributes[item]

	def _replace_attribute_range(self, attribute: Attribute, r: Range) -> Self:
		return RangeMachinePart(self.attributes | {attribute: r})

	def split_on(
		self, attribute: Attribute, left_range: Range | None, right_range: Range | None
	) -> tuple[Self | None, Self | None]:
		left: Self | None = self._replace_attribute_range(attribute, left_range) if left_range is not None else None
		right: Self | None = self._replace_attribute_range(attribute, right_range) if right_range is not None else None

		return left, right

	def combinations(self) -> int:
		return math.prod(map(len, self.attributes.values()))


@dataclass(frozen=True)
class WorkflowTag:
	tag: str

	@classmethod
	def initial(cls) -> Self:
		return cls('in')


@dataclass
class WorkflowResult:
	accepted: bool

	@classmethod
	def accept(cls) -> Self:
		return cls(True)

	@classmethod
	def reject(cls) -> Self:
		return cls(False)


class Comparator(ABC):
	@abstractmethod
	def __call__(self, left: int, right: int) -> bool:
		pass

	@abstractmethod
	def split_range(self, r: Range, pivot: int) -> tuple[Range | None, Range | None]:
		pass


class LessThan(Comparator):
	def __call__(self, left: int, right: int) -> bool:
		return left < right

	def split_range(self, r: Range, pivot: int) -> tuple[Range | None, Range | None]:
		if pivot <= r.left:
			return None, r
		if pivot <= r.right:
			return Range(r.left, pivot - 1), Range(pivot, r.right)
		return r, None


class GreaterThan(Comparator):
	def __call__(self, left: int, right: int) -> bool:
		return left > right

	def split_range(self, r: Range, pivot: int) -> tuple[Range | None, Range | None]:
		if pivot >= r.right:
			return None, r
		if pivot >= r.left:
			return Range(pivot + 1, r.right), Range(r.left, pivot)
		return r, None


_COMPARATOR_SYMBOL_MAPPING: Mapping[str, Comparator] = {
	'>': GreaterThan(),
	'<': LessThan()
}


@dataclass
class Condition:
	attribute: Attribute
	comparator: Comparator
	value: int

	@classmethod
	def parse_condition(cls, raw_condition: str) -> Self:
		match: re.Match | None = CONDITION_PATTERN.match(raw_condition)
		if match is None:
			raise ValueError(f"Invalid condition: {raw_condition!r}")

		attribute: Attribute = Attribute(match["attribute"])
		comparator: Comparator = _COMPARATOR_SYMBOL_MAPPING[match["comparator"]]
		value: int = int(match["value"])

		return cls(attribute, comparator, value)

	def satisfied_by(self, machine_part: MachinePart) -> bool:
		return self.comparator(machine_part[self.attribute], self.value)

	def split_range_machine_part(
		self, rmp: RangeMachinePart
	) -> tuple[RangeMachinePart | None, RangeMachinePart | None]:
		r: Range = rmp[self.attribute]
		left_range, right_range = self.comparator.split_range(r, self.value)
		return rmp.split_on(self.attribute, left_range, right_range)


@dataclass
class Rule:
	maybe_condition: Condition | None
	tag_or_result: WorkflowTag | WorkflowResult

	@staticmethod
	def _parse_tag_of_result(tag_or_result: str) -> WorkflowTag | WorkflowResult:
		match tag_or_result:
			case 'A':
				return WorkflowResult.accept()
			case 'R':
				return WorkflowResult.reject()

			case tag:
				return WorkflowTag(tag)

	@classmethod
	def parse_rule(cls, raw_rule: str) -> Self:
		match: re.Match | None = RULE_PATTERN.match(raw_rule)
		if match is None:
			raise ValueError(f"Invalid rule: {raw_rule!r}")

		maybe_condition: Condition | None
		if (raw_condition := match['condition']) is not None:
			maybe_condition = Condition.parse_condition(raw_condition)
		else:
			maybe_condition = None

		tag_or_result: WorkflowTag | WorkflowResult = cls._parse_tag_of_result(match['result'])

		return cls(maybe_condition, tag_or_result)

	def output_for_machine_part(self, machine_part: MachinePart) -> WorkflowTag | WorkflowResult | None:
		if self.maybe_condition is None or self.maybe_condition.satisfied_by(machine_part):
			return self.tag_or_result
		return None

	def output_for_range_machine_part(
		self, rmp: RangeMachinePart
	) -> tuple[tuple[WorkflowTag | WorkflowResult, RangeMachinePart] | None, RangeMachinePart | None]:
		satisfied_rmp: RangeMachinePart | None
		unsatisfied_rmp: RangeMachinePart | None

		if self.maybe_condition is not None:
			satisfied_rmp, unsatisfied_rmp = self.maybe_condition.split_range_machine_part(rmp)
		else:
			satisfied_rmp, unsatisfied_rmp = rmp, None

		return (self.tag_or_result, satisfied_rmp) if satisfied_rmp is not None else None, unsatisfied_rmp


@dataclass
class Workflow:
	tag: WorkflowTag
	rules: list[Rule]

	@classmethod
	def parse_workflow(cls, raw_workflow: str) -> Self:
		match: re.Match | None = WORKFLOW_PATTERN.match(raw_workflow)
		if match is None:
			raise ValueError(f"Invalid workflow: {raw_workflow!r}")

		tag: WorkflowTag = WorkflowTag(match['tag'])
		raw_rules: list[str] = match['rules'].split(',')
		rules: list[Rule] = list(map(Rule.parse_rule, raw_rules))

		return cls(tag, rules)

	def as_mapping_key(self) -> tuple[WorkflowTag, Self]:
		return self.tag, self

	def output_for_machine_part(self, machine_part: MachinePart) -> WorkflowTag | WorkflowResult:
		for rule in self.rules:
			if (output := rule.output_for_machine_part(machine_part)) is not None:
				return output

		raise ValueError(f"No rule matched for {machine_part}")

	def output_for_range_machine_part(
		self, rmp: RangeMachinePart
	) -> list[tuple[WorkflowTag | WorkflowResult, RangeMachinePart]]:
		pending: RangeMachinePart | None = rmp
		results: list[tuple[WorkflowTag | WorkflowResult, RangeMachinePart]] = []

		for rule in self.rules:
			if pending is None:
				break

			satisfied_and_result, pending = rule.output_for_range_machine_part(pending)
			match satisfied_and_result:
				case (_satisfied, _result_for_satisfied) as partial_result:
					results.append(partial_result)
				case None:
					pass

		return results


@dataclass
class Day19Input:
	mapped_workflows: dict[WorkflowTag, Workflow]
	machine_parts: list[MachinePart]

	@classmethod
	def from_raw_lines(cls, raw_lines: Iterable[str]) -> Self:
		raw_workflows, raw_machine_parts = chunk_on(raw_lines, lambda line: len(line) == 0)
		return cls(
			dict(map(Workflow.as_mapping_key, map(Workflow.parse_workflow, raw_workflows))),
			list(map(MachinePart.parse_machine_part, raw_machine_parts))
		)


def check_machine_accepted(
	machine_part: MachinePart, mapped_workflows: dict[WorkflowTag, Workflow],
	selected_workflow: WorkflowTag = WorkflowTag('in')
) -> bool:
	workflow: Workflow = mapped_workflows[selected_workflow]
	match workflow.output_for_machine_part(machine_part):
		case WorkflowResult(accepted=accepted):
			return accepted
		case WorkflowTag() as tag:
			return check_machine_accepted(machine_part, mapped_workflows, tag)


class Day19(DaySolver[Day19Input, int]):
	def __init__(self):
		super().__init__(19)

	def _solve_part1(self, part_input: Day19Input) -> int:
		accepted_machine_parts: Iterable[MachinePart] = filter(
			functools.partial(check_machine_accepted, mapped_workflows=part_input.mapped_workflows),
			part_input.machine_parts
		)

		return sum(map(MachinePart.total_value, accepted_machine_parts))

	def _solve_part2(self, part_input: Day19Input) -> int:
		accepted: list[RangeMachinePart] = []
		rejected: list[RangeMachinePart] = []

		pending: deque[tuple[WorkflowTag, RangeMachinePart]] = deque(
			[
				(WorkflowTag.initial(), RangeMachinePart.initial(Range(1, 4000)))
			]
		)

		while pending:
			tag, rmp = pending.popleft()
			workflow: Workflow = part_input.mapped_workflows[tag]

			workflow_output: list[tuple[WorkflowTag | WorkflowResult, RangeMachinePart]] = \
				workflow.output_for_range_machine_part(rmp)

			for tag_or_result, processed_rmp in workflow_output:
				match tag_or_result:
					case WorkflowTag() as next_tag:
						pending.append((next_tag, processed_rmp))
					case WorkflowResult(accepted=True):
						accepted.append(processed_rmp)
					case WorkflowResult(accepted=False):
						rejected.append(processed_rmp)
					case _:
						raise ValueError(f"Unhandled tag or result: {tag_or_result!r}")

		return sum(map(RangeMachinePart.combinations, accepted))

	def _parse_input(self, path: Path) -> Day19Input:
		with open(path) as f:
			return Day19Input.from_raw_lines(map(str.strip, f.readlines()))


if __name__ == '__main__':
	Day19().solve()
