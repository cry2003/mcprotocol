# src/codec/data_types/special/tag_update.py

from dataclasses import dataclass
from typing import Optional

from codec.data_types.data_type import DataType
from codec.data_types.complex.identifier import Identifier
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.varint import VarInt


@dataclass(slots=True, frozen=True)
class RegistryTag(DataType):
    """
    One tag definition inside a tagged registry.

    Fields:
        tag_name (Identifier): Tag identifier without the '#' prefix.
        entries (PrefixedArray[VarInt]): Numeric entry IDs in the registry.
    """

    tag_name: Identifier
    entries: PrefixedArray

    def __post_init__(self) -> None:
        if not isinstance(self.tag_name, Identifier):
            raise TypeError("RegistryTag.tag_name must be an Identifier")
        if not isinstance(self.entries, PrefixedArray):
            raise TypeError("RegistryTag.entries must be a PrefixedArray")
        for entry_id in self.entries.values:
            if not isinstance(entry_id, VarInt):
                raise TypeError("RegistryTag.entries must contain VarInt values")
        seen_entry_ids: set[int] = set()
        for entry_id in self.entries.values:
            if entry_id.value in seen_entry_ids:
                raise ValueError(
                    f"RegistryTag contains duplicate entry id: {entry_id.value}"
                )
            seen_entry_ids.add(entry_id.value)

    def __bytes__(self) -> bytes:
        return bytes(self.tag_name) + bytes(self.entries)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["RegistryTag", int]:
        offset = 0

        tag_name, consumed = Identifier.from_bytes(data[offset:])
        offset += consumed

        entries, consumed = PrefixedArray.from_bytes(data[offset:], VarInt)
        offset += consumed

        return cls(tag_name=tag_name, entries=entries), offset

    @property
    def entry_ids(self) -> tuple[int, ...]:
        """Return entry IDs as immutable integers."""
        return tuple(entry_id.value for entry_id in self.entries.values)


@dataclass(slots=True, frozen=True)
class TaggedRegistry(DataType):
    """
    Tagged registry section in Update Tags packet.

    Fields:
        registry_id (Identifier): Registry identifier (e.g. minecraft:block).
        tags (PrefixedArray[RegistryTag]): Tags defined for the registry.
    """

    registry_id: Identifier
    tags: PrefixedArray

    def __post_init__(self) -> None:
        if not isinstance(self.registry_id, Identifier):
            raise TypeError("TaggedRegistry.registry_id must be an Identifier")
        if not isinstance(self.tags, PrefixedArray):
            raise TypeError("TaggedRegistry.tags must be a PrefixedArray")
        for tag in self.tags.values:
            if not isinstance(tag, RegistryTag):
                raise TypeError("TaggedRegistry.tags must contain RegistryTag values")
        seen_tag_names: set[str] = set()
        for tag in self.tags.values:
            if tag.tag_name.value in seen_tag_names:
                raise ValueError(
                    f"TaggedRegistry contains duplicate tag name: {tag.tag_name.value}"
                )
            seen_tag_names.add(tag.tag_name.value)

    def __bytes__(self) -> bytes:
        return bytes(self.registry_id) + bytes(self.tags)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["TaggedRegistry", int]:
        offset = 0

        registry_id, consumed = Identifier.from_bytes(data[offset:])
        offset += consumed

        tags, consumed = PrefixedArray.from_bytes(data[offset:], RegistryTag)
        offset += consumed

        return cls(registry_id=registry_id, tags=tags), offset

    @property
    def tags_by_name(self) -> dict[str, RegistryTag]:
        """Return tags indexed by tag name."""
        return {tag.tag_name.value: tag for tag in self.tags.values}

    def get_tag(self, tag_name: str) -> Optional[RegistryTag]:
        """Return a tag by name, or None if not present."""
        return self.tags_by_name.get(tag_name)
