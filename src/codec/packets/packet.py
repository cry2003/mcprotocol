# src/codec/packet/packet.py

from abc import ABC, abstractmethod
from typing import Iterable, Optional
import zlib

from codec.data_types.primitives.varint import VarInt
from codec.packets.constants import _MAX_VARINT_3_BYTES


class Packet(ABC):
    """Base class for all Minecraft protocol packets."""

    __slots__ = ("packet_id",)

    def __init__(self, packet_id: VarInt):
        if not isinstance(packet_id, VarInt):
            raise TypeError(
                f"packet_id must be a VarInt, got {type(packet_id).__name__}"
            )
        self.packet_id = packet_id

    @abstractmethod
    def _iter_fields(self) -> Iterable[bytes]:
        raise NotImplementedError

    def serialize(self, compression_threshold: Optional[int] = None) -> bytes:
        """Serialize the packet according to the Minecraft protocol."""

        # --- Build Packet ID + Data ---
        body = bytearray(bytes(self.packet_id))
        for field in self._iter_fields():
            body.extend(bytes(field))

        body_len = len(body)

        # Treat negative threshold as compression disabled
        if compression_threshold is not None and compression_threshold < 0:
            compression_threshold = None

        # ============================================================
        # No compression
        # ============================================================
        if compression_threshold is None:
            if body_len > _MAX_VARINT_3_BYTES:
                raise ValueError(
                    f"Packet length exceeds maximum allowed size: "
                    f"{body_len} bytes (max {_MAX_VARINT_3_BYTES})"
                )

            length_prefix = VarInt(body_len)
            length_bytes = bytes(length_prefix)

            if len(length_bytes) > 3:
                raise ValueError(
                    f"Packet Length VarInt exceeds 3 bytes: {len(length_bytes)}"
                )

            return length_bytes + body

        # ============================================================
        # Compression enabled
        # ============================================================
        if body_len < compression_threshold:
            # Uncompressed packet with Data Length = 0
            data_length = VarInt(0)
            packet_length_value = len(bytes(data_length)) + body_len

            if packet_length_value > _MAX_VARINT_3_BYTES:
                raise ValueError(
                    f"Packet length exceeds maximum allowed size: "
                    f"{packet_length_value} bytes (max {_MAX_VARINT_3_BYTES})"
                )

            packet_length = VarInt(packet_length_value)
            packet_length_bytes = bytes(packet_length)

            if len(packet_length_bytes) > 3:
                raise ValueError(
                    f"Packet Length VarInt exceeds 3 bytes: "
                    f"{len(packet_length_bytes)}"
                )

            return packet_length_bytes + bytes(data_length) + body

        # --- Compressed packet ---
        compressed_body = zlib.compress(body)
        data_length = VarInt(body_len)

        packet_length_value = len(bytes(data_length)) + len(compressed_body)

        if packet_length_value > _MAX_VARINT_3_BYTES:
            raise ValueError(
                f"Packet length exceeds maximum allowed size: "
                f"{packet_length_value} bytes (max {_MAX_VARINT_3_BYTES})"
            )

        packet_length = VarInt(packet_length_value)
        packet_length_bytes = bytes(packet_length)

        if len(packet_length_bytes) > 3:
            raise ValueError(
                f"Packet Length VarInt exceeds 3 bytes: " f"{len(packet_length_bytes)}"
            )

        return packet_length_bytes + bytes(data_length) + compressed_body

    def __str__(self) -> str:
        fields = (
            f"{name}={getattr(self, name)!r}"
            for name in getattr(self, "__slots__", ())
            if not name.startswith("_") and name != "packet_id"
        )
        return (
            f"<{self.__class__.__name__} "
            f"packet_id={self.packet_id.value:#04x}, "
            f"{', '.join(fields)}>"
        )

    def __repr__(self) -> str:
        return self.__str__()
