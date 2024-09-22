"""Represents a `[[bind]]` entry in the toml config."""

from typing import Iterable

from evdev import UInput  # type: ignore

from .mapper import Mapper
from .sender import Sender


class Binding:
    """Represents a `[[bind]]` entry in the toml config.

    This class is hashable over the immutable properties `in_etype`,
    `in_ecode` and `modifiers`.
    """

    def __init__(
        self,
        in_etype: int,
        in_ecode: int,
        modifiers: Iterable[int],
        mapper: Mapper,
        sender: Sender,
    ):
        self.in_etype = in_etype
        self.in_ecode = in_ecode
        self.modifiers = frozenset(modifiers)
        self.mapper = mapper
        self.sender = sender

    def __hash__(self):
        return hash((self.in_etype, self.in_ecode, self.modifiers))

    def send(self, uinput: UInput, evalue: int):
        if code_map := self.mapper.try_map(evalue):
            self.sender.send(uinput, code_map)
