# src/codec/packets/handshaking/serverbound/intention.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.string import String
from codec.data_types.primitives.unsigned_short import UnsignedShort
from codec.data_types.primitives.enum import Enum


class Intention(Packet):
    """
    Handshake packet.

    Packet ID:
        0x00
    State:
        Handshaking
    Bound:
        Serverbound

    Fields:
        protocol_version (VarInt): Protocol version number.
        server_address (String): Target server hostname or IP.
        server_port (UnsignedShort): Target server port.
        intent (VarInt Enum): Intended next state: 1 (Status), 2 (Login), 3 (Transfer).
    """

    __slots__ = (
        "protocol_version",
        "server_address",
        "server_port",
        "intent",
    )

    def __init__(
        self,
        protocol_version: int,
        server_address: str,
        server_port: int,
        intent: int,
    ) -> None:
        super().__init__(packet_id=VarInt(0x00))

        if intent not in (1, 2, 3):
            raise ValueError(
                "Invalid handshake intent: must be 1 (Status), 2 (Login), or 3 (Transfer)"
            )

        self.protocol_version = VarInt(protocol_version)
        self.server_address = String(server_address)
        self.server_port = UnsignedShort(server_port)
        self.intent = Enum(intent, VarInt)

    def _iter_fields(self):
        yield self.protocol_version
        yield self.server_address
        yield self.server_port
        yield self.intent
