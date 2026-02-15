# src/codec/packets/configuration/clientbound/store_cookie.py

from codec.packets.packet import Packet
from codec.data_types.complex.identifier import Identifier
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.byte import Byte
from codec.data_types.primitives.varint import VarInt


class StoreCookie(Packet):
    """
    Configuration Store Cookie packet.

    Packet ID:
        0x0A
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        key (Identifier): The identifier of the cookie.
        payload (PrefixedArray[Byte]): Cookie data (max 5120 bytes).
    """

    __slots__ = ("key", "payload")

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x0A))
        offset = 0

        self.key, consumed = Identifier.from_bytes(data[offset:])
        offset += consumed

        self.payload, consumed = PrefixedArray.from_bytes(data[offset:], Byte)
        offset += consumed

        if len(self.payload.values) > 5120:
            raise ValueError(
                f"StoreCookie payload too long: {len(self.payload.values)} bytes "
                "(max 5120 Bytes)"
            )

        if offset != len(data):
            raise ValueError(
                f"StoreCookie has unexpected trailing bytes: {len(data) - offset}"
            )

    def _iter_fields(self):
        yield self.key
        yield self.payload
