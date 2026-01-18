# src/codec/data_types/primitives/boolean.py

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Boolean:
    """Represents a Boolean in the Minecraft protocol.

    Encoding:
        - False → 0x00
        - True  → 0x01
    Stored as a single unsigned byte.

    Attributes:
        value (bool): The boolean value.

    Serialization:
        - `__bytes__()` returns the byte representation.
        - Ensures protocol-compliant single-byte encoding.
    """
    
    value: bool

    def __bytes__(self) -> bytes:
        """Return the single-byte representation of the boolean.

        Returns:
            bytes: b'\x01' for True, b'\x00' for False.
        """
        return b"\x01" if self.value else b"\x00"
