# src/codec/data_types/primitives/enum.py

from dataclasses import dataclass
from typing import Type
from ..data_type import DataType


@dataclass(slots=True, frozen=True)
class Enum(DataType):
    """Represents an enumerated value in Minecraft protocol format.

    Encoding:
        - Enum value is stored using a specified base type (e.g., VarInt, UnsignedShort).
        - `__bytes__()` encodes the integer value with the chosen primitive type.

    Attributes:
        value (int): The integer representing the enum.
        base_type (Type): Primitive type used for serialization. Must implement `__bytes__` and `from_bytes`.

    Serialization:
        - Delegates encoding and decoding to `base_type`.
        - Ensures consistent serialization across packets.
    """

    value: int
    base_type: Type

    def __bytes__(self) -> bytes:
        """Encode the enum value using the specified base type.

        Returns:
            bytes: The encoded bytes of the enum.
        """
        return bytes(self.base_type(self.value))

    @classmethod
    def from_bytes(cls, data: bytes) -> "Enum":
        """Deserialize an Enum from a byte buffer.

        Args:
            data (bytes): Byte buffer containing the enum.

        Returns:
            Enum: Enum instance.
        """
        base_instance = cls.base_type.from_bytes(data)
        return cls(base_instance.value, cls.base_type)
