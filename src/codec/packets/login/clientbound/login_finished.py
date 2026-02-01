from codec.packets.packet import Packet
from codec.data_types.complex.game_profile import GameProfile
from codec.data_types.primitives.varint import VarInt


class LoginFinished(Packet):
    """
    Login Finished packet.

    Packet ID:
        0x02
    State:
        Login
    Bound:
        Client

    Fields:
        profile (GameProfile): Game profile of the player.
    """

    __slots__ = ("profile",)

    def __init__(self, profile: GameProfile) -> None:
        super().__init__(packet_id=VarInt(0x02))

        # Type validation for profile
        if not isinstance(profile, GameProfile):
            raise TypeError("profile must be an instance of GameProfile")

        self.profile = profile

    def _iter_fields(self):
        yield self.profile
