# src\network\packet_io.py

import socket
from typing import Optional

from codec.packets.registry import PacketRegistry
from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.packets.constants import _MAX_VARINT_3_BYTES


class PacketIO:
    """Handles packet input/output."""

    def __init__(
        self,
        sock: socket.socket,
        compression_threshold: Optional[int] = None,
        initial_state: str = "Handshaking",
    ):
        """
        Initialize the packet I/O handler.

        Args:
            sock: Connected TCP socket.
            registry: Packet registry used for packet resolution.
            compression_threshold: Compression threshold if enabled.
            initial_state: Initial protocol state.
        """
        self.sock = sock
        self.registry = PacketRegistry()
        self.compression_threshold = compression_threshold
        self._state = initial_state

    @property
    def state(self) -> str:
        """
        Return the current protocol state.

        Returns:
            Current state.
        """
        return self._state

    def set_state(self, new_state: str) -> None:
        """
        Set the current protocol state.

        Args:
            new_state: New protocol state.
        """
        self._state = new_state

    def _encode_packet(self, packet_id: str, **kwargs) -> bytes:
        """
        Serialize a serverbound packet.

        Args:
            packet_id: Packet identifier.
            **kwargs: Packet fields.

        Returns:
            Serialized packet bytes.
        """
        packet: Packet = self.registry.instantiate(
            state=self._state,
            direction="serverbound",
            packet_id=packet_id,
            **kwargs,
        )
        return packet.serialize(self.compression_threshold)

    def _decode_packet(self, raw_bytes: bytes) -> Packet:
        """
        Decode a clientbound packet.

        Args:
            raw_bytes: Full packet bytes including length prefix.

        Returns:
            Decoded packet instance.

        Raises:
            ValueError: If packet length exceeds limits.
        """
        packet_length, cursor = VarInt.from_bytes(raw_bytes, 0)
        if packet_length.value > _MAX_VARINT_3_BYTES:
            raise ValueError(f"Packet length too large: {packet_length.value}")

        packet_bytes = raw_bytes[cursor : cursor + packet_length.value]

        packet_id, pid_size = VarInt.from_bytes(packet_bytes, 0)
        packet_data = packet_bytes[pid_size:]

        return self.registry.instantiate(
            state=self._state,
            direction="clientbound",
            packet_id=f"{packet_id.value:#04x}",
            data=packet_data,
        )

    def send(self, packet_id: str, **kwargs) -> None:
        """
        Send a serverbound packet.

        Args:
            packet_id: Packet identifier.
            **kwargs: Packet fields.
        """
        self.sock.sendall(self._encode_packet(packet_id, **kwargs))

    def read(self) -> Packet:
        """
        Read and decode a clientbound packet.

        Returns:
            Decoded packet instance.

        Raises:
            ConnectionError: If the socket closes unexpectedly.
            ValueError: If the packet length is invalid.
        """
        raw_length = bytearray()
        for _ in range(3):
            byte = self.sock.recv(1)
            if not byte:
                raise ConnectionError("Socket closed while reading packet length")
            raw_length += byte
            if byte[0] & 0x80 == 0:
                break
        else:
            raise ValueError("VarInt length exceeds 3 bytes")

        packet_length, _ = VarInt.from_bytes(raw_length, 0)
        if packet_length.value > _MAX_VARINT_3_BYTES:
            raise ValueError(f"Packet length too large: {packet_length.value}")

        raw_packet = bytearray()
        remaining = packet_length.value
        while remaining > 0:
            chunk = self.sock.recv(remaining)
            if not chunk:
                raise ConnectionError("Socket closed while reading packet data")
            raw_packet += chunk
            remaining -= len(chunk)

        return self._decode_packet(bytes(raw_length) + bytes(raw_packet))
