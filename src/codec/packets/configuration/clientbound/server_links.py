# src/codec/packets/configuration/clientbound/server_links.py

from codec.packets.packet import Packet
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.varint import VarInt
from codec.data_types.special.server_link import ServerLink


class ServerLinks(Packet):
    """
    Configuration Server Links packet.

    Packet ID:
        0x10
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        links (PrefixedArray[ServerLink]): Links shown in the client menu.
    """

    __slots__ = ("links",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x10))

        self.links, consumed = PrefixedArray.from_bytes(data, ServerLink)

        seen_urls: set[str] = set()
        for link in self.links.values:
            if link.url.value in seen_urls:
                raise ValueError(f"ServerLinks contains duplicate URL: {link.url.value}")
            seen_urls.add(link.url.value)

        if consumed != len(data):
            raise ValueError(
                f"ServerLinks has unexpected trailing bytes: {len(data) - consumed}"
            )

    def _iter_fields(self):
        yield self.links
