# src/codec/data_types/complex/identifier.py

import re
from ..primitives.string import String
from codec.packets.constants import _NAMESPACE_RE, _VALUE_RE



class Identifier(String):
    """
    Minecraft namespaced identifier, e.g., 'minecraft:stone'.

    Format:
        [namespace:]value
        - namespace defaults to 'minecraft' if omitted.
        - namespace: [a-z0-9._-]+
        - value: [a-z0-9._/-]+
        - total length: 1 to (32767 * 3) + 3 bytes

    Raises:
        ValueError if identifier is invalid.
    """

    MAX_LENGTH_BYTES = (32767 * 3) + 3

    def __init__(self, value: str):
        # Must be a string
        if not isinstance(value, str):
            raise TypeError(f"Identifier must be a string, got {type(value).__name__}")

        # Split namespace and path
        parts = value.split(":")
        if len(parts) > 2:
            raise ValueError(f"Identifier '{value}' cannot contain more than one ':'")

        if len(parts) == 2:
            namespace, path = parts
        else:
            namespace, path = "minecraft", parts[0]

        # Non-empty checks
        if not namespace:
            raise ValueError(f"Namespace cannot be empty in identifier '{value}'")
        if not path:
            raise ValueError(f"Value/path cannot be empty in identifier '{value}'")

        # Regex validation
        if not _NAMESPACE_RE.fullmatch(namespace):
            raise ValueError(f"Invalid namespace '{namespace}' in identifier '{value}'")
        if not _VALUE_RE.fullmatch(path):
            raise ValueError(f"Invalid value/path '{path}' in identifier '{value}'")

        # Byte length validation
        byte_length = len(value.encode("utf-8"))
        if not (1 <= byte_length <= self.MAX_LENGTH_BYTES):
            raise ValueError(f"Identifier length {byte_length} bytes out of bounds")

        # Store final normalized value
        super().__init__(f"{namespace}:{path}")

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["Identifier", int]:
        string_value, consumed = String.from_bytes(data)
        return cls(string_value.value), consumed

    @property
    def namespace(self) -> str:
        return self.value.split(":", 1)[0]

    @property
    def path(self) -> str:
        return self.value.split(":", 1)[1]
