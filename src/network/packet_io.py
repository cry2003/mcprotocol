# src/network/packet_io.py

import socket
from typing import Optional
from codec.packets.registry import PacketRegistry
from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.packets.constants import _MAX_VARINT_3_BYTES


class PacketIO:
    """Handle Minecraft packet I/O using PacketRegistry and Packet base class."""

    def __init__(
        self,
        sock: socket.socket,
        registry: PacketRegistry,
        compression_threshold: Optional[int] = None,
    ):
        self.sock = sock
        self.registry = registry
        self.compression_threshold = compression_threshold

    # ---------------------- Private encode/decode ---------------------- #

    def _encode_packet(
        self, state: str, direction: str, packet_id: str, **kwargs
    ) -> bytes:
        """Create a serverbound packet and serialize it (compression handled by Packet)."""
        packet: Packet = self.registry.instantiate(
            state, direction, packet_id, **kwargs
        )
        return packet.serialize(self.compression_threshold)

    def _decode_packet(self, state: str, direction: str, raw_bytes: bytes) -> Packet:
        """Decode received bytes into a Packet object (handles compression)."""
        # 1. Read packet length VarInt
        packet_length, cursor = VarInt.from_bytes(raw_bytes, 0)
        if packet_length.value > _MAX_VARINT_3_BYTES:
            raise ValueError(f"Packet length too large: {packet_length.value}")

        # 2. Slice full packet bytes
        packet_bytes = raw_bytes[cursor : cursor + packet_length.value]

        # 3. Read Packet ID VarInt
        packet_id, pid_size = VarInt.from_bytes(packet_bytes, 0)
        packet_data = packet_bytes[pid_size:]

        # 4. Instantiate clientbound packet
        return self.registry.instantiate(
            state, direction, f"{packet_id.value:#04x}", data=packet_data
        )

    # ---------------------- Public I/O ---------------------- #

    def send(self, state: str, direction: str, packet_id: str, **kwargs):
        """Encode and send a serverbound packet over the socket."""
        self.sock.sendall(self._encode_packet(state, direction, packet_id, **kwargs))

    def read(self, state: str, direction: str) -> Packet:
        """Read a full clientbound packet from the socket and decode it."""
        # 1. Read VarInt packet length (max 3 bytes)
        raw_length = bytearray()
        for _ in range(3):
            b = self.sock.recv(1)
            if not b:
                raise ConnectionError("Socket closed while reading packet length")
            raw_length += b
            if b[0] & 0x80 == 0:  # MSB 0 → last byte of VarInt
                break
        else:
            raise ValueError("VarInt length exceeds 3 bytes")

        packet_length, _ = VarInt.from_bytes(raw_length, 0)
        if packet_length.value > _MAX_VARINT_3_BYTES:
            raise ValueError(f"Packet length too large: {packet_length.value}")

        # 2. Read remaining bytes
        raw_packet = bytearray()
        remaining = packet_length.value
        while remaining > 0:
            chunk = self.sock.recv(remaining)
            if not chunk:
                raise ConnectionError("Socket closed while reading packet data")
            raw_packet += chunk
            remaining -= len(chunk)

        full_bytes = bytes(raw_length) + bytes(raw_packet)
        return self._decode_packet(state, direction, full_bytes)
