# src/codec/packets/login/serverbound/cookie_response.py

from codec.packets.packet import Packet
from codec.data_types.complex.identifier import Identifier
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.byte import Byte
from codec.data_types.primitives.varint import VarInt


class CookieResponse(Packet):
    """
    Login Cookie Response packet.

    Packet ID:
        0x04

    Fields:
        key (Identifier): The identifier of the cookie.
        payload (PrefixedArray[Byte], optional): The data of the cookie.
            Maximum length 5120 Bytes (5 KiB). Only present if the cookie has content.
    """

    __slots__ = ("key", "payload")

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x04))
        offset = 0

        # Parse key
        self.key, consumed = Identifier.from_bytes(data[offset:])
        offset += consumed

        # Remaining bytes are optional payload
        if offset < len(data):
            self.payload, _ = PrefixedArray.from_bytes(
                data[offset:], element_type=Byte
            )
            # Validate maximum length
            if len(self.payload.values) > 5120:
                raise ValueError(
                    f"CookieResponse payload too long: {len(self.payload.values)} bytes "
                    "(max 5120 Bytes)"
                )
        else:
            self.payload = None  # Optional, may be empty

    def _iter_fields(self):
        yield self.key
        if self.payload is not None:
            yield self.payload
