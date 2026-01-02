# src/codec/packets/lslp.py

from dataclasses import dataclass
from codec.data_types.primitives.unsigned_short import UnsignedShort
from codec.data_types.primitives.string import String


@dataclass(slots=True, frozen=True)
class LegacyServerListPing:
    """Represents the Legacy Server List Ping packet (pre-Netty, Minecraft <= 1.6).

    Encoding:
        - Packet ID: 0xFE
        - Payload: Unsigned Byte, always 0x01
        - Plugin Message: 0xFA
            - Length of following string: 11 (MC|PingHost)
            - String: "MC|PingHost" encoded in UTF-16BE
            - Data length: 7 + len(hostname in bytes)
            - Protocol version: 1 byte
            - Hostname length: short (code units)
            - Hostname: UTF-16BE
            - Port: 4-byte int, big-endian

    Attributes:
        hostname (str): Hostname or IP of the server.
        port (int): Port of the server (default 25565).
        protocol_version (int): Minecraft protocol version (e.g., 74).
    """

    hostname: str
    port: int = 25565
    protocol_version: int = 74

    def _iter_fields(self):
        """Yield the serialized fields in order."""
        # Packet ID
        yield b"\xfe"
        # Payload
        yield b"\x01"
        # Plugin Message
        yield b"\xfa"
        # Length of "MC|PingHost" in code units (16-bit big-endian)
        yield UnsignedShort(11).__bytes__()
        # String "MC|PingHost" encoded UTF-16BE
        yield String("MC|PingHost").value.encode("utf-16-be")
        # Length of rest of the data: 7 + len(hostname UTF-16BE)
        hostname_bytes = self.hostname.encode("utf-16-be")
        yield UnsignedShort(7 + len(hostname_bytes)).__bytes__()
        # Protocol version
        yield self.protocol_version.to_bytes(1, "big")
        # Hostname length in code units
        yield UnsignedShort(len(self.hostname)).__bytes__()
        # Hostname UTF-16BE
        yield hostname_bytes
        # Port (4 bytes, big-endian)
        yield self.port.to_bytes(4, "big")

    def __bytes__(self) -> bytes:
        """Convert the packet to its raw byte representation."""
        return b"".join(self._iter_fields())
