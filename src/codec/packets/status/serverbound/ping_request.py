# src/codec/packets/status/serverbound/ping_request.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.long import Long


class PingRequest(Packet):
    """
    Ping Request packet.

    Packet ID: 
        0x01
    State: 
        Status
    Bound to:
        serverbound

    Fields:
        timestamp (Long): Client timestamp, usually in milliseconds.
    """

    __slots__ = ("timestamp",)

    def __init__(self, timestamp: int) -> None:
        super().__init__(packet_id=VarInt(0x01))
        self.timestamp = Long(timestamp)

    def _iter_fields(self):
        """
        Yield packet fields in wire order.

        Yields:
            Long: Timestamp field.
        """
        yield self.timestamp
