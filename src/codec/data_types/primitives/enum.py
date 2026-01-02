# src/codec/data_types/primitives/enum.py

from dataclasses import dataclass
from typing import Type


@dataclass(slots=True, frozen=True)
class Enum:
    """Represents a protocol enum encoded as a specific primitive type.

    Encoding:
        - The enum value is encoded using the specified base type (e.g., VarInt, UnsignedShort).
        - No caching; bytes are computed on demand.

    Attributes:
        value (int): The integer value of the enum.
        base_type (Type): The primitive type used for encoding (must support __bytes__).
    """

    value: int
    base_type: Type

    def __bytes__(self) -> bytes:
        """Encode the enum value using the specified base type.

        Returns:
            bytes: The encoded bytes of the enum.
        """
        return bytes(self.base_type(self.value))
