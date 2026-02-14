# src/codec/packets/configuration/clientbound/resource_pack_pop.py

from codec.packets.packet import Packet
from codec.data_types.complex.prefixed_optional import PrefixedOptional
from codec.data_types.primitives.uuid import UUID
from codec.data_types.primitives.varint import VarInt


class ResourcePackPop(Packet):
    """
    Configuration Remove Resource Pack packet.

    Packet ID:
        0x08
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        uuid (PrefixedOptional[UUID]): Resource pack UUID to remove.
            If absent, remove all resource packs.
    """

    __slots__ = ("uuid",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x08))

        self.uuid, consumed = PrefixedOptional.from_bytes(data, UUID)
        if consumed != len(data):
            raise ValueError(
                f"ResourcePackPop has unexpected trailing bytes: {len(data) - consumed}"
            )

    def _iter_fields(self):
        yield self.uuid
