# src/codec/packets/configuration/clientbound/finish_configuration.py

from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt


class FinishConfiguration(Packet):
    """
    Configuration Finish Configuration packet.

    Packet ID:
        0x03
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        None

    Notes:
        This packet indicates that configuration is complete and the
        connection will proceed to Play state.
    """

    __slots__ = ()

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x03))
        if data:
            raise ValueError(
                f"FinishConfiguration has no fields, got {len(data)} trailing bytes"
            )

    def _iter_fields(self):
        return iter(())
