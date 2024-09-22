import threading
import time

from evdev import UInput  # type: ignore


class MotionThread:
    """TODO documentation"""

    def __init__(
        self,
        etype: int,
        einfo: dict[int, int],
        *,
        secs: float,
        minsecs: float,
        step: float,
        stepstep: float,
    ):
        self.etype = etype
        self.einfo = einfo
        self.evalues_stop = list(self.einfo.values())

        self.secs = secs
        self.minsecs = minsecs
        self.step = step
        self.stepstep = stepstep

        self.thread: threading.Thread
        self.started = False

    def start(self, uinput: UInput) -> None:
        self.thread = threading.Thread(target=self.loop, args=(uinput,))
        self.thread.start()
        self.started = True

    def update(self, ecode: int, evalue: int) -> None:
        self.einfo[ecode] = evalue

    def stopped(self) -> bool:
        """Return true is all values in einfo are equal to the initial values."""
        return all(i == j for i, j in zip(self.einfo.values(), self.evalues_stop))

    def try_join(self) -> None:
        if self.stopped():
            self.thread.join()
            self.started = False

    def loop(self, uinput: UInput) -> None:
        secs = self.secs
        minsecs = self.minsecs
        step = self.step
        stepstep = self.stepstep

        while not self.stopped():
            for ecode, evalue in self.einfo.items():
                uinput.write(self.etype, ecode, evalue)
            uinput.syn()

            # Check self.stopped() every 100ms so that the sleep doesn't
            # block for too long if `secs` is too big.
            cur = secs
            while cur > 0:
                sleep_for = 0.1 if cur >= 0.1 else cur
                time.sleep(sleep_for)
                cur -= sleep_for
                if self.stopped():
                    return

            if secs > minsecs:
                secs -= step
                step += stepstep
