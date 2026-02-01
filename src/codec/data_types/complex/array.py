# src/codec/data_types/complex/array.py

from dataclasses import dataclass
from typing import Generic, TypeVar, List
from ..data_type import DataType

X = TypeVar("X")


@dataclass(slots=True, frozen=True)
class Array(Generic[X], DataType):
    """
    Represents an array of X with no length prefix.

    The number of elements MUST be known from the context.
    """

    values: List[X]

    def __bytes__(self) -> bytes:
        return b"".join(bytes(v) for v in self.values)

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        element_type: type[X],
        length: int,
    ) -> "Array[X]":
        """
        Deserialize exactly `count` elements of type X.

        Args:
            data (bytes): Byte buffer.
            count (int): Number of elements to read.

        Returns:
            Array[X]: Array instance.
        """
        elements: List[X] = []
        offset = 0

        for _ in range(length):
            element = element_type.from_bytes(data[offset:])
            elements.append(element)
            offset += len(bytes(element))

        return cls(elements)
