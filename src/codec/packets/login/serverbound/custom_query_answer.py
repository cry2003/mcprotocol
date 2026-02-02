# src/codec/packets/login/serverbound/custom_query_answer.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt


class CustomQueryAnswer(Packet):
    """
    Login Custom Query Answer packet.

    Packet ID:
        0x02

    Fields:
        message_id (VarInt): Should match the ID from the server's custom query request.
        data (bytes): Optional payload, only present if the client understood the request.
                      Format depends on the channel. Max length 1048576 bytes.
    """

    __slots__ = ("message_id", "data")

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x02))
        offset = 0

        # Parse message_id
        self.message_id = VarInt.from_bytes(data[offset:])
        offset += len(bytes(self.message_id))

        # Validate message_id
        if self.message_id.value < 0:
            raise ValueError(f"Invalid message_id {self.message_id.value}")

        # The rest is optional data
        self.data = data[offset:]
        if not isinstance(self.data, (bytes, bytearray)):
            raise TypeError("CustomQueryAnswer data must be bytes")

        # Optional maximum length check
        if len(self.data) > 1048576:
            raise ValueError(
                f"CustomQueryAnswer data too long: {len(self.data)} bytes (max 1048576)"
            )

    def _iter_fields(self):
        """Returns an iterator over the packet's fields."""
        yield self.message_id
        yield self.data
