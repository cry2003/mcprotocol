# src/codec/packets/configuration/clientbound/custom_payload.py

from codec.packets.constants import _MAX_PAYLOAD_LENGTH
from codec.packets.packet import Packet
from codec.data_types.complex.identifier import Identifier
from codec.data_types.primitives.varint import VarInt


class CustomPayload(Packet):
    """
    Configuration Custom Payload packet.

    Packet ID:
        0x01
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        channel (Identifier): Name of the plugin channel used to send the data.
        data (bytes): Channel-specific payload. Format depends on the channel.
                      No global length prefix is applied.
                      The vanilla client enforces a 1048576 byte limit
                      if the channel is unrecognized.
    """

    __slots__ = ("channel", "data")


    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x01))
        offset = 0

        # Parse channel identifier
        self.channel, consumed = Identifier.from_bytes(data[offset:])
        offset += consumed

        # Remaining bytes are channel-specific payload
        self.data = data[offset:]

        if not isinstance(self.data, (bytes, bytearray)):
            raise TypeError("CustomPayload data must be bytes")

        # Vanilla-enforced limit for unrecognized channels
        if len(self.data) > _MAX_PAYLOAD_LENGTH:
            raise ValueError(
                f"CustomPayload data too long: {len(self.data)} bytes "
                f"(max {_MAX_PAYLOAD_LENGTH})"
            )

    def _iter_fields(self):
        """Returns an iterator over the packet's fields."""
        yield self.channel
        yield self.data
