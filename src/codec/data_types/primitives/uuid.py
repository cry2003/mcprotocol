# src/codec/data_types/primitives/uuid.py

from dataclasses import dataclass
from uuid import UUID as PyUUID
from typing import Union
from ..data_type import DataType


@dataclass(slots=True, frozen=True)
class UUID(DataType):
    """Represents a 128-bit UUID in Minecraft protocol format.

    Encoding:
        - 16 bytes in big-endian order:
            - First 8 bytes: Most Significant Bits (MSB)
            - Last 8 bytes: Least Significant Bits (LSB)

    Attributes:
        value (PyUUID): The UUID object.

    Serialization:
        - `__bytes__()` returns the 16-byte network-ready UUID.
        - `from_bytes(buf)` decodes UUID from buffer.

    Validation:
        - Ensures `value` is a valid PyUUID instance.
        - Raises ValueError if the buffer is too short for decoding.
    """

    value: PyUUID

    def __post_init__(self) -> None:
        """Ensure that the UUID is a PyUUID instance."""
        object.__setattr__(
            self,
            "value",
            self.value if isinstance(self.value, PyUUID) else PyUUID(str(self.value)),
        )

    @property
    def msb(self) -> int:
        """Return the most significant 64 bits of the UUID as an unsigned integer."""
        return int.from_bytes(self.value.bytes[:8], byteorder="big", signed=False)

    @property
    def lsb(self) -> int:
        """Return the least significant 64 bits of the UUID as an unsigned integer."""
        return int.from_bytes(self.value.bytes[8:], byteorder="big", signed=False)

    def __bytes__(self) -> bytes:
        """Return the 16-byte big-endian representation of the UUID."""
        return self.value.bytes

    @classmethod
    def from_bytes(
        cls, buf: Union[bytes, memoryview]
    ) -> "UUID":
        """Deserialize a UUID from a byte buffer.

        Args:
            buf (bytes | memoryview): Buffer containing at least 16 bytes.

        Returns:
            UUID: Decoded UUID instance.

        Raises:
            ValueError: If there are fewer than 16 bytes in the buffer.
        """
        if len(buf) < 16:
            raise ValueError(
                f"Buffer too small to decode UUID: need 16 bytes"
            )
        raw = bytes(buf[:16])
        return cls(PyUUID(bytes=raw))
