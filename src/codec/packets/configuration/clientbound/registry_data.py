# src/codec/packets/configuration/clientbound/registry_data.py

from codec.data_types.complex.identifier import Identifier
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.complex.registry_entry import RegistryEntry
from codec.data_types.primitives.varint import VarInt
from codec.packets.packet import Packet


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
