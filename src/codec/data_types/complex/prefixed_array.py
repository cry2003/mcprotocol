# src/codec/data_types/complex/prefixed_array.py

from dataclasses import dataclass
from typing import Type, List

from codec.data_types.primitives.varint import VarInt
from codec.data_types.complex.array import Array
from ..data_type import DataType


@dataclass(slots=True, frozen=True)
class PrefixedArray(DataType):
    """Represents a length-prefixed array in the Minecraft protocol.

    Encoding:
        - The array is prefixed with its length encoded as a VarInt.
        - Followed by `length` consecutive elements of the same type.

    Layout:
        Length (VarInt)
        Data   (Array of elements)

    Attributes:
        values (list[DataType]): List of deserialized elements.

    Serialization:
        - `__bytes__()` encodes the array length as VarInt,
          followed by the serialized bytes of each element.

    Deserialization:
        - `from_bytes(data, element_type)` reads:
            1. The VarInt length prefix.
            2. Exactly `length` elements of type `element_type`.
        - The number of elements is determined exclusively by the length prefix.

    Validation:
        - Raises exceptions if the buffer does not contain enough bytes
          to deserialize all elements.
        - Ensures protocol-compliant, sequential decoding.
    """

    values: List[DataType]

    def __bytes__(self) -> bytes:
        """Serialize the prefixed array.

        Returns:
            bytes: VarInt length prefix followed by serialized elements.
        """
        length = VarInt(len(self.values))
        return bytes(length) + bytes(Array(self.values))

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        element_type: Type[DataType],
    ) -> "PrefixedArray":
        """Deserialize a length-prefixed array from a byte buffer.

        Args:
            data (bytes): Byte buffer containing the prefixed array.
            element_type (Type[DataType]): Type used to deserialize each element.

        Returns:
            PrefixedArray: Deserialized array instance.
        """
        length = VarInt.from_bytes(data)
        offset = len(bytes(length))

        array = Array.from_bytes(
            data=data[offset:], length=length.value, element_type=element_type
        )

        return cls(array.values)
