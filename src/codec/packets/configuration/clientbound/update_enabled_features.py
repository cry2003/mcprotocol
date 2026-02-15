# src/codec/packets/configuration/clientbound/update_enabled_features.py

from codec.packets.packet import Packet
from codec.data_types.complex.identifier import Identifier
from codec.data_types.complex.prefixed_array import PrefixedArray
from codec.data_types.primitives.varint import VarInt
from codec.packets.constants import (
    _VANILLA_FEATURE_FLAG,
    _JAVA_EXPERIMENTAL_FEATURE_FLAGS,
)


class UpdateEnabledFeatures(Packet):
    """
    Configuration Update Enabled Features packet.

    Packet ID:
        0x0C
    State:
        Configuration
    Bound:
        Clientbound

    Fields:
        feature_flags (PrefixedArray[Identifier]): Enabled feature flag identifiers.
    """

    __slots__ = ("feature_flags",)

    def __init__(self, data: bytes) -> None:
        super().__init__(packet_id=VarInt(0x0C))

        self.feature_flags, consumed = PrefixedArray.from_bytes(data, Identifier)

        seen: set[str] = set()
        for feature_flag in self.feature_flags.values:
            if feature_flag.value in seen:
                raise ValueError(
                    f"UpdateEnabledFeatures contains duplicate feature flag: "
                    f"{feature_flag.value}"
                )
            seen.add(feature_flag.value)

        if consumed != len(data):
            raise ValueError(
                "UpdateEnabledFeatures has unexpected trailing bytes: "
                f"{len(data) - consumed}"
            )

    def _iter_fields(self):
        yield self.feature_flags

    @property
    def feature_flag_names(self) -> frozenset[str]:
        """Return all feature flags as a normalized string set."""
        return frozenset(feature_flag.value for feature_flag in self.feature_flags.values)

    def has_feature(self, feature_flag: str) -> bool:
        """Return True if the exact feature flag is present."""
        return feature_flag in self.feature_flag_names

    @property
    def has_vanilla_feature(self) -> bool:
        """
        Return True if the special vanilla feature flag is present.

        Notes:
            `minecraft:vanilla` exists in most versions, but is not enforced
            as mandatory by this codec layer.
        """
        return self.has_feature(_VANILLA_FEATURE_FLAG)

    @property
    def java_experimental_features(self) -> frozenset[str]:
        """
        Return known Java experimental feature flags present in this packet.

        The known set is version-dependent and intentionally limited to
        currently documented Java experiment IDs.
        """
        return self.feature_flag_names & _JAVA_EXPERIMENTAL_FEATURE_FLAGS
