"""Typed input and output declarations for Reference Reconcile."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    RUN = "reconcile_entries"


class Task(Enum):
    RUN = "reconcile-entries"


@dataclass
class Entry(Output):
    entry_id: Annotated[str, "Unique entry identifier within its source"]
    reference: Annotated[str, "Grouping reference identifier"]
    cents: Annotated[int, "Signed integer amount from -1000000000 through 1000000000"]


@dataclass
class ResultRow(Output):
    reference: Annotated[str, "Reference shared by the grouped entries"]
    bank_present: Annotated[bool, "Whether at least one bank entry has this reference"]
    ledger_present: Annotated[bool, "Whether at least one ledger entry has this reference"]
    bank_cents: Annotated[int, "Sum of bank amounts for the reference"]
    ledger_cents: Annotated[int, "Sum of ledger amounts for the reference"]
    difference_cents: Annotated[int, "Bank sum minus ledger sum"]


@dataclass
class TaskInput(Output):
    bank: Annotated[list[Entry], "At most 200 bank entries"]
    ledger: Annotated[list[Entry], "At most 200 ledger entries"]
    destination: Annotated[str, "New relative .json output path, never overwritten"]


@dataclass
class TaskOutput(Output):
    path: Annotated[str, "Artifact path matching destination"]
    records: Annotated[list[ResultRow], "Complete ordered task results"]
    total: Annotated[int, "Sum of absolute per-reference differences in cents"]


TOOLS = {Tool.RUN: (TaskInput, TaskOutput)}
TASKS = {Task.RUN: (TaskInput, TaskOutput)}
