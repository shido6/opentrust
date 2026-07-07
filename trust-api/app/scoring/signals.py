"""
Signal registry — each signal is a callable that returns a SignalResult.
Signals are discovered by the engine and evaluated in order.
"""

from typing import Awaitable, Callable, NamedTuple
from dataclasses import dataclass


class SignalResult(NamedTuple):
    name: str
    score_delta: int
    reason_code: str | None
    weight: float


SignalFn = Callable[..., Awaitable[SignalResult] | SignalResult]
SignalRegistry = dict[str, SignalFn]
