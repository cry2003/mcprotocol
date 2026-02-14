# src/codec/data_types/constants.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codec.data_types.complex.array import Array
    from codec.data_types.primitives.string import String
    from codec.data_types.primitives.int import Int
    from codec.data_types.complex.text_component import TextComponent

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
    "show_dialog": {"dialog": "TextComponent"},  # either String ID or compound
    "custom": {"id": "String", "payload": "String"},  # optional payload
}

_HOVER_EVENTS = {
    "show_text": {"value": "TextComponent"},
    "show_item": {
        "id": "String",
        "count": "Int",  # optional
        "components": "TextComponent",  # optional
    },
    "show_entity": {
        "name": "TextComponent",  # optional
        "id": "String",
        "uuid": "Array",  # array of 4 ints or String UUID
    },
}

# Constants for NBT tags and utility maps.
_TAG_END = 0
_TAG_BYTE = 1
_TAG_SHORT = 2
_TAG_INT = 3
_TAG_LONG = 4
_TAG_FLOAT = 5
_TAG_DOUBLE = 6
_TAG_BYTE_ARRAY = 7
_TAG_STRING = 8
_TAG_LIST = 9
_TAG_COMPOUND = 10
_TAG_INT_ARRAY = 11
_TAG_LONG_ARRAY = 12

# Map id -> human name (optional convenience)
_TAG_NAMES = {
    _TAG_END: "TAG_End",
    _TAG_BYTE: "TAG_Byte",
    _TAG_SHORT: "TAG_Short",
    _TAG_INT: "TAG_Int",
    _TAG_LONG: "TAG_Long",
    _TAG_FLOAT: "TAG_Float",
    _TAG_DOUBLE: "TAG_Double",
    _TAG_BYTE_ARRAY: "TAG_Byte_Array",
    _TAG_STRING: "TAG_String",
    _TAG_LIST: "TAG_List",
    _TAG_COMPOUND: "TAG_Compound",
    _TAG_INT_ARRAY: "TAG_Int_Array",
    _TAG_LONG_ARRAY: "TAG_Long_Array",
}

# NBT sizes (bytes), per specification
_NBT_NAME_LEN_BYTES = 2  # unsigned short
_NBT_STRING_LEN_BYTES = 2  # unsigned short
_NBT_LIST_LEN_BYTES = 4  # signed int
_NBT_ARRAY_LEN_BYTES = 4  # signed int
_NBT_BYTE_BYTES = 1
_NBT_SHORT_BYTES = 2
_NBT_INT_BYTES = 4
_NBT_LONG_BYTES = 8
_NBT_FLOAT_BYTES = 4
_NBT_DOUBLE_BYTES = 8

# NBT practical bounds used by parser validation
_MAX_NBT_STRING = 0xFFFF  # unsigned short byte length
_MAX_NBT_ARRAY = _INT32_MAX

# text_component.py constants
_TEXT_COMPONENT_CONTENT_TYPES = {
    "text",
    "translatable",
    "score",
    "selector",
    "keybind",
    "nbt",
    "object",
}

_TEXT_COMPONENT_CLICK_ACTIONS = {
    "open_url",
    "open_file",
    "run_command",
    "suggest_command",
    "change_page",
    "copy_to_clipboard",
    "show_dialog",
    "custom",
}

_TEXT_COMPONENT_HOVER_ACTIONS = {"show_text", "show_item", "show_entity"}

_TEXT_COMPONENT_BOOL_FIELDS = {
    "bold",
    "italic",
    "underlined",
    "strikethrough",
    "obfuscated",
    "interpret",
    "hat",
}
