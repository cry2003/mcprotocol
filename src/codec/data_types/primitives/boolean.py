# src/codec/data_types/primitives/boolean.py

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Boolean:
    """Represents a boolean value in Minecraft protocol format.

    Encodes boolean as a single unsigned byte:
        False -> 0x00
        True  -> 0x01

    Attributes:
        value (bool): The boolean value.
    """

    value: bool

    def __bytes__(self) -> bytes:
        """Return the single-byte representation of the boolean.

        Returns:
            bytes: b'\x01' for True, b'\x00' for False.
        """
        return b"\x01" if self.value else b"\x00"
