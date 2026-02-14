# src/codec/packets/configuration/clientbound/ping.py

from codec.packets.packet import Packet
from codec.data_types.primitives.int import Int
from codec.data_types.primitives.varint import VarInt


class Ping(Packet):
    """
    Configuration Ping packet.

    Packet ID:
        0x05
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        ping_id (Int): Ping identifier echoed back by clientbound pong.
    """

    __slots__ = ("ping_id",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x05))

        self.ping_id, consumed = Int.from_bytes(data)
        if consumed != len(data):
            raise ValueError(f"Ping has unexpected trailing bytes: {len(data) - consumed}")

    def _iter_fields(self):
        yield self.ping_id
