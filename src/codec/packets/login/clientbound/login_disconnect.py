# src/codec/packets/login/clientbound/login_disconnect.py

from codec.packets.packet import Packet
from codec.data_types.complex.json_text_component import JsonTextComponent
from codec.data_types.primitives.varint import VarInt


class LoginDisconnect(Packet):
    """
    Login Disconnect packet (clientbound).

    Packet ID:
        0x00
    State:
        Login
    Bound:
        Clientbound

    Fields:
        reason (JsonTextComponent): The JSON-formatted reason why the player was disconnected.
    """

    __slots__ = ("reason",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x00))

        # JSON Text Component
        self.reason = JsonTextComponent.from_bytes(data)

    def _iter_fields(self):
        # Serialization order must match protocol specification
        yield self.reason
