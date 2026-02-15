# src/codec/data_types/special/known_pack.py

from dataclasses import dataclass

from codec.data_types.data_type import DataType
from codec.data_types.primitives.string import String


@dataclass(slots=True, frozen=True)
class KnownPack(DataType):
    """
    One known pack entry used in known packs negotiation.

    Fields:
        namespace (String): Namespace part, e.g. "minecraft".
        pack_id (String): Path/id part, e.g. "core".
        version (String): Pack version string.
    """

    namespace: String
    pack_id: String
    version: String

    def __post_init__(self) -> None:
        if not isinstance(self.namespace, String):
            raise TypeError("KnownPack.namespace must be a String")
        if not isinstance(self.pack_id, String):
            raise TypeError("KnownPack.pack_id must be a String")
        if not isinstance(self.version, String):
            raise TypeError("KnownPack.version must be a String")

    def __bytes__(self) -> bytes:
        return bytes(self.namespace) + bytes(self.pack_id) + bytes(self.version)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["KnownPack", int]:
        offset = 0

        namespace, consumed = String.from_bytes(data[offset:])
        offset += consumed

        pack_id, consumed = String.from_bytes(data[offset:])
        offset += consumed

        version, consumed = String.from_bytes(data[offset:])
        offset += consumed

        return cls(namespace=namespace, pack_id=pack_id, version=version), offset
