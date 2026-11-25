"""What the search can go to."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchEntry:
    """One thing the search can go to: a screen, an action or a resource."""

    label: str
    detail: str
    run: Callable[[], None]
