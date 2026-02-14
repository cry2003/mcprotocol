# src/codec/packets/configuration/clientbound/reset_chat.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt


class ResetChat(Packet):
    """
    Configuration Reset Chat packet.

    Packet ID:
        0x06
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        None
    """

    __slots__ = ()

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x06))
        if data:
            raise ValueError(f"ResetChat has no fields, got {len(data)} trailing bytes")

    def _iter_fields(self):
        return iter(())
