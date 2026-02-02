# src/codec/constants.py

import re

# packet.py constants
_MAX_VARINT_3_BYTES = 0x1FFFFF  # 2097151 (2^21 - 1)

# Maximum packet size representable by a 3-byte VarInt (protocol limit)
_MAX_PACKET_LENGTH = 2**21 - 1  # 2097151

# identifier.py constants
_NAMESPACE_RE = re.compile(r"^[a-z0-9._-]+$")
_VALUE_RE = re.compile(r"^[a-z0-9._/-]+$")
