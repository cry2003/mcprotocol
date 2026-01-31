# src/codec/packets/login/serverbound/hello.py

from codec.packets.packet import Packet
from codec.data_types.primitives.string import String
from codec.data_types.primitives.uuid import UUID
from codec.data_types.primitives.varint import VarInt
from uuid import UUID as PyUUID


class Hello(Packet):
    """
    Hello packet.

    Packet ID:
        0x00
    State:
        Login
    Bound:
        Serverbound

    Fields:
        name (String, max 16): Player's username.
        player_uuid (UUID, optional): Player's UUID. Unused by vanilla server.
    """

    __slots__ = ("name", "player_uuid")

    def __init__(self, name: str, player_uuid: PyUUID = None) -> None:
        super().__init__(packet_id=VarInt(0x00))

        if len(name) > 16:
            raise ValueError("Player name cannot exceed 16 characters")

        self.name = String(name)
        self.player_uuid = UUID(player_uuid)

    def _iter_fields(self):
        """Yield fields in order for serialization."""
        yield self.name
        if self.player_uuid is not None:
            yield self.player_uuid
