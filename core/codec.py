"""Turns state dataclasses into JSON-ready data and back.

Saves and the frontend both use this, so the state has exactly one serialized
shape. Supported field types: dataclasses, lists, dicts with string keys,
Optional, and plain scalars.
"""
from dataclasses import fields, is_dataclass
import types
import typing


_HINTS = {}


def hints(kind):
    if kind not in _HINTS:
        _HINTS[kind] = typing.get_type_hints(kind)
    return _HINTS[kind]


def dump(value):
    if is_dataclass(value):
        declared = hints(type(value))
        out = {}
        for f in fields(value):
            item = getattr(value, f.name)
            # Float fields always serialize as floats, so a save looks the same before and after loading.
            if declared[f.name] is float and type(item) is int:
                item = float(item)
            out[f.name] = dump(item)
        return out
    if isinstance(value, (list, tuple)):
        return [dump(v) for v in value]
    if isinstance(value, dict):
        return {k: dump(v) for k, v in value.items()}
    return value


def load(kind, data):
    if data is None:
        return None
    origin = typing.get_origin(kind)
    if origin in (typing.Union, types.UnionType):
        inner = [a for a in typing.get_args(kind) if a is not type(None)]
        return load(inner[0], data)
    if origin is list:
        (item,) = typing.get_args(kind)
        return [load(item, v) for v in data]
    if origin is tuple:
        return tuple(data)
    if origin is dict:
        _, item = typing.get_args(kind)
        return {k: load(item, v) for k, v in data.items()}
    if is_dataclass(kind):
        declared = hints(kind)
        known = {f.name for f in fields(kind)}
        # Unknown keys are dropped and missing ones take their defaults, so
        # older saves keep loading after a system gains a field.
        return kind(**{k: load(declared[k], v) for k, v in data.items() if k in known})
    if kind is float and isinstance(data, int):
        return float(data)
    return data
