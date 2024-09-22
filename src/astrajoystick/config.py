"""Interface for the toml config."""

import tomllib
from pprint import pformat
from textwrap import indent

from evdev import ecodes  # type: ignore

from .binding import mapper, sender
from .binding.binding import Binding
from .binding.common import CodeMap
from .motion_thread import MotionThread


class InvalidConfigError(Exception):
    pass


def ecode_from_str(name: str) -> int:
    """Convert a string describing a member in evdev.ecodes into its value."""
    return ecodes.__dict__[name]


def code_map_from_str(d: dict[str, int]) -> CodeMap:
    """Convert the str keys from a dict into int ecodes."""
    return {ecode_from_str(k): v for k, v in d.items()}


def pred_from_str(pred: str) -> mapper.Predicate:
    """Return a Predicate function from a string.

    A predicate string has one of the following formats:

        -  "NUM": the function returns True if VAL is *equal* to NUM (VAL == NUM);
        -  "<NUM": returns True if VAL is *less* than NUM (VAL < NUM);
        -  ">NUM": returns True if VAL is *greater* than NUM (VAL > NUM);
        -  "else": always returns True.

    Where NUM is any integer number, and VAL is the value of the event
    received.
    """

    def try_parse_int(s: str) -> int:
        try:
            return int(s)
        except ValueError as e:
            raise InvalidConfigError(
                f"invalid predicate: could not parse number: {s}"
            ) from e

    if pred[0] == "<":
        # `__gt__` because the order is inverted: NUM > VAL
        return try_parse_int(pred[1:]).__gt__

    if pred[0] == ">":
        # idem
        return try_parse_int(pred[1:]).__lt__

    if pred == "else":
        return lambda _: True

    return try_parse_int(pred).__eq__


class BindingNotFoundError(Exception):
    pass


class BindingDict:
    """Helper for managing a collection of bindings.

    The bindings themselves are stored in a dict, so the time complexity for
    `put` and `get` are about O(1).
    """

    def __init__(self) -> None:
        self._binds: dict[tuple[int, int, frozenset[int]], Binding] = {}

    def put(self, b: Binding) -> None:
        """Insert a binding into the dict."""
        key = (b.in_etype, b.in_ecode, b.modifiers)
        self._binds[key] = b

    def get(self, etype: int, ecode: int, modifiers: frozenset[int]) -> Binding:
        """Retrieve a binding with the given properties."""
        key = (etype, ecode, modifiers)
        try:
            return self._binds[key]
        except KeyError as e:
            raise BindingNotFoundError from e


def _get_ecode(bind: dict, key: str) -> int:
    """Try to convert the str ecode of the `key` entry in `bind`."""
    try:
        in_etype_str = bind[key]
    except KeyError as e:
        raise InvalidConfigError(f"{key} is not defined") from e

    try:
        return ecode_from_str(in_etype_str)
    except KeyError as e:
        raise InvalidConfigError(f"could not parse {key} into a valid ecode") from e


def _get_modifiers(bind: dict, modifiers: dict[str, int]) -> list[int]:
    """Translate modifier names (specified in the [modifiers] section
    into their corresponding int ecodes in modifiers."""
    assert modifiers is not None

    if modifiers_str := bind.get("modifiers"):
        try:
            return [modifiers[x] for x in modifiers_str]
        except KeyError as e:
            raise InvalidConfigError(
                "modifier name is not defined in the [modifier] section"
            ) from e

    return []


def _get_mapper(bind: dict) -> mapper.Mapper:
    """Get the appropriate Mapper for `bind`."""
    try:
        mapping = bind["mapping"]
    except KeyError as e:
        raise InvalidConfigError("bind has no mapping section") from e

    if len(mapping) > 1:
        raise InvalidConfigError("mapping must have only one section")

    if opts := mapping.get("plain"):
        out_ecode = ecode_from_str(opts["out"])
        return mapper.PlainMapper(out_ecode)
    elif opts := mapping.get("preds"):
        preds = [pred_from_str(x) for x in opts.keys()]
        code_maps = [code_map_from_str(x) for x in opts.values()]
        return mapper.PredMapper(preds, code_maps)

    mapping_type = list(mapping.keys())[0]
    raise InvalidConfigError(f"invalid mapping type: {mapping_type}")


def _get_sender(bind: dict, templates: dict) -> sender.Sender:
    """Get the appropriate Sender for `bind`."""
    if motion := bind.get("motion"):
        out_etype = ecode_from_str(motion["out_etype"])
        init = {ecode_from_str(k): v for k, v in motion["init"].items()}

        if isinstance(motion["opts"], str):
            # bind["opts"] contains the template name;
            # replace it with the actual opts
            opts = templates[motion["opts"]]
        else:
            opts = motion["opts"]

        return sender.MotionSender(MotionThread(out_etype, init, **opts))
    else:
        return sender.PlainSender()


def parse_config(config_path: str) -> tuple[BindingDict, dict]:
    with open(config_path, "rb") as f:
        c = tomllib.load(f)

    binds = BindingDict()

    modifiers = (
        {name: ecode_from_str(ecode_str) for name, ecode_str in c["modifier"].items()}
        if "modifier" in c
        else {}
    )

    templates = c.get("template", {})

    for bind in c.get("bind", []):
        try:
            binding = Binding(
                _get_ecode(bind, "in_etype"),
                _get_ecode(bind, "in_ecode"),
                _get_modifiers(bind, modifiers),
                _get_mapper(bind),
                _get_sender(bind, templates),
            )
        except InvalidConfigError as e:
            pretty_bind = indent(pformat(bind), "\t")
            print(f"{type(e).__name__}: {e}\nIn bind:\n{pretty_bind}")
        else:
            binds.put(binding)

    return binds, modifiers
