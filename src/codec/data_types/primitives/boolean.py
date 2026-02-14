# src/codec/data_types/primitives/boolean.py

from dataclasses import dataclass

from ..data_type import DataType


@dataclass(slots=True, frozen=True)
class Boolean(DataType):
    """Represents a Boolean in the Minecraft protocol.

    Encoding:
        - False → 0x00
        - True  → 0x01
    Stored as a single unsigned byte.

    Attributes:
        value (bool): The boolean value.

    Serialization:
        - `__bytes__()` returns the byte representation.
        - `from_bytes(data)` parses a single byte into a Boolean.
    """

    value: bool

    def __bytes__(self) -> bytes:
        """Return the single-byte representation of the boolean.

        Returns:
            bytes: b'\x01' for True, b'\x00' for False.
        """
        return b"\x01" if self.value else b"\x00"

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["Boolean", int]:
        """Deserialize a Boolean from a byte buffer.

        Args:
            data (bytes): Byte buffer containing at least one byte.
        Returns:
            Boolean: Deserialized Boolean instance.

        Raises:
            ValueError: If the buffer is empty or contains an invalid byte.
        """
        if not data:
            raise ValueError("Data too short to read Boolean")
        byte_val = data[0]
        if byte_val not in (0x00, 0x01):
            raise ValueError(f"Invalid Boolean byte: {byte_val}")
        return cls(bool(byte_val)), 1
