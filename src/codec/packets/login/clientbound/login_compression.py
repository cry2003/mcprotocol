# src/codec/packets/login/clientbound/login_compression.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.packets.constants import _MAX_PACKET_LENGTH


class LoginCompression(Packet):
    """Set Compression packet.

    Packet ID:
        0x03
    State:
        Login
    Bound:
        Clientbound (Server -> Client)

    Fields:
        threshold (VarInt):
            Compression threshold.
            - threshold >= 0 enables compression
            - threshold < 0 disables compression
    """

    __slots__ = ("threshold",)



    def __init__(self, data: bytes) -> None:
        """Deserialize Set Compression packet.

        Args:
            data (bytes): Packet payload excluding packet length and packet ID.

        Raises:
            ValueError: If the compression threshold exceeds protocol limits.
        """
        super().__init__(packet_id=VarInt(0x03))

        self.threshold, _ = VarInt.from_bytes(data)
        value = self.threshold.value

        # Negative values are allowed and disable compression
        # Zero is allowed and enables compression with no packets compressed
        if value > _MAX_PACKET_LENGTH:
            raise ValueError(
                f"Invalid compression threshold {value}: "
                f"exceeds maximum packet size ({_MAX_PACKET_LENGTH})"
            )

    def _iter_fields(self):
        """Iterate over packet fields in serialization order."""
        yield self.threshold
