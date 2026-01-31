from __future__ import annotations
import struct
from codec.data_types.data_types import DataType
from codec.data_types.constants import _INT32_MIN, _INT32_MAX


class Int(DataType):
    """Signed 32-bit integer (-2147483648 to 2147483647)."""

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Int must be an integer, got {type(value).__name__}")
        if not _INT32_MIN <= value <= _INT32_MAX:
            raise ValueError(
                f"Int must be between {_INT32_MIN} and {_INT32_MAX}, got {value}"
            )
        self.value = value

    def __bytes__(self) -> bytes:
        """Serialize as 4-byte signed integer, big-endian."""
        return struct.pack(">i", self.value)

    @classmethod
    def from_bytes(cls, data: bytes) -> Int:
        """Deserialize 4-byte signed integer."""
        if len(data) < 4:
            raise ValueError("Not enough bytes to read Int")
        value = struct.unpack(">i", data[:4])[0]
        return cls(value)
