# src/codec/data_types/data_types_constants.py

# varint.py and varlong.py constants
_SEGMENT_BITS = 0x7F
_CONTINUE_BIT = 0x80
_MAX_VARINT = 0xFFFFFFFF
_MAX_VARLONG = 0xFFFFFFFFFFFFFFFF


# string.py constants
_DEFAULT_MAX_CODE_UNITS = 32767

# long.py constants
_MIN_LONG = -9223372036854775808
_MAX_LONG = 9223372036854775807