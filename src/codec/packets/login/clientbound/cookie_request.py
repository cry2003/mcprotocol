# src/codec/packets/login/clientbound/cookie_request.py

from codec.packets.packet import Packet
from codec.data_types.complex.identifier import Identifier
from codec.data_types.primitives.varint import VarInt


class CookieRequest(Packet):
    """Login Cookie Request packet.

    Packet ID:
        0x05
    State:
        Login
    Bound:
        Clientbound

    Fields:
        key (Identifier): The identifier of the cookie being requested
    """

    __slots__ = ("key",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x05))
        # Deserialize the key
        self.key = Identifier.from_bytes(data)

    def _iter_fields(self):
        """Returns an iterator over the packet's fields."""
        yield self.key
