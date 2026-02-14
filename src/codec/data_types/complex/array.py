# src/codec/data_types/complex/array.py

from dataclasses import dataclass
from typing import Type, List
from ..data_type import DataType


@dataclass(slots=True, frozen=True)
class Array(DataType):
    """Represents an array of elements with no length prefix.

    The number of elements MUST be known from the context.

    Attributes:
        values (list[DataType]): List of array elements.

    Serialization:
        - `__bytes__()` concatenates the serialized bytes of all elements.

    Deserialization:
        - `from_bytes(data, length, element_type)` reads exactly `length` elements
          of type `element_type` sequentially from the buffer.
    """

    values: List[DataType]

    def __bytes__(self) -> bytes:
        """Serialize the array by concatenating serialized elements.

        Returns:
            bytes: Serialized elements concatenated.
        """
        return b"".join(bytes(v) for v in self.values)

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        length: int,
        element_type: Type[DataType],
    ) -> tuple["Array", int]:
        """Deserialize exactly `length` elements of type `element_type`.

        Args:
            data (bytes): Byte buffer.
            length (int): Number of elements to read.
            element_type (Type[DataType]): Type used to deserialize each element.

        Returns:
            Array: Deserialized array instance.
        """
        elements: List[DataType] = []
        offset = 0

        for _ in range(length):
            element, consumed = element_type.from_bytes(data[offset:])
            elements.append(element)
            offset += consumed

        return cls(elements), offset
