# src/codec/packets/configuration/clientbound/select_known_packs.py

from codec.packets.packet import Packet
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.varint import VarInt
from codec.data_types.special.known_pack import KnownPack


class SelectKnownPacks(Packet):
    """
    Configuration Clientbound Known Packs packet.

    Packet ID:
        0x0E
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        known_packs (PrefixedArray[KnownPack]): Packs listed by the server.
    """

    __slots__ = ("known_packs",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x0E))

        self.known_packs, consumed = PrefixedArray.from_bytes(data, KnownPack)

        seen: set[tuple[str, str, str]] = set()
        for pack in self.known_packs.values:
            key = (pack.namespace.value, pack.pack_id.value, pack.version.value)
            if key in seen:
                raise ValueError(
                    "SelectKnownPacks contains duplicate pack entry: "
                    f"{pack.namespace.value}:{pack.pack_id.value}@{pack.version.value}"
                )
            seen.add(key)

        if consumed != len(data):
            raise ValueError(
                f"SelectKnownPacks has unexpected trailing bytes: {len(data) - consumed}"
            )

    def _iter_fields(self):
        yield self.known_packs
