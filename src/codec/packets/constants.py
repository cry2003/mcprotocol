# src/codec/packets/constants.py

import re

# packet.py constants
_MAX_VARINT_3_BYTES = 0x1FFFFF  # 2097151 (2^21 - 1)

# Maximum packet size representable by a 3-byte VarInt (protocol limit)
_MAX_PACKET_LENGTH = 2**21 - 1  # 2097151

# identifier.py constants
_NAMESPACE_RE = re.compile(r"^[a-z0-9._-]+$")
_VALUE_RE = re.compile(r"^[a-z0-9._/-]+$")

# custom_payload.py constants
_MAX_PAYLOAD_LENGTH = 1048576

# update_enabled_features.py constants
_VANILLA_FEATURE_FLAG = "minecraft:vanilla"
_JAVA_EXPERIMENTAL_FEATURE_FLAGS = frozenset(
    {
        "minecraft:minecart_improvements",
        "minecraft:redstone_experiments",
        "minecraft:trade_rebalance",
    }
)
