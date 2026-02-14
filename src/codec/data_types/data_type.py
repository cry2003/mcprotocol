# src\codec\data_types\data_type.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Tuple


T = TypeVar("T", bound="DataType")


class DataType(ABC):
    """
    Base class for all Minecraft protocol data types.

    Every data type must:
    - implement __bytes__ for serialization
    - implement from_bytes for deserialization
    - be immutable once constructed (recommended)
    """

    __slots__ = ()

    @abstractmethod
    def __bytes__(self) -> bytes:
        """
        Serialize the data type to bytes according to the protocol.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_bytes(cls: type[T], data: bytes) -> Tuple[T, int]:
        """
        Deserialize the data type from bytes.

        Args:
            data: Raw byte buffer starting at this data type.

        Returns:
            A tuple of (instance, bytes_consumed).
        
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """
        Human-readable representation for debugging.
        """
        attrs = (
            f"{name}={getattr(self, name)!r}"
            for name in getattr(self, "__slots__", ())
            if not name.startswith("_")
        )
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def __repr__(self) -> str:
        return str(self)
