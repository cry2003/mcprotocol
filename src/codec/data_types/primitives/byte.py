# src/codec/data_types/primitives/byte.py

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Byte:
    """Represents a single signed byte in Minecraft protocol.

    Encoding:
        - 1 byte
        - Signed 8-bit integer, two's complement
        - Range: -128 to 127

    Attributes:
        value (int): The byte value.

    Serialization:
        - `__bytes__()` encodes the integer as a single byte.
        - `from_bytes(data, offset=0)` decodes the byte from a buffer.

    Validation:
        - Raises ValueError if the value is outside -128..127.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate the byte value after initialization.

        Raises:
            ValueError: If value not in [-128, 127].
        """
        if not -128 <= self.value <= 127:
            raise ValueError("Byte value must be between -128 and 127")

    def __bytes__(self) -> bytes:
        """Serialize the value as a single signed byte.

        Returns:
            bytes: Single-byte representation.
        """
        return self.value.to_bytes(1, byteorder="big", signed=True)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> tuple["Byte", int]:
        """Deserialize a Byte from a byte buffer starting at `offset`.

        Args:
            data (bytes): Byte buffer.
            offset (int): Start index.

        Returns:
            tuple[Byte, int]: Byte instance and number of bytes consumed (1).

        Raises:
            ValueError: If buffer is too short.
        """
        if len(data) < offset + 1:
            raise ValueError("Data too short to read a Byte")
        value = int.from_bytes(data[offset : offset + 1], byteorder="big", signed=True)
        return cls(value), 1
