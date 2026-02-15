# src/codec/packets/configuration/clientbound/update_tags.py

from codec.packets.packet import Packet
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.special.tag_update import TaggedRegistry
from codec.data_types.primitives.varint import VarInt
from typing import Optional


class UpdateTags(Packet):
    """
    Configuration Update Tags packet.

    Packet ID:
        0x0D
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        tagged_registries (PrefixedArray[TaggedRegistry]): Registries with tag updates.
    """

    __slots__ = ("tagged_registries",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x0D))

        self.tagged_registries, consumed = PrefixedArray.from_bytes(data, TaggedRegistry)
        seen_registry_ids: set[str] = set()
        for tagged_registry in self.tagged_registries.values:
            if tagged_registry.registry_id.value in seen_registry_ids:
                raise ValueError(
                    "UpdateTags contains duplicate registry id: "
                    f"{tagged_registry.registry_id.value}"
                )
            seen_registry_ids.add(tagged_registry.registry_id.value)

        if consumed != len(data):
            raise ValueError(
                f"UpdateTags has unexpected trailing bytes: {len(data) - consumed}"
            )

    def _iter_fields(self):
        yield self.tagged_registries

    @property
    def registries_by_id(self) -> dict[str, TaggedRegistry]:
        """Return tagged registries indexed by registry identifier."""
        return {
            tagged_registry.registry_id.value: tagged_registry
            for tagged_registry in self.tagged_registries.values
        }

    def get_registry(self, registry_id: str) -> Optional[TaggedRegistry]:
        """Return one tagged registry by its identifier, or None."""
        return self.registries_by_id.get(registry_id)

    def get_tag(self, registry_id: str, tag_name: str):
        """Return one tag from a given registry, or None."""
        registry = self.get_registry(registry_id)
        if registry is None:
            return None
        return registry.get_tag(tag_name)
