# src/codec/data_types/primitives/varint.py

from dataclasses import dataclass
from ..constants import _SEGMENT_BITS, _CONTINUE_BIT, _MAX_VARINT


@dataclass(slots=True, frozen=True)
class VarInt:
    """Represents a variable-length 32-bit signed integer in Minecraft protocol format.

    Encodes integers using 1 to 5 bytes, where each byte uses 7 bits for value
    and the most significant bit (MSB) as a continuation flag.

    Attributes:
        value (int): The integer value to be encoded (0 to _MAX_VARINT).
    """

    value: int

    def __post_init__(self) -> None:
        """Validate the integer value after initialization.

        Raises:
            ValueError: If the value is not between 0 and _MAX_VARINT.
        """
        if not 0 <= self.value <= _MAX_VARINT:
            raise ValueError("VarInt must be between 0 and 4294967295")

    def __bytes__(self) -> bytes:
        """Convert the integer to its variable-length byte representation.

        Returns:
            bytes: The VarInt-encoded bytes.
        """
        value = self.value
        result = bytearray()
        while True:
            if (value & ~_SEGMENT_BITS) == 0:
                result.append(value)
                break
            result.append((value & _SEGMENT_BITS) | _CONTINUE_BIT)
            value >>= 7
        return bytes(result)

    @classmethod
    def from_bytes(cls, data: bytes) -> "VarInt":
        """
        Decodes a VarInt from a sequence of bytes.

        Args:
            data (bytes): Byte sequence containing the VarInt.

        Returns:
            VarInt: Decoded VarInt object.

        Raises:
            ValueError: If the VarInt is too long (>5 bytes) or malformed.
        """
        num_read = 0
        result = 0
        for b in data:
            value = b & _SEGMENT_BITS
            result |= value << (7 * num_read)
            num_read += 1
            if num_read > 5:
                raise ValueError("VarInt is too long (max 5 bytes)")
            if (b & _CONTINUE_BIT) == 0:
                return cls(result)
        raise ValueError("Incomplete VarInt bytes")