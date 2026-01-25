# src/codec/data_types/primitives/unsigned_short.py

from dataclasses import dataclass
import struct


@dataclass(slots=True, frozen=True)
class UnsignedShort:
    """Represents a 16-bit unsigned integer in Minecraft protocol.

    Encoding:
        - Big-endian 2-byte representation.

    Attributes:
        value (int): Integer value between 0 and 65535.

    Validation:
        - Raises ValueError if the value is out of range.

    Serialization:
        - `__bytes__()` returns the 2-byte big-endian value.
        - `from_bytes(data)` deserializes from a byte buffer.
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

    @classmethod
    def from_bytes(cls, data: bytes) -> "UnsignedShort":
        """Deserialize an UnsignedShort from a byte buffer.

        Args:
            data (bytes): Byte buffer containing at least 2 bytes.

        Returns:
            UnsignedShort: UnsignedShort instance.

        Raises:
            ValueError: If buffer is too short to read 2 bytes.
        """
        if len(data) < 2:
            raise ValueError("Data too short to read UnsignedShort")
        value = struct.unpack_from(">H", data)[0]
        return cls(value)
