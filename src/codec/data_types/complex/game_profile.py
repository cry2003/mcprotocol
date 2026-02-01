# src/codec/data_types/complex/game_profile.py

from dataclasses import dataclass
from typing import List
from ..data_type import DataType
from ..primitives.string import String
from ..primitives.varint import VarInt
from .prefixed_optional import PrefixedOptional
from ..primitives.uuid import UUID


@dataclass(slots=True, frozen=True)
class Property(DataType):
    """
    Represents a single Minecraft player property.

    Attributes:
        name (String): Name of the property (e.g., "textures").
        value (String): Base64-encoded value of the property, usually JSON.
        signature (PrefixedOptional[String]): Optional signature of the property.
            Encoded as a boolean prefix + value if present.
    """

    name: String
    value: String
    signature: PrefixedOptional[String]

    def __post_init__(self) -> None:
        if not isinstance(self.name, String):
            raise TypeError("Property name must be a String")
        if not isinstance(self.value, String):
            raise TypeError("Property value must be a String")
        if not isinstance(self.signature, PrefixedOptional):
            raise TypeError("Property signature must be a PrefixedOptional[String]")

    def __bytes__(self) -> bytes:
        return bytes(self.name) + bytes(self.value) + bytes(self.signature)

    @classmethod
    def from_bytes(cls, data: bytes) -> "Property":
        name = String.from_bytes(data)
        offset = len(bytes(name))

        value = String.from_bytes(data[offset:])
        offset += len(bytes(value))

        if offset < len(data):
            signature = PrefixedOptional.from_bytes(data[offset:], String)
        else:
            signature = PrefixedOptional(None)

        return cls(name=name, value=value, signature=signature)


@dataclass(slots=True, frozen=True)
class GameProfile(DataType):
    """
    Represents a Minecraft player profile.

    Attributes:
        uuid (UUID): Player's unique identifier as a DataType.
        name (String): Player's username.
        properties (List[Property]): List of player properties such as textures or skins.
    """

    uuid: UUID
    name: String
    properties: List[Property]

    def __post_init__(self) -> None:
        if not isinstance(self.uuid, UUID):
            raise TypeError("uuid must be a UUID DataType instance")
        if not isinstance(self.name, String):
            raise TypeError("name must be a String")
        if not isinstance(self.properties, list):
            raise TypeError("properties must be a list of Property")
        for prop in self.properties:
            if not isinstance(prop, Property):
                raise TypeError("All elements in properties must be Property instances")

    def __bytes__(self) -> bytes:
        uuid_bytes = bytes(self.uuid)
        name_bytes = bytes(self.name)
        properties_count = bytes(VarInt(len(self.properties)))
        properties_bytes = b"".join(bytes(prop) for prop in self.properties)
        return uuid_bytes + name_bytes + properties_count + properties_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "GameProfile":
        offset = 0

        # Deserialize UUID
        uuid = UUID.from_bytes(data[offset:16])  # UUID DataType uses 16 bytes
        offset += 16

        # Deserialize Name
        name = String.from_bytes(data[offset:])
        offset += len(bytes(name))

        # Deserialize Properties count
        properties_count_varint = VarInt.from_bytes(data[offset:])
        properties_count = properties_count_varint.value
        offset += len(bytes(properties_count_varint))

        # Deserialize Properties
        properties = []
        for _ in range(properties_count):
            prop_name = String.from_bytes(data[offset:])
            offset += len(bytes(prop_name))

            prop_value = String.from_bytes(data[offset:])
            offset += len(bytes(prop_value))

            if offset < len(data):
                prop_signature = PrefixedOptional.from_bytes(data[offset:], String)
            else:
                prop_signature = PrefixedOptional(None)

            properties.append(
                Property(name=prop_name, value=prop_value, signature=prop_signature)
            )

        return cls(uuid=uuid, name=name, properties=properties)
