import evdev  # type: ignore

from .config import BindingNotFoundError, parse_config


class Mainlooper:
    def __init__(self, device_path: str, config_path: str):
        self.dev = evdev.InputDevice(device_path)

        self.binds, self.modifiers = parse_config(config_path)
        self.modifiers_values = list(self.modifiers.values())

        self.uinput = evdev.UInput(
            {
                # Advertise all possible EV_KEY and EV_REL capabilities for uinput.
                # XXX: is there a better way to specify capabilities?
                evdev.ecodes.EV_KEY: range(max(evdev.ecodes.KEY)),
                evdev.ecodes.EV_REL: range(max(evdev.ecodes.REL)),
            },
            name="astrajoystick-uinput-device",
        )

    def mainloop(self) -> None:
        for ev in self.dev.read_loop():
            if active_keys := self.dev.active_keys():
                # Filter the active keys to include only the modifiers registered
                # in the config. If we don't do this, any pressed key can be
                # interpreted as a modifier.
                modifiers = frozenset(
                    x for x in active_keys if x in self.modifiers_values
                )
            else:
                modifiers = frozenset()

            try:
                binding = self.binds.get(ev.type, ev.code, modifiers)
            except BindingNotFoundError:
                pass
            else:
                binding.send(self.uinput, ev.value)
