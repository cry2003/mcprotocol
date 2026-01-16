# src/codec/packet/packet.py

from abc import ABC, abstractmethod
from typing import Iterable, Optional
import zlib

from codec.data_types.primitives.varint import VarInt
from codec.packets.constants import _MAX_VARINT_3_BYTES, _MAX_UNCOMPRESSED_SERVERBOUND


class Packet(ABC):
    """Base class for Minecraft protocol packets.

    Subclasses must:
        - define `packet_id: VarInt`
        - implement `_iter_fields()` yielding the serialized fields as bytes.

    Attributes:
        packet_id (VarInt): The protocol packet ID.
    """

    __slots__ = ("packet_id",)

    def __init__(self, packet_id):
        if not isinstance(packet_id, VarInt):
            raise TypeError(
                f"packet_id must be a VarInt, got {type(packet_id).__name__}"
            )
        self.packet_id = packet_id

    @abstractmethod
    def _iter_fields(self) -> Iterable[bytes]:
        """Yield serialized packet fields as bytes.

        Subclasses must override this method to yield each field in order.

        Returns:
            Iterable[bytes]: Serialized fields.
        """
        raise NotImplementedError

    def serialize(self, compression_threshold: Optional[int] = None) -> bytes:
        """Serialize the packet according to the Minecraft protocol.

        Depending on the compression threshold, this method produces either
        a compressed or uncompressed packet compliant with the protocol specification.

        Args:
            compression_threshold: Threshold for compression.
                - None: compression disabled.
                - >= 0: packets with body length >= threshold are compressed.

        Returns:
            bytes: The serialized packet ready to be sent over TCP.

        Raises:
            ValueError: If packet exceeds protocol size limits or
                compression threshold is invalid.
        """
        # --- Build uncompressed body (Packet ID + Data) ---
        body = bytearray(bytes(self.packet_id))
        for field in self._iter_fields():
            body.extend(bytes(field))

        body_len = len(body)
        if body_len > _MAX_UNCOMPRESSED_SERVERBOUND:
            raise ValueError(
                f"Uncompressed packet too large: {body_len} bytes "
                f"(max {_MAX_UNCOMPRESSED_SERVERBOUND})"
            )

        # --- Compression disabled ---
        if compression_threshold is None:
            length_prefix = bytes(VarInt(body_len))
            if len(length_prefix) > 3:
                raise ValueError(
                    f"Packet length VarInt exceeds 3 bytes: {len(length_prefix)}"
                )
            if body_len > _MAX_VARINT_3_BYTES:
                raise ValueError(
                    f"Packet length exceeds maximum allowed: {body_len} bytes "
                    f"(max {_MAX_VARINT_3_BYTES})"
                )
            return length_prefix + body

        if compression_threshold < 0:
            raise ValueError("compression_threshold must be >= 0 or None")

        # --- Compression enabled ---
        if body_len < compression_threshold:
            # Too small → uncompressed with Data Length = 0
            data_length = bytes(VarInt(0))
            packet_length = bytes(VarInt(len(data_length) + body_len))
            if len(packet_length) > 3:
                raise ValueError(
                    f"Packet Length VarInt exceeds 3 bytes: {len(packet_length)}"
                )
            return packet_length + data_length + body

        # Compress body
        compressed = zlib.compress(body)
        data_length = bytes(VarInt(body_len))
        packet_length = bytes(VarInt(len(data_length) + len(compressed)))

        if len(packet_length) > 3:
            raise ValueError(
                f"Packet Length VarInt exceeds 3 bytes: {len(packet_length)}"
            )

        return packet_length + data_length + compressed

    def __str__(self) -> str:
        """Return a concise representation showing only public fields."""
        fields = (
            f"{name}={getattr(self, name)!r}"
            for name in getattr(self, "__slots__", ())
            if not name.startswith("_") and name != "packet_id"
        )

        return f"<{self.__class__.__name__} packet_id={self.packet_id.value:#04x}, {', '.join(fields)}>"
