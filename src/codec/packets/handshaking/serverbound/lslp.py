# src/codec/packets/handshaking/serverbound/lslp.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.unsigned_short import UnsignedShort
from codec.data_types.primitives.string import String


class LegacyServerListPing(Packet):
    """
    Legacy Server List Ping packet (pre-Netty, Minecraft <= 1.6).

    Packet ID:
        0xFE
    State:
        Status (legacy)
    Bound:
        Serverbound

    Fields:
        hostname (str): Hostname or IP of the server.
        port (int): Port of the server (default 25565).
        protocol_version (int): Minecraft protocol version (default 74).
    """

    __slots__ = (
        "hostname",
        "port",
        "protocol_version",
    )

    def __init__(
        self,
        hostname: str,
        port: int = 25565,
        protocol_version: int = 74,
    ) -> None:
        super().__init__(packet_id=VarInt(0xFE))

        if not hostname:
            raise ValueError("Hostname cannot be empty")
        if not (0 < port <= 65535):
            raise ValueError(f"Port must be in range 1-65535, got {port}")
        if protocol_version < 0:
            raise ValueError(
                f"Protocol version must be non-negative, got {protocol_version}"
            )

        self.hostname = hostname
        self.port = port
        self.protocol_version = protocol_version

    def _iter_fields(self):
        """
        Yield packet payload fields in wire order.
        """
        # Packet ID (legacy, not VarInt-prefixed)
        yield b"\xfe"

        # Payload discriminator
        yield b"\x01"

        # Plugin message identifier
        yield b"\xfa"

        # Length of "MC|PingHost" in UTF-16 code units
        yield bytes(UnsignedShort(11))

        # "MC|PingHost" encoded in UTF-16BE
        yield String("MC|PingHost").value.encode("utf-16-be")

        # Hostname encoded in UTF-16BE
        hostname_bytes = self.hostname.encode("utf-16-be")

        # Length of remaining data
        yield bytes(UnsignedShort(7 + len(hostname_bytes)))

        # Protocol version (1 byte)
        yield self.protocol_version.to_bytes(1, "big")

        # Hostname length in UTF-16 code units
        yield bytes(UnsignedShort(len(self.hostname)))

        # Hostname bytes
        yield hostname_bytes

        # Port (4 bytes, big-endian)
        yield self.port.to_bytes(4, "big")

    def __bytes__(self) -> bytes:
        """
        Return the raw packet byte representation.

        Returns:
            Serialized packet bytes.
        """
        return b"".join(self._iter_fields())
