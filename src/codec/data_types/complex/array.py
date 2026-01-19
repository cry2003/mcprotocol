# src/codec/data_types/complex/array.py

from dataclasses import dataclass
from typing import Type, List, Tuple


@dataclass(slots=True, frozen=True)
class Array:
    """Represents an array of elements of a specified primitive type in Minecraft protocol.

    Encoding:
        - Consecutive serialization of `length` elements.
        - Each element is encoded using its own `__bytes__()` method.
        - Total length in bytes = length * size_of_each_element (may vary for variable-length types).

    Attributes:
        elements (List): List of instances of the specified primitive type.
        element_type (Type): Primitive type of the elements. Must implement `__bytes__` and `from_bytes`.

    Serialization:
        - `__bytes__()` serializes all elements consecutively.
        - `from_bytes(data, offset=0, length)` deserializes a fixed number of elements from a buffer.

    Validation:
        - Ensures all items in `elements` are instances of `element_type`.
        - Raises ValueError if deserialization buffer is too short.
    """

    elements: List
    element_type: Type

    def __post_init__(self) -> None:
        """Validate that all elements are instances of the specified type."""
        for el in self.elements:
            if not isinstance(el, self.element_type):
                raise ValueError(
                    f"All elements must be of type {self.element_type.__name__}"
                )

    def __bytes__(self) -> bytes:
        """Serialize all elements consecutively.

        Returns:
            bytes: Concatenation of all element bytes.
        """
        result = bytearray()
        for el in self.elements:
            result.extend(bytes(el))
        return bytes(result)

    @classmethod
    def from_bytes(
        cls, data: bytes, offset: int = 0, length: int = 0
    ) -> Tuple["Array", int]:
        """Deserialize a fixed-length array of elements from a buffer.

        Args:
            data (bytes): Byte buffer containing the elements.
            offset (int): Start index in buffer.
            length (int): Number of elements to read.

        Returns:
            Tuple[Array, int]: Array instance and total bytes consumed.

        Raises:
            ValueError: If the buffer does not contain enough bytes for all elements.
        """
        if length == 0:
            return cls([], cls.element_type), 0

        elements = []
        total_consumed = 0
        for _ in range(length):
            el, consumed = cls.element_type.from_bytes(data, offset + total_consumed)
            elements.append(el)
            total_consumed += consumed

        return cls(elements, cls.element_type), total_consumed
