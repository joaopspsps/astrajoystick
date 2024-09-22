"""Ways of turning a bind's `mapping` section into `CodeMap`s"""

from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional

from .common import CodeMap

Predicate = Callable[[int], bool]


class Mapper(ABC):
    @abstractmethod
    def try_map(self, evalue: int) -> Optional[CodeMap]:
        """Return the CodeMap associated with event with value `evalue."""
        pass


class PlainMapper(Mapper):
    """Always maps to CodeMaps with ecode given by `out_ecode`, and with
    evalue equal to the received `evalue`."""

    def __init__(self, out_ecode: int) -> None:
        self.out_ecode = out_ecode

    def try_map(self, evalue: int) -> Optional[CodeMap]:
        return {self.out_ecode: evalue}


class PredMapper(Mapper):
    """Mappings are given in pairs of Predicates and CodeMaps.

    A Predicate is a function that takes as argument the evalue of the
    received event, and returns True if the CodeMap associated with that
    evalue should be sent, or False otherwise.
    """

    def __init__(
        self, preds: Iterable[Predicate], code_maps: Iterable[CodeMap]
    ) -> None:
        if len(preds) != len(code_maps):
            raise ValueError("preds and code_maps should have the same length")

        self.preds = preds
        self.code_maps = code_maps

    def try_map(self, evalue: int) -> Optional[CodeMap]:
        for pred, code_map in zip(self.preds, self.code_maps):
            if pred(evalue):
                return code_map
        return None
