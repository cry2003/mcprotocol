# src/codec/packets/login/clientbound/hello.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.string import String
from codec.data_types.primitives.byte import Byte
from codec.data_types.primitives.boolean import Boolean
from codec.data_types.complex.prefixed_array import PrefixedArray


class Hello(Packet):
    """Login Hello packet.

    Packet ID:
        0x01
    State:
        Login
    Bound:
        Clientbound

    Fields:
        server_id (String): Server ID (max 20 chars, empty for vanilla)
        public_key (PrefixedArray[Byte]): Server public key bytes
        verify_token (PrefixedArray[Byte]): Verification token bytes
        should_authenticate (Boolean): Whether Mojang authentication is required
    """

    __slots__ = (
        "server_id",
        "public_key",
        "verify_token",
        "should_authenticate",
    )

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x01))
        offset = 0

        # Parse server_id using existing String.from_bytes
        self.server_id, consumed = String.from_bytes(data[offset:])
        offset += consumed
        if len(self.server_id.value) > 20:
            raise ValueError("server_id exceeds maximum length of 20 characters")

        # Parse public_key
        self.public_key, consumed = PrefixedArray.from_bytes(
            data[offset:], element_type=Byte
        )
        offset += consumed

        # Parse verify_token
        self.verify_token, consumed = PrefixedArray.from_bytes(
            data[offset:], element_type=Byte
        )
        offset += consumed

        # Parse should_authenticate
        self.should_authenticate, consumed = Boolean.from_bytes(data[offset:])
        offset += consumed
        if offset != len(data):
            raise ValueError("Unexpected trailing bytes in Login Hello packet payload")

    def _iter_fields(self):
        yield self.server_id
        yield self.public_key
        yield self.verify_token
        yield self.should_authenticate
