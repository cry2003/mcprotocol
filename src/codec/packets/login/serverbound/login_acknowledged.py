# src/codec/packets/login/serverbound/login_acknowledged.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt


class LoginAcknowledged(Packet):
    """
    Login Acknowledged packet.

    Packet ID:
        0x03
    State:
        Login
    Bound:
        Serverbound

    Fields:
        None

    Notes:
        This packet signals that the login process has completed successfully
        and the connection state should switch to configuration/play.
    """

    __slots__ = ()

    def __init__(self, data: bytes) -> None:
        """Initialize LoginAcknowledged packet."""
        super().__init__(packet_id=VarInt(0x03))

        if data:
            raise ValueError(
                f"LoginAcknowledged has no fields, got {len(data)} trailing bytes"
            )

    def _iter_fields(self):
        """Iterate over packet fields (none for this packet)."""
        return
        yield  # empty generator to satisfy iterable interface
