# src/codec/packets/configuration/clientbound/clear_dialog.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt


class ClearDialog(Packet):
    """
    Configuration Clear Dialog packet.

    Packet ID:
        0x11
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        None
    """

    __slots__ = ()

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x11))
        if data:
            raise ValueError(f"ClearDialog has no fields, got {len(data)} trailing bytes")

    def _iter_fields(self):
        return iter(())
