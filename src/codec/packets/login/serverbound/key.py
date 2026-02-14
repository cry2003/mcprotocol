# src/codec/packets/login/serverbound/key.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.byte import Byte
from codec.data_types.complex.prefixed_array import PrefixedArray


class Key(Packet):
    """Login Encryption Request packet.

    Packet ID:
        0x01
    State:
        Login
    Bound:
        Serverbound

    Fields:
        shared_secret (PrefixedArray[Byte]): Server shared secret encrypted with public key.
        verify_token (PrefixedArray[Byte]): Verify token encrypted with the same public key as the shared secret.
    """

    __slots__ = ("shared_secret", "verify_token")

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x01))
        offset = 0

        # Parse shared_secret
        self.shared_secret, consumed = PrefixedArray.from_bytes(
            data[offset:], element_type=Byte
        )
        offset += consumed

        # Parse verify_token
        self.verify_token, consumed = PrefixedArray.from_bytes(
            data[offset:], element_type=Byte
        )
        offset += consumed

    def _iter_fields(self):
        """Returns an iterator over the packet's fields."""
        yield self.shared_secret
        yield self.verify_token
