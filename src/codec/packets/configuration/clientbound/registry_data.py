# src/codec/packets/configuration/clientbound/registry_data.py

from dataclasses import dataclass
from typing import Optional

from codec.data_types.data_type import DataType
from codec.data_types.complex.identifier import Identifier
from codec.data_types.complex.nbt import TagCompound, dump_nbt
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.boolean import Boolean
from codec.data_types.primitives.varint import VarInt
from codec.packets.packet import Packet


@dataclass(slots=True, frozen=True)
class RegistryEntry(DataType):
    """
    One registry entry in Configuration Registry Data.

    Fields:
        entry_id (Identifier): Entry name (for example minecraft:overworld).
        data (Optional[TagCompound]): Optional NBT entry payload.
    """

    entry_id: Identifier
    data: Optional[TagCompound]

    def __post_init__(self) -> None:
        if not isinstance(self.entry_id, Identifier):
            raise TypeError("RegistryEntry.entry_id must be an Identifier")
        if self.data is not None and not isinstance(self.data, TagCompound):
            raise TypeError("RegistryEntry.data must be a TagCompound or None")

    def __bytes__(self) -> bytes:
        if self.data is None:
            return bytes(self.entry_id) + bytes(Boolean(False))
        return (
            bytes(self.entry_id)
            + bytes(Boolean(True))
            + dump_nbt(self.data, network=True)
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["RegistryEntry", int]:
        offset = 0

        entry_id, consumed = Identifier.from_bytes(data[offset:])
        offset += consumed

        present, consumed = Boolean.from_bytes(data[offset:])
        offset += consumed

        nbt_data: Optional[TagCompound]
        if present.value:
            nbt_data, consumed = TagCompound.from_bytes(
                data[offset:], network=True, is_root=True
            )
            offset += consumed
        else:
            nbt_data = None

        return cls(entry_id=entry_id, data=nbt_data), offset


class RegistryData(Packet):
    """
    Configuration Registry Data packet.

    Packet ID:
        0x07
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        registry_id (Identifier): Registry name (for example minecraft:dimension_type).
        entries (PrefixedArray[RegistryEntry]): Registry entry list in ID order.
    """

    __slots__ = ("registry_id", "entries")

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x07))
        offset = 0

        self.registry_id, consumed = Identifier.from_bytes(data[offset:])
        offset += consumed

        self.entries, consumed = PrefixedArray.from_bytes(data[offset:], RegistryEntry)
        offset += consumed

        if offset != len(data):
            raise ValueError(
                f"RegistryData has unexpected trailing bytes: {len(data) - offset}"
            )

    def _iter_fields(self):
        yield self.registry_id
        yield self.entries
