# src/codec/packets/configuration/clientbound/code_of_conduct.py

from codec.packets.packet import Packet
from codec.data_types.primitives.string import String
from codec.data_types.primitives.varint import VarInt


class CodeOfConduct(Packet):
    """
    Configuration Code Of Conduct packet.

    Packet ID:
        0x13
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        code_of_conduct (String): Server code-of-conduct text.
    """

    __slots__ = ("code_of_conduct",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x13))

        self.code_of_conduct, consumed = String.from_bytes(data)
        if consumed != len(data):
            raise ValueError(
                f"CodeOfConduct has unexpected trailing bytes: {len(data) - consumed}"
            )

    def _iter_fields(self):
        yield self.code_of_conduct
