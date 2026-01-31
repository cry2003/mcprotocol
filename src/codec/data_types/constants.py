# src/codec/data_types/data_types_constants.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codec.data_types.complex.array import Array
    from codec.data_types.primitives.string import String
    from codec.data_types.primitives.int import Int
    from codec.data_types.complex.json_text_component import JsonTextComponent

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

# json_text_component.py constants
_MAX_JSON_TEXT_COMPONENT_BYTES = 262144

# int.py constants
_INT32_MIN = -2_147_483_648
_INT32_MAX = 2_147_483_647

# json_text_component.py JSON Text Component constants
_VALID_COLORS = {
    "black",
    "dark_blue",
    "dark_green",
    "dark_aqua",
    "dark_red",
    "dark_purple",
    "gold",
    "gray",
    "dark_gray",
    "blue",
    "green",
    "aqua",
    "red",
    "light_purple",
    "yellow",
    "white",
}
_VALID_STYLES = {"bold", "italic", "underlined", "strikethrough", "obfuscated"}
_HEX_COLOR_RE = r"^#[0-9a-fA-F]{6}$"

# Click & Hover events with correct DataTypes
_CLICK_EVENTS = {
    "open_url": {"url": "String"},
    "open_file": {"path": "String"},
    "run_command": {"command": "String"},
    "suggest_command": {"command": "String"},
    "change_page": {"page": "Int"},
    "copy_to_clipboard": {"value": "String"},
    "show_dialog": {"dialog": "JsonTextComponent"},  # either String ID or compound
    "custom": {"id": "String", "payload": "String"},  # optional payload
}

_HOVER_EVENTS = {
    "show_text": {"value": "JsonTextComponent"},
    "show_item": {
        "id": "String",
        "count": "Int",  # optional
        "components": "JsonTextComponent",  # optional
    },
    "show_entity": {
        "name": "JsonTextComponent",  # optional
        "id": "String",
        "uuid": "Array",  # array of 4 ints or String UUID
    },
}
