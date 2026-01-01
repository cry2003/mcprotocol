# src/codec/data_types/primitives/unsigned_short.py

from dataclasses import dataclass
import struct


@dataclass(slots=True, frozen=True)
class UnsignedShort:
    """Represents an unsigned short integer in Minecraft protocol format.

    Encodes 16-bit unsigned integers in big-endian byte order.

    Attributes:
        value (int): The integer value to be encoded (0-65535).
    """
    value: int

    def __post_init__(self) -> None:
        """Validate the integer value after initialization.

        Raises:
            ValueError: If the value is outside the valid range for UnsignedShort.
        """
        if not 0 <= self.value <= 0xFFFF:
            raise ValueError("UnsignedShort must be between 0 and 65535")

    def __bytes__(self) -> bytes:
        """Convert the integer to its big-endian byte representation.

        Returns:
            bytes: The 2-byte big-endian encoded value.
        """
        return struct.pack(">H", self.value)
