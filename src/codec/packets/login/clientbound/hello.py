# src/codec/packets/login/clientbound/hello.py

from typing import Iterable

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.string import String
from codec.data_types.primitives.byte import Byte
from codec.data_types.primitives.boolean import Boolean
from codec.data_types.complex.prefixed_array import PrefixedArray


class Hello(Packet):
    """Login Hello packet (clientbound).

    Packet ID:
        0x01
    State:
        Login
    Bound:
        Clientbound (Server -> Client)

    Fields:
        server_id (String): Server ID (max 20 characters, empty for vanilla).
        public_key (PrefixedArray[Byte]): Server public key bytes.
        verify_token (PrefixedArray[Byte]): Verification token bytes.
        should_authenticate (Boolean): Whether Mojang authentication is required.
    """

    __slots__ = (
        "server_id",
        "public_key",
        "verify_token",
        "should_authenticate",
    )

    def __init__(
        self,
        server_id: str,
        public_key: Iterable[int],
        verify_token: Iterable[int],
        should_authenticate: bool,
    ) -> None:
        super().__init__(packet_id=VarInt(0x01))

        self.server_id = String(server_id)

        self.public_key = PrefixedArray([Byte(b) for b in public_key])
        self.verify_token = PrefixedArray([Byte(b) for b in verify_token])

        self.should_authenticate = Boolean(should_authenticate)

    def _iter_fields(self):
        yield self.server_id
        yield self.public_key
        yield self.verify_token
        yield self.should_authenticate
