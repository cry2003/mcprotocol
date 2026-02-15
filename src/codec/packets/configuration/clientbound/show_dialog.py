# src/codec/packets/configuration/clientbound/show_dialog.py

from codec.packets.packet import Packet
from codec.data_types.complex.nbt import TagCompound, dump_nbt
from codec.data_types.primitives.varint import VarInt
from codec.data_types.special.dialog_definition import validate_dialog_definition


class ShowDialog(Packet):
    """
    Configuration Show Dialog packet.

    Packet ID:
        0x12
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        dialog (TagCompound): Inline dialog definition encoded as network NBT.
    """

    __slots__ = ("dialog",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x12))

        self.dialog, consumed = TagCompound.from_bytes(data, network=True, is_root=True)
        validate_dialog_definition(self.dialog)
        if consumed != len(data):
            raise ValueError(
                f"ShowDialog has unexpected trailing bytes: {len(data) - consumed}"
            )

    def _iter_fields(self):
        yield dump_nbt(self.dialog, network=True)
