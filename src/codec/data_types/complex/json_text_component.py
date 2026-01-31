# src/codec/data_types/complex/json_text_component.py

from __future__ import annotations
import json

from codec.data_types.primitives.varint import VarInt


class JsonTextComponent:
    __slots__ = ("component",)

    def __init__(self, component: dict | list | str) -> None:
        if isinstance(component, JsonTextComponent):
            raise TypeError("Nested JsonTextComponent is not allowed")

        self.component = component

    def __bytes__(self) -> bytes:
        encoded = json.dumps(
            self.component,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return bytes(VarInt(len(encoded))) + encoded

    @classmethod
    def from_bytes(cls, data: bytes) -> JsonTextComponent:
        length, offset = VarInt.from_bytes(data)
        raw = data[offset : offset + length]
        return cls(json.loads(raw.decode("utf-8")))
