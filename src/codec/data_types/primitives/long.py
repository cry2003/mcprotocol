from dataclasses import dataclass
import struct
from ..constants import _MAX_LONG, _MIN_LONG


@dataclass(slots=True, frozen=True)
class Long:
    """
    Represents a signed 64-bit integer in Minecraft protocol format.

    Attributes:
        value (int): Integer value between -2^63 and 2^63 - 1.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate that value fits in a signed 64-bit integer."""
        if not _MIN_LONG <= self.value <= _MAX_LONG:
            raise ValueError(f"Long must be between {_MIN_LONG} and {_MAX_LONG}, got {self.value}")

    def __bytes__(self) -> bytes:
        """
        Serialize the Long as 8 bytes, big-endian, two's complement.

        Returns:
            bytes: 8-byte representation of the integer.
        """
        return struct.pack(">q", self.value)

    def __repr__(self) -> str:
        return f"<Long value={self.value}>"

    def __str__(self) -> str:
        return str(self.value)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "Long":
        """Construct a Long from 8 raw bytes."""
        if len(data) < 8:
            raise ValueError(f"Not enough bytes to unpack Long, got {len(data)}")
        value = struct.unpack(">q", data[:8])[0]
        return cls(value)
