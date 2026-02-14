# src/codec/data_types/primitives/prefixed_optional.py

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar
from ..data_type import DataType
from ..primitives.boolean import Boolean

X = TypeVar("X", bound=DataType)


@dataclass(slots=True, frozen=True)
class PrefixedOptional(DataType, Generic[X]):
    """
    Represents a field of type T that is prefixed with a boolean indicating its presence.

    Serialization:
        - Boolean: 1 byte, True if value is present, False otherwise
        - If present, the value of type T is serialized immediately after
    """

    value: Optional[X]

    def __post_init__(self) -> None:
        if self.value is not None and not isinstance(self.value, DataType):
            raise TypeError(
                "PrefixedOptional value must be a DataType instance or None"
            )

    def __bytes__(self) -> bytes:
        """
        Serialize the PrefixedOptional field.
        Returns:
            bytes: Serialized byte sequence
        """
        if self.value is None:
            return bytes(Boolean(False))
        return bytes(Boolean(True)) + bytes(self.value)

    @classmethod
    def from_bytes(
        cls, data: bytes, type_cls: type[X]
    ) -> tuple["PrefixedOptional[X]", int]:
        """
        Deserialize a PrefixedOptional field.

        Args:
            data (bytes): Byte sequence
            type_cls (Type[DataType]): The class of the inner type T

        Returns:
            PrefixedOptional[X]
        """
        if not data:
            raise ValueError("No data to deserialize PrefixedOptional")

        # Read presence boolean
        presence, consumed = Boolean.from_bytes(data)
        present = presence.value
        if not present:
            return cls(value=None), consumed

        # Deserialize the inner type
        value, value_consumed = type_cls.from_bytes(data[consumed:])
        return cls(value=value), consumed + value_consumed
