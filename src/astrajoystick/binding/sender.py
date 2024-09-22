"""Ways of sending `CodeMap`s to UInput."""

from abc import ABC, abstractmethod

from evdev import UInput  # type: ignore
from evdev.ecodes import EV_KEY  # type: ignore

from ..motion_thread import MotionThread
from .common import CodeMap


class Sender(ABC):
    @abstractmethod
    def send(self, uinput: UInput, code_map: CodeMap) -> None:
        """Send the given `code_map` to `uinput`."""
        pass


class PlainSender(Sender):
    """Send CodeMaps in a one-shot way."""

    def __init__(self):
        pass

    def send(self, uinput: UInput, code_map: CodeMap) -> None:
        for ecode, evalue in code_map.items():
            uinput.write(EV_KEY, ecode, evalue)
        uinput.syn()


class MotionSender(Sender):
    """Send CodeMaps through a MotionThread."""

    def __init__(self, motion_thread: MotionThread):
        self.mt = motion_thread

    def send(self, uinput: UInput, code_map: CodeMap) -> None:
        for ecode, evalue in code_map.items():
            self.mt.update(ecode, evalue)

        if self.mt.started:
            self.mt.try_join()
        else:
            self.mt.start(uinput)
