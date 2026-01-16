# src\codec\packets\status\serverbound\status_request.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt


class StatusRequest(Packet):
    """
    Status Request packet (serverbound).

    Packet ID: 0x00
    State: Status
    Bound to: Server

    This packet has no fields. It is sent immediately after the handshake
    to request the server status.
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(packet_id=VarInt(0x00))

    def _iter_fields(self):
        """No fields to serialize. Return empty generator for compatibility."""
        return iter(())
