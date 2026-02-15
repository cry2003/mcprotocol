# src/codec/packets/configuration/clientbound/custom_report_details.py

from codec.packets.packet import Packet
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.varint import VarInt
from codec.data_types.special.custom_report_detail import CustomReportDetail


class CustomReportDetails(Packet):
    """
    Configuration Custom Report Details packet.

    Packet ID:
        0x0F
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        details (PrefixedArray[CustomReportDetail]): Key-value text entries.
            Maximum 32 entries.
    """

    __slots__ = ("details",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x0F))

        self.details, consumed = PrefixedArray.from_bytes(data, CustomReportDetail)

        if len(self.details.values) > 32:
            raise ValueError(
                f"CustomReportDetails has too many entries: {len(self.details.values)} "
                "(max 32)"
            )

        if consumed != len(data):
            raise ValueError(
                f"CustomReportDetails has unexpected trailing bytes: {len(data) - consumed}"
            )

    def _iter_fields(self):
        yield self.details
