# src/codec/constants.py

# packet.py constants
_MAX_VARINT_3_BYTES = 0x1FFFFF          # 2097151 (2^21 - 1)
_MAX_UNCOMPRESSED_SERVERBOUND = 0x7FFFFF  # 8388607 (2^23 - 1)