# src/network/packet_io.py

import socket
import zlib
from typing import Optional

from codec.packets.registry import PacketRegistry
from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.packets.constants import _MAX_VARINT_3_BYTES


class PacketIO:
    """Handles packet input/output according to Minecraft protocol.

    This class manages both sending and receiving packets over a socket,
    handling compression transparently if enabled via SetCompression.

    It uses the registered packets from PacketRegistry to instantiate
    the correct packet class based on the connection state and packet ID.

    Attributes:
        sock (socket.socket): Socket used for communication.
        registry (PacketRegistry): Registry for packet instantiation.
        compression_threshold (Optional[int]): Current compression threshold.
            - None or < 0 → compression disabled.
            - >= 0 → packets >= threshold are compressed.
        _state (str): Current protocol state (Handshaking, Login, Play, etc.).
    """

    __slots__ = ("sock", "registry", "compression_threshold", "_state")

    def __init__(
        self,
        sock: socket.socket,
        compression_threshold: Optional[int] = None,
        initial_state: str = "Handshaking",
    ):
        """
        Initialize the packet I/O handler.

        Args:
            sock: Socket object for communication.
            compression_threshold: Initial compression threshold (None = no compression).
            initial_state: Protocol state at connection start.
        """
        self.sock = sock
        self.registry = PacketRegistry()
        self.compression_threshold = compression_threshold
        self._state = initial_state

    @property
    def state(self) -> str:
        """Return the current protocol state (Handshaking, Login, Play, etc.)."""
        return self._state

    def set_state(self, new_state: str) -> None:
        """Update the current protocol state.

        Args:
            new_state: New protocol state as a string.
        """
        self._state = new_state

    def _encode_packet(self, packet_id: str, **kwargs) -> bytes:
        """
        Serialize a serverbound packet according to current compression rules.

        Args:
            packet_id: Packet identifier as hex string, e.g., '0x01'.
            **kwargs: Fields to pass to the packet constructor.

        Returns:
            Serialized packet bytes ready to be sent.
        """
        packet: Packet = self.registry.instantiate(
            state=self._state,
            direction="serverbound",
            packet_id=packet_id,
            **kwargs,
        )
        return packet.serialize(self.compression_threshold)

    def send(self, packet_id: str, **kwargs) -> None:
        """
        Send a serverbound packet over the socket.

        Args:
            packet_id: Packet ID as hex string (e.g., '0x01').
            **kwargs: Fields to pass to the packet constructor.

        Raises:
            ConnectionError: If the socket closes unexpectedly.
            ValueError: If serialization fails or packet is too large.
        """
        self.sock.sendall(self._encode_packet(packet_id, **kwargs))

    def read(self) -> Packet:
        """
        Read and decode a clientbound packet from the socket.

        This method automatically handles:
            - Reading VarInt packet length (max 3 bytes)
            - Reading the full packet payload
            - Handling compressed packets if compression_threshold >= 0
            - Validating decompressed length matches expected Data Length

        Returns:
            Decoded Packet instance.

        Raises:
            ConnectionError: If the socket closes before reading the full packet.
            ValueError: If packet length exceeds 3-byte VarInt, exceeds protocol limits,
                        or decompressed length mismatches the Data Length.
        """
        # --- Read Packet Length (VarInt, max 3 bytes) ---
        raw_length = bytearray()
        for _ in range(3):
            byte = self.sock.recv(1)
            if not byte:
                raise ConnectionError("Socket closed while reading packet length")
            raw_length += byte
            if byte[0] & 0x80 == 0:
                break
        else:
            raise ValueError("Packet Length VarInt exceeds 3 bytes")

        packet_length = VarInt.from_bytes(raw_length)
        if packet_length.value > _MAX_VARINT_3_BYTES:
            raise ValueError(f"Packet length too large: {packet_length.value}")

        # --- Read packet payload ---
        payload = bytearray()
        remaining = packet_length.value
        while remaining > 0:
            chunk = self.sock.recv(remaining)
            if not chunk:
                raise ConnectionError("Socket closed while reading packet payload")
            payload += chunk
            remaining -= len(chunk)

        return self._decode_payload(bytes(payload))

    def _decode_payload(self, payload: bytes) -> Packet:
        """
        Decode a packet payload according to current compression rules.

        Args:
            payload: Raw packet bytes excluding Packet Length.

        Returns:
            Packet: Instantiated clientbound packet.

        Raises:
            ValueError: If decompressed length mismatches Data Length, or size exceeds limits.
        """
        cursor = 0

        # Compression disabled → legacy format
        if self.compression_threshold is None:
            packet_id = VarInt.from_bytes(payload)
            cursor = len(bytes(packet_id))

            return self.registry.instantiate(
                state=self._state,
                direction="clientbound",
                packet_id=f"{packet_id.value:#04x}",
                data=payload[cursor:],
            )

        # Compression enabled → Data Length is mandatory
        data_length = VarInt.from_bytes(payload)
        cursor = len(bytes(data_length))

        # Uncompressed packet
        if data_length.value == 0:
            packet_id = VarInt.from_bytes(payload[cursor:])
            cursor += len(bytes(packet_id))

            return self.registry.instantiate(
                state=self._state,
                direction="clientbound",
                packet_id=f"{packet_id.value:#04x}",
                data=payload[cursor:],
            )

        # Compressed packet
        if data_length.value > 2**23:
            raise ValueError(f"Uncompressed packet size too large: {data_length.value}")

        decompressed = zlib.decompress(payload[cursor:])
        if len(decompressed) != data_length.value:
            raise ValueError("Decompressed data length mismatch")

        packet_id = VarInt.from_bytes(decompressed)
        cursor = len(bytes(packet_id))

        return self.registry.instantiate(
            state=self._state,
            direction="clientbound",
            packet_id=f"{packet_id.value:#04x}",
            data=decompressed[cursor:],
        )
