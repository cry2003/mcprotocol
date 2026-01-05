# src/codec/packets/__init__.py

from codec.packets.packet import Packet

from .registry import CLIENTBOUND_REGISTRY, SERVERBOUND_REGISTRY


class PacketFactory:
    """Factory that constructs packet objects from raw packet ID and data."""

    def __new__(cls, packet_id: int, data: bytes, clientbound: bool = True) -> Packet:
        """
        Construct and return the proper Packet subclass based on packet ID.

        Args:
            packet_id (int): The ID of the packet.
            data (bytes): Raw packet data.
            clientbound (bool): True if the packet is clientbound, False if serverbound.

        Returns:
            Packet: Instance of the appropriate Packet subclass.

        Raises:
            ValueError: If the packet ID is unknown.
        """
        registry = CLIENTBOUND_REGISTRY if clientbound else SERVERBOUND_REGISTRY
        packet_cls = registry.get(packet_id)
        if packet_cls is None:
            raise ValueError(
                f"Unknown packet ID {packet_id:#04x} "
                f"for {'clientbound' if clientbound else 'serverbound'}"
            )
        return packet_cls(data)
