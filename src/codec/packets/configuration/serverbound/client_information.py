# src/codec/packets/configuration/serverbound/client_information.py

from codec.packets.packet import Packet
from codec.data_types.primitives.boolean import Boolean
from codec.data_types.primitives.byte import Byte
from codec.data_types.primitives.string import String
from codec.data_types.primitives.varint import VarInt


class ClientInformation(Packet):
    """
    Configuration Client Information packet.

    Packet ID:
        0x00
    State:
        Configuration
    Bound:
        Serverbound

    Fields:
        locale (String): Client locale, max 16 characters (example: en_GB).
        view_distance (Byte): Client-side render distance in chunks.
        chat_mode (VarInt): 0=enabled, 1=commands only, 2=hidden.
        chat_colors (Boolean): Chat colors setting.
        displayed_skin_parts (unsigned byte): Skin-part bitmask.
        main_hand (VarInt): 0=left, 1=right.
        enable_text_filtering (Boolean): Profanity filtering preference.
        allow_server_listings (Boolean): Allow appearing in server listings.
        particle_status (VarInt): 0=all, 1=decreased, 2=minimal.
    """

    __slots__ = (
        "locale",
        "view_distance",
        "chat_mode",
        "chat_colors",
        "displayed_skin_parts",
        "main_hand",
        "enable_text_filtering",
        "allow_server_listings",
        "particle_status",
    )

    def __init__(
        self,
        locale: str,
        view_distance: int,
        chat_mode: int,
        chat_colors: bool,
        displayed_skin_parts: int,
        main_hand: int,
        enable_text_filtering: bool,
        allow_server_listings: bool,
        particle_status: int,
    ) -> None:
        super().__init__(packet_id=VarInt(0x00))

        if len(locale) > 16:
            raise ValueError(f"Locale too long: {len(locale)} (max 16)")
        self.locale = String(locale)

        self.view_distance = Byte(view_distance)

        if chat_mode not in (0, 1, 2):
            raise ValueError(f"Invalid chat_mode: {chat_mode} (expected 0, 1, or 2)")
        self.chat_mode = VarInt(chat_mode)

        self.chat_colors = Boolean(chat_colors)

        if not (0 <= displayed_skin_parts <= 0xFF):
            raise ValueError(
                "displayed_skin_parts out of range: "
                f"{displayed_skin_parts} (expected 0..255)"
            )
        self.displayed_skin_parts = displayed_skin_parts

        if main_hand not in (0, 1):
            raise ValueError(f"Invalid main_hand: {main_hand} (expected 0 or 1)")
        self.main_hand = VarInt(main_hand)

        self.enable_text_filtering = Boolean(enable_text_filtering)
        self.allow_server_listings = Boolean(allow_server_listings)

        if particle_status not in (0, 1, 2):
            raise ValueError(
                f"Invalid particle_status: {particle_status} (expected 0, 1, or 2)"
            )
        self.particle_status = VarInt(particle_status)

    def _iter_fields(self):
        yield self.locale
        yield self.view_distance
        yield self.chat_mode
        yield self.chat_colors
        yield self.displayed_skin_parts.to_bytes(1, byteorder="big", signed=False)
        yield self.main_hand
        yield self.enable_text_filtering
        yield self.allow_server_listings
        yield self.particle_status
