# src/codec/data_types/complex/prefixed_array.py

from dataclasses import dataclass
from typing import Generic, TypeVar

from codec.data_types.primitives.varint import VarInt
from codec.data_types.complex.array import Array

X = TypeVar("X")


@dataclass(slots=True, frozen=True)
class PrefixedArray(Generic[X]):
    """Represents a length-prefixed array in the Minecraft protocol.

    Encoding:
        - The array is prefixed with its length encoded as a VarInt.
        - Followed by `length` consecutive elements of type X.
        - All elements MUST be of the same type.

    Layout:
        Length (VarInt)
        Data   (Array of X)

    Attributes:
        values (list[X]): List of deserialized elements.

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

    values: list[X]

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
        element_type: type[X],
    ) -> "PrefixedArray[X]":
        """Deserialize a length-prefixed array from a byte buffer.

        Args:
            data (bytes): Byte buffer containing the prefixed array.
            element_type (type[X]): Type used to deserialize each element.

        Returns:
            PrefixedArray[X]: Deserialized array instance.
        """
        length = VarInt.from_bytes(data)
        offset = len(bytes(length))

        array = Array.from_bytes(
            data=data[offset:],
            element_type=element_type,
            length=length.value,
        )

        return cls(array.values)
