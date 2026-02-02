# src/codec/packets/configuration/client/cookie_request.py

from codec.packets.packet import Packet
from codec.data_types.complex.identifier import Identifier
from codec.data_types.primitives.varint import VarInt


class CookieRequest(Packet):
    """
    Configuration Cookie Request packet.

    Packet ID:
        0x00

    Fields:
        key (Identifier): The identifier of the cookie being requested.
    """

    __slots__ = ("key",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x00))
        # Parse key
        self.key = Identifier.from_bytes(data)

    def _iter_fields(self):
        """Returns an iterator over the packet's fields."""
        yield self.key
