"""Lightweight trigger/statement helpers for strategy DSL semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Any
import pandas as pd


# Type aliases
Condition = Callable[[Any], bool]
Action = Callable[[Any], None]


@dataclass
class Trigger:
	condition: Condition
	action: Action
	name: Optional[str] = None
	last_state: bool = field(default=False, init=False)

	def evaluate(self, context: Any) -> None:
		current = False
		try:
			current = bool(self.condition(context))
		except Exception as exc:
			raise RuntimeError(f"Condition failed for trigger {self.name or ''}: {exc}") from exc

		if current and not self.last_state:
			try:
				self.action(context)
			except Exception as exc:
				raise RuntimeError(f"Action failed for trigger {self.name or ''}: {exc}") from exc
		self.last_state = current


_TRIGGERS: List[Trigger] = []
_ON_BAR: List[Action] = []


def always(condition: Condition, action: Action, name: Optional[str] = None) -> Trigger:
	trig = Trigger(condition=condition, action=action, name=name)
	_TRIGGERS.append(trig)
	return trig


def on_bar(action: Action) -> Action:
	_ON_BAR.append(action)
	return action


def run_triggers(context: Any) -> None:
	for action in list(_ON_BAR):
		action(context)
	for trig in list(_TRIGGERS):
		trig.evaluate(context)


def assign(value: Any) -> Any:
	return value


def assert_stmt(condition: bool, message: str = "assertion failed") -> None:
	if not condition:
		raise AssertionError(message)
	
def crossabove(a: pd.Series, b: pd.Series) -> pd.Series:
    """Edge-trigger: a crosses above b (prev <=, now >)."""
    return (a > b) & (a.shift(1) <= b.shift(1))


def crossbelow(a: pd.Series, b: pd.Series) -> pd.Series:
    """Edge-trigger: a crosses below b (prev >=, now <)."""
    return (a < b) & (a.shift(1) >= b.shift(1))


__all__ = [
	"Trigger",
	"always",
	"on_bar",
	"run_triggers",
	"assign",
	"assert_stmt",
	"crossabove",
	"crossbelow",
]
