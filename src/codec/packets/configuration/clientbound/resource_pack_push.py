# src/codec/packets/configuration/clientbound/resource_pack_push.py

import re

from codec.packets.packet import Packet
from codec.data_types.complex.prefixed_optional import PrefixedOptional
from codec.data_types.complex.text_component import TextComponent
from codec.data_types.primitives.boolean import Boolean
from codec.data_types.primitives.string import String
from codec.data_types.primitives.uuid import UUID
from codec.data_types.primitives.varint import VarInt


_SHA1_HEX_40_RE = re.compile(r"^[0-9a-fA-F]{40}$")


class ResourcePackPush(Packet):
    """
    Configuration Add Resource Pack packet.

    Packet ID:
        0x09
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        uuid (UUID): Unique identifier for the resource pack.
        url (String): Resource pack URL.
        hash (String): 40-character SHA-1 hex hash.
        forced (Boolean): Whether accepting the pack is mandatory.
        prompt_message (PrefixedOptional[TextComponent]): Optional prompt text.
    """

    __slots__ = ("uuid", "url", "hash", "forced", "prompt_message")

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x09))
        offset = 0

        self.uuid, consumed = UUID.from_bytes(data[offset:])
        offset += consumed

        self.url, consumed = String.from_bytes(data[offset:])
        offset += consumed

        self.hash, consumed = String.from_bytes(data[offset:])
        offset += consumed
        if not _SHA1_HEX_40_RE.fullmatch(self.hash.value):
            raise ValueError(
                "ResourcePackPush hash must be a 40-character hexadecimal SHA-1 string"
            )

        self.forced, consumed = Boolean.from_bytes(data[offset:])
        offset += consumed

        self.prompt_message, consumed = PrefixedOptional.from_bytes(
            data[offset:], TextComponent
        )
        offset += consumed

        if offset != len(data):
            raise ValueError(
                f"ResourcePackPush has unexpected trailing bytes: {len(data) - offset}"
            )

    def _iter_fields(self):
        yield self.uuid
        yield self.url
        yield self.hash
        yield self.forced
        yield self.prompt_message
