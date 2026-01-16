# src/codec/packets/status/clientbound/pong_response.py

from codec.packets.packet import Packet
from codec.data_types.primitives.long import Long
from codec.data_types.primitives.varint import VarInt


class PongResponse(Packet):
    """
    Pong Response packet (clientbound).

    Packet ID: 0x01
    State: Status
    Bound to: Client

    Contains the timestamp payload sent by the client in Ping Request.
    """

    __slots__ = ("timestamp",)

    def __init__(self, data: bytes | int) -> None:
        """
        Initialize PongResponse.

        Args:
            data (bytes | int): Raw packet data from server or a direct timestamp.
        """
        super().__init__(VarInt(0x01))

        if isinstance(data, bytes):
            self.timestamp = Long.from_bytes(data).value
        else:
            self.timestamp = int(data)

    def _iter_fields(self):
        """Yield the timestamp as a Long field for serialization."""
        yield Long(self.timestamp)
