# src/codec/packets/configuration/clientbound/transfer.py

from codec.packets.packet import Packet
from codec.data_types.primitives.string import String
from codec.data_types.primitives.varint import VarInt


class Transfer(Packet):
    """
    Configuration Transfer packet.

    Packet ID:
        0x0B
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        host (String): Hostname or IP of the destination server.
        port (VarInt): Port of the destination server.
    """

    __slots__ = ("host", "port")

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x0B))
        offset = 0

        self.host, consumed = String.from_bytes(data[offset:])
        offset += consumed

        self.port, consumed = VarInt.from_bytes(data[offset:])
        offset += consumed

        if not (0 <= self.port.value <= 65535):
            raise ValueError(
                f"Transfer port out of range: {self.port.value} (expected 0..65535)"
            )

        if offset != len(data):
            raise ValueError(
                f"Transfer has unexpected trailing bytes: {len(data) - offset}"
            )

    def _iter_fields(self):
        yield self.host
        yield self.port
