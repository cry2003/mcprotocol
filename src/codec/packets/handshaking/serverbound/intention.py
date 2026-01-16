# src\codec\packets\handshaking\serverbound\intention.py

from dataclasses import dataclass

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.string import String
from codec.data_types.primitives.unsigned_short import UnsignedShort
from codec.data_types.primitives.enum import Enum


@dataclass(slots=True)
class Intention(Packet):
    """Serverbound Handshake packet (0x00).

    This packet is sent immediately after opening the TCP connection.
    It switches the protocol state to Status, Login, or Transfer.

    Fields (in order):
        - protocol_version (VarInt)
        - server_address (String)
        - server_port (UnsignedShort)
        - Intent (VarInt Enum)
    """
    protocol_version: int
    server_address: str
    server_port: int
    intent: int

    def __post_init__(self) -> None:
        """Validate handshake-specific constraints."""
        super().__init__(VarInt(0x00))

        if self.intent not in (1, 2, 3):
            raise ValueError(
                "Invalid handshake Intent: "
                "must be 1 (Status), 2 (Login), or 3 (Transfer)"
            )

    def _iter_fields(self):
        """Yield serialized handshake fields in protocol order."""
        yield bytes(VarInt(self.protocol_version))
        yield bytes(String(self.server_address))
        yield bytes(UnsignedShort(self.server_port))
        yield bytes(Enum(self.intent, VarInt))
