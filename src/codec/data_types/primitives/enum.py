# src/codec/data_types/primitives/enum.py

from dataclasses import dataclass
from typing import Type, Tuple


@dataclass(slots=True, frozen=True)
class Enum:
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
    def from_bytes(cls, data: bytes, offset: int = 0) -> Tuple["Enum", int]:
        """Deserialize an Enum from a byte buffer starting at `offset`.

        Args:
            data (bytes): Byte buffer containing the enum.
            offset (int, optional): Starting index. Defaults to 0.

        Returns:
            Tuple[Enum, int]: Enum instance and number of bytes consumed.
        """
        base_instance, consumed = cls.base_type.from_bytes(data, offset)
        return cls(base_instance.value, cls.base_type), consumed
