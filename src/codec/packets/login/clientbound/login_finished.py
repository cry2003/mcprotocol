# src/codec/packets/login/clientbound/login_finished.py

from codec.packets.packet import Packet
from codec.data_types.complex.game_profile import GameProfile
from codec.data_types.primitives.varint import VarInt


class LoginFinished(Packet):
    """
    Login Finished packet (clientbound).

    Packet ID:
        0x02
    State:
        Login
    Bound:
        Clientbound

    Fields:
        profile (GameProfile): Game profile of the player.
    """

    __slots__ = ("profile",)

    def __init__(self, data: bytes) -> None:
        """Deserialize LoginFinished packet.

        Args:
            data (bytes): Packet payload excluding length and packet ID.
        """
        super().__init__(packet_id=VarInt(0x02))

        # Deserialize the GameProfile from bytes
        self.profile = GameProfile.from_bytes(data)

    def _iter_fields(self):
        """Yield serialized fields in protocol order."""
        yield self.profile
