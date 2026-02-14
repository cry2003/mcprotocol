# src/codec/packets/configuration/clientbound/disconnect.py

from codec.packets.packet import Packet
from codec.data_types.complex.text_component import TextComponent
from codec.data_types.primitives.varint import VarInt


class Disconnect(Packet):
    """
    Configuration Disconnect packet.

    Packet ID:
        0x02
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        reason (TextComponent): The reason why the player was disconnected.
    """

    __slots__ = ("reason",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x02))

        # Deserialize reason using the new from_bytes API
        self.reason, _ = TextComponent.from_bytes(data)
        # `consumed` can be used if further parsing is needed

    def _iter_fields(self):
        yield self.reason
