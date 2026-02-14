# src/codec/data_types/complex/json_text_component.py

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from codec.data_types.data_type import DataType
from codec.data_types.primitives.varint import VarInt
from codec.data_types.complex.text_component import TextComponent


_JSON_COMPONENT_DECODE_MAX_CHARS = 262144
_JSON_COMPONENT_ENCODE_MAX_CHARS = 32767
_JSON_COMPONENT_MAX_UTF8_BYTES = _JSON_COMPONENT_DECODE_MAX_CHARS * 3


@dataclass(slots=True)
class JsonTextComponent(DataType):
    """
    JSON Text Component (network string format).

    Wire format:
    - VarInt byte length
    - UTF-8 JSON payload

    Notes:
    - Decoder accepts up to 262144 characters (spec limit).
    - Encoder is capped at 32767 characters to match vanilla behavior since 1.20.3.
    """

    component: str | dict[str, Any] | list[Any]

    def __post_init__(self) -> None:
        if not isinstance(self.component, (str, dict, list)):
            raise TypeError(
                "JsonTextComponent must be str, dict or list, "
                f"got {type(self.component).__name__}"
            )
        # Reuse TextComponent normalization/validation rules.
        self.component = TextComponent(self.component).component

    def __bytes__(self) -> bytes:
        # Keep JSON wire format, but validate/canonicalize via TextComponent.
        canonical_component = TextComponent(self.component).component
        json_text = json.dumps(
            canonical_component,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if not (1 <= len(json_text) <= _JSON_COMPONENT_ENCODE_MAX_CHARS):
            raise ValueError(
                "JSON Text Component encode length out of bounds: "
                f"{len(json_text)} chars (max {_JSON_COMPONENT_ENCODE_MAX_CHARS})"
            )

        encoded = json_text.encode("utf-8")
        return bytes(VarInt(len(encoded))) + encoded

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["JsonTextComponent", int]:
        length, consumed = VarInt.from_bytes(data)
        payload_len = length.value

        if payload_len < 1:
            raise ValueError("JSON Text Component payload cannot be empty")
        if payload_len > _JSON_COMPONENT_MAX_UTF8_BYTES:
            raise ValueError(
                "JSON Text Component payload too large: "
                f"{payload_len} bytes (max {_JSON_COMPONENT_MAX_UTF8_BYTES})"
            )

        start = consumed
        end = start + payload_len
        if len(data) < end:
            raise ValueError("Data too short for JSON Text Component payload")

        raw = data[start:end]
        text = raw.decode("utf-8")
        if len(text) > _JSON_COMPONENT_DECODE_MAX_CHARS:
            raise ValueError(
                "JSON Text Component decoded length too large: "
                f"{len(text)} chars (max {_JSON_COMPONENT_DECODE_MAX_CHARS})"
            )

        component = json.loads(text)
        if not isinstance(component, (str, dict, list)):
            raise ValueError(
                "JSON Text Component root must be string, object, or list"
            )

        normalized = TextComponent(component).component
        return cls(normalized), end
