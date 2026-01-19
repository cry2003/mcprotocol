# src/codec/data_types/complex/array.py

from dataclasses import dataclass
from typing import Type, List, Tuple
from ..primitives.varint import VarInt


@dataclass(slots=True, frozen=True)
class PrefixedArray:
    """Represents a length-prefixed array of elements in Minecraft protocol.

    Encoding:
        - VarInt length prefix
        - Consecutive serialization of elements
        - Total size = size of VarInt + sum of element sizes

    Attributes:
        elements (List): List of elements of the specified type.
        element_type (Type): Primitive type of the elements. Must implement `__bytes__` and `from_bytes`.

    Serialization:
        - __bytes__() returns VarInt length + bytes of all elements.
        - from_bytes(data, offset=0) reads VarInt length and then elements.

    Validation:
        - Ensures all elements are of the specified type.
        - Raises ValueError if buffer too short.
    """

    elements: List
    element_type: Type

    def __post_init__(self):
        for el in self.elements:
            if not isinstance(el, self.element_type):
                raise ValueError(
                    f"All elements must be of type {self.element_type.__name__}"
                )

    def __bytes__(self) -> bytes:
        length_bytes = bytes(VarInt(len(self.elements)))
        result = bytearray(length_bytes)
        for el in self.elements:
            result.extend(bytes(el))
        return bytes(result)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> Tuple["PrefixedArray", int]:
        length_varint, varint_size = VarInt.from_bytes(data, offset)
        length = length_varint.value
        elements = []
        total_consumed = varint_size

        for _ in range(length):
            el, consumed = cls.element_type.from_bytes(data, offset + total_consumed)
            elements.append(el)
            total_consumed += consumed

        return cls(elements, cls.element_type), total_consumed
