# src/codec/packets/login/serverbound/login_acknowledged.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from network.packet_io import PacketIO


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

    def __init__(self, packet_io: PacketIO) -> None:
        """Initialize LoginAcknowledged packet."""
        super().__init__(packet_id=VarInt(0x03))

        packet_io.set_state("Configuration")

    def _iter_fields(self):
        """Iterate over packet fields (none for this packet)."""
        return
        yield  # empty generator to satisfy iterable interface
