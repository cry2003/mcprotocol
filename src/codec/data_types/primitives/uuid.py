# src/codec/data_types/primitives/uuid.py

from dataclasses import dataclass
from uuid import UUID as PyUUID
from typing import Union, Tuple


@dataclass(slots=True, frozen=True)
class UUID:
    """Represents a UUID in the Minecraft protocol.

    Encoded as 16 bytes (128-bit) in big-endian order:
        - First 8 bytes: Most significant bits (MSB)
        - Last 8 bytes: Least significant bits (LSB)

    Attributes:
        value (PyUUID): The UUID value.
    """

    value: PyUUID

    def __post_init__(self) -> None:
        """Ensure that the UUID is a PyUUID instance.

        Raises:
            ValueError: If the provided value is not a valid UUID string or PyUUID.
        """
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
        """Return the 16-byte big-endian representation of the UUID.

        Returns:
            bytes: 16-byte UUID ready for network transmission.
        """
        return self.value.bytes

    @classmethod
    def decode(
        cls, buf: Union[bytes, memoryview], offset: int = 0
    ) -> Tuple["UUID", int]:
        """Decode a UUID from a 16-byte buffer.

        Args:
            buf (bytes | memoryview): Buffer containing the UUID.
            offset (int, optional): Start position in buffer. Defaults to 0.

        Returns:
            Tuple[UUID, int]: Decoded UUID instance and number of bytes consumed (16).

        Raises:
            ValueError: If there are fewer than 16 bytes available from the offset.
        """
        if len(buf) - offset < 16:
            raise ValueError(
                f"Buffer too small to decode UUID: need 16 bytes from offset {offset}"
            )
        raw = bytes(buf[offset : offset + 16])
        return cls(PyUUID(bytes=raw)), 16
