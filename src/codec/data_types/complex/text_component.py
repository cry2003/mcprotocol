# src/codec/data_types/complex/text_component.py

from __future__ import annotations

from dataclasses import dataclass
import re
import struct
from typing import Any

from codec.data_types.data_type import DataType
from codec.data_types.constants import (
    _HEX_COLOR_RE,
    _VALID_COLORS,
    _VALID_STYLES,
    _TAG_END,
    _TAG_BYTE,
    _TAG_INT,
    _TAG_FLOAT,
    _TAG_STRING,
    _TAG_LIST,
    _TAG_COMPOUND,
    _TAG_INT_ARRAY,
    _TEXT_COMPONENT_CONTENT_TYPES,
    _TEXT_COMPONENT_CLICK_ACTIONS,
    _TEXT_COMPONENT_HOVER_ACTIONS,
)


def _encode_mutf8(value: str) -> bytes:
    out = bytearray()
    utf16 = value.encode("utf-16-be")
    for i in range(0, len(utf16), 2):
        code_unit = (utf16[i] << 8) | utf16[i + 1]
        if code_unit == 0:
            out.extend(b"\xC0\x80")
        elif code_unit <= 0x007F:
            out.append(code_unit)
        elif code_unit <= 0x07FF:
            out.append(0xC0 | ((code_unit >> 6) & 0x1F))
            out.append(0x80 | (code_unit & 0x3F))
        else:
            out.append(0xE0 | ((code_unit >> 12) & 0x0F))
            out.append(0x80 | ((code_unit >> 6) & 0x3F))
            out.append(0x80 | (code_unit & 0x3F))
    return bytes(out)


def _decode_mutf8(data: bytes) -> str:
    code_units: list[int] = []
    i = 0
    n = len(data)
    while i < n:
        b0 = data[i]
        if b0 & 0x80 == 0:
            code_units.append(b0)
            i += 1
            continue
        if (b0 & 0xE0) == 0xC0:
            if i + 1 >= n:
                raise ValueError("Invalid modified UTF-8 sequence")
            b1 = data[i + 1]
            if (b1 & 0xC0) != 0x80:
                raise ValueError("Invalid modified UTF-8 continuation byte")
            code_units.append(((b0 & 0x1F) << 6) | (b1 & 0x3F))
            i += 2
            continue
        if (b0 & 0xF0) == 0xE0:
            if i + 2 >= n:
                raise ValueError("Invalid modified UTF-8 sequence")
            b1 = data[i + 1]
            b2 = data[i + 2]
            if (b1 & 0xC0) != 0x80 or (b2 & 0xC0) != 0x80:
                raise ValueError("Invalid modified UTF-8 continuation byte")
            code_units.append(
                ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F)
            )
            i += 3
            continue
        raise ValueError("Invalid modified UTF-8 leading byte")

    utf16 = bytearray()
    for cu in code_units:
        utf16.append((cu >> 8) & 0xFF)
        utf16.append(cu & 0xFF)
    return utf16.decode("utf-16-be", errors="surrogatepass")


def _detect_content_type(comp: dict[str, Any]) -> str:
    explicit = comp.get("type")
    if explicit in _TEXT_COMPONENT_CONTENT_TYPES:
        return explicit
    detection_order = {
        "text": "text",
        "translate": "translatable",
        "score": "score",
        "selector": "selector",
        "keybind": "keybind",
        "nbt": "nbt",
    }
    for key, result in detection_order.items():
        if key in comp:
            return result
    if any(k in comp for k in ("object", "player", "atlas", "sprite")):
        return "object"
    return "text"


def _normalize_component(comp: Any) -> str | dict[str, Any]:
    if isinstance(comp, str):
        return comp
    if isinstance(comp, list):
        if not comp:
            return {"text": ""}
        first = _normalize_to_object(comp[0])
        extra = [_normalize_to_object(x) for x in comp[1:]]
        if "extra" in first:
            first["extra"] = [*_coerce_component_list(first["extra"]), *extra]
        elif extra:
            first["extra"] = extra
        return first
    if isinstance(comp, dict):
        out = dict(comp)
        if "extra" in out:
            out["extra"] = _coerce_component_list(out["extra"])
        if "with" in out:
            out["with"] = _coerce_component_list(out["with"])
        if "separator" in out:
            out["separator"] = _normalize_to_object(out["separator"])
        hover_event = out.get("hover_event")
        if isinstance(hover_event, dict):
            hv = dict(hover_event)
            if hv.get("action") == "show_text" and "value" in hv:
                hv["value"] = _normalize_to_object(hv["value"])
            if hv.get("action") == "show_entity" and "name" in hv:
                hv["name"] = _normalize_to_object(hv["name"])
            out["hover_event"] = hv
        return out
    raise TypeError(
        f"Text component must be string, list or object, got {type(comp).__name__}"
    )


def _coerce_component_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise TypeError("Component list field must be a list")
    return [_normalize_to_object(x) for x in value]


def _normalize_to_object(comp: Any) -> dict[str, Any]:
    normalized = _normalize_component(comp)
    if isinstance(normalized, str):
        return {"text": normalized}
    return normalized


def _is_simple_text_only(comp: str | dict[str, Any]) -> bool:
    if isinstance(comp, str):
        return True
    if "text" not in comp:
        return False
    allowed = {"text", "type"}
    if not set(comp).issubset(allowed):
        return False
    return comp.get("type", "text") == "text"


def _validate_color(value: str) -> None:
    if value in _VALID_COLORS:
        return
    if re.match(_HEX_COLOR_RE, value):
        return
    raise ValueError(f"Invalid color: {value}")


def _validate_component_object(comp: dict[str, Any]) -> None:
    ctype = _detect_content_type(comp)
    if "type" in comp:
        t = comp["type"]
        if not isinstance(t, str):
            raise TypeError("type must be a string")
        if t not in _TEXT_COMPONENT_CONTENT_TYPES:
            raise ValueError(f"Invalid type: {t}")

    match ctype:
        case "text":
            if "text" not in comp:
                raise ValueError("Text component requires 'text'")
        case "translatable":
            if "translate" not in comp:
                raise ValueError("Translatable component requires 'translate'")
        case "score":
            score = comp.get("score")
            if not isinstance(score, dict):
                raise TypeError("score must be an object")
            if "name" not in score or "objective" not in score:
                raise ValueError("score requires 'name' and 'objective'")
        case "selector":
            if "selector" not in comp:
                raise ValueError("Selector component requires 'selector'")
        case "keybind":
            if "keybind" not in comp:
                raise ValueError("Keybind component requires 'keybind'")
        case "nbt":
            if "nbt" not in comp:
                raise ValueError("NBT component requires 'nbt'")
            if not any(k in comp for k in ("block", "entity", "storage")):
                raise ValueError("NBT component requires one of: block, entity, storage")
            source = comp.get("source")
            if source is not None and source not in {"block", "entity", "storage"}:
                raise ValueError("source must be one of: block, entity, storage")
        case "object":
            obj = comp.get(
                "object", "atlas" if ("sprite" in comp or "atlas" in comp) else None
            )
            match obj:
                case "atlas":
                    if "sprite" not in comp:
                        raise ValueError("atlas object requires 'sprite'")
                case "player":
                    if "player" not in comp:
                        raise ValueError("player object requires 'player'")
                case None:
                    raise ValueError("object component requires object-specific fields")
                case _:
                    raise ValueError("object must be 'atlas' or 'player'")

    if "color" in comp:
        if not isinstance(comp["color"], str):
            raise TypeError("color must be a string")
        _validate_color(comp["color"])

    if "font" in comp and not isinstance(comp["font"], str):
        raise TypeError("font must be a string")

    for field in _VALID_STYLES:
        if field in comp and not isinstance(comp[field], bool):
            raise TypeError(f"{field} must be boolean")

    if "shadow_color" in comp:
        sv = comp["shadow_color"]
        if isinstance(sv, int):
            pass
        elif isinstance(sv, list):
            if len(sv) != 4 or not all(isinstance(x, (int, float)) for x in sv):
                raise TypeError("shadow_color list must be [r,g,b,a] with 4 numbers")
            if not all(0.0 <= float(x) <= 1.0 for x in sv):
                raise ValueError("shadow_color list values must be in range [0,1]")
        else:
            raise TypeError("shadow_color must be int or list[4]")

    if "insertion" in comp and not isinstance(comp["insertion"], str):
        raise TypeError("insertion must be a string")

    click = comp.get("click_event")
    if click is not None:
        if not isinstance(click, dict):
            raise TypeError("click_event must be an object")
        action = click.get("action")
        if action not in _TEXT_COMPONENT_CLICK_ACTIONS:
            raise ValueError("Invalid click_event action")
        required_by_action = {
            "open_url": "url",
            "open_file": "path",
            "run_command": "command",
            "suggest_command": "command",
            "change_page": "page",
            "copy_to_clipboard": "value",
            "show_dialog": "dialog",
            "custom": "id",
        }
        req = required_by_action[action]
        if req not in click:
            raise ValueError(f"click_event action '{action}' requires '{req}'")
        match action:
            case "change_page":
                if not isinstance(click["page"], int):
                    raise TypeError("click_event.page must be int")
            case "show_dialog":
                dialog = click["dialog"]
                if not isinstance(dialog, (str, dict)):
                    raise TypeError("click_event.dialog must be string or object")

    hover = comp.get("hover_event")
    if hover is not None:
        if not isinstance(hover, dict):
            raise TypeError("hover_event must be an object")
        action = hover.get("action")
        if action not in _TEXT_COMPONENT_HOVER_ACTIONS:
            raise ValueError("Invalid hover_event action")
        match action:
            case "show_text":
                if "value" not in hover:
                    raise ValueError("hover_event show_text requires 'value'")
            case "show_item":
                if "id" not in hover:
                    raise ValueError("hover_event show_item requires 'id'")
                if "count" in hover and not isinstance(hover["count"], int):
                    raise TypeError("hover_event show_item count must be int")
            case "show_entity":
                if "id" not in hover:
                    raise ValueError("hover_event show_entity requires 'id'")
                if "uuid" in hover:
                    uuidv = hover["uuid"]
                    if not isinstance(uuidv, str):
                        if not (
                            isinstance(uuidv, list)
                            and len(uuidv) == 4
                            and all(isinstance(x, int) for x in uuidv)
                        ):
                            raise TypeError(
                                "hover_event show_entity uuid must be string or list[4]int"
                            )

    if "extra" in comp:
        for child in _coerce_component_list(comp["extra"]):
            _validate_component_object(child)
    if "with" in comp:
        for child in _coerce_component_list(comp["with"]):
            _validate_component_object(child)


def _write_nbt_string_payload(value: str) -> bytes:
    encoded = _encode_mutf8(value)
    return struct.pack(">H", len(encoded)) + encoded


def _read_nbt_string_payload(data: bytes, offset: int) -> tuple[str, int]:
    if len(data) < offset + 2:
        raise ValueError("Not enough bytes for NBT string length")
    ln = struct.unpack(">H", data[offset : offset + 2])[0]
    offset += 2
    if len(data) < offset + ln:
        raise ValueError("Not enough bytes for NBT string payload")
    return _decode_mutf8(data[offset : offset + ln]), offset + ln


def _encode_named_tag(name: str, tag_id: int, payload: bytes) -> bytes:
    name_bytes = _encode_mutf8(name)
    return bytes([tag_id]) + struct.pack(">H", len(name_bytes)) + name_bytes + payload


def _encode_list_payload(item_tag_id: int, payload_items: list[bytes]) -> bytes:
    out = bytearray()
    out.append(item_tag_id)
    out.extend(struct.pack(">i", len(payload_items)))
    for p in payload_items:
        out.extend(p)
    return bytes(out)


def _encode_compound_payload(obj: dict[str, Any]) -> bytes:
    out = bytearray()
    for key, value in obj.items():
        tag_id, payload = _encode_value_as_named_tag_payload(key, value)
        out.extend(_encode_named_tag(key, tag_id, payload))
    out.append(_TAG_END)
    return bytes(out)


def _encode_value_as_named_tag_payload(key: str, value: Any) -> tuple[int, bytes]:
    if isinstance(value, bool):
        return _TAG_BYTE, (b"\x01" if value else b"\x00")
    if isinstance(value, int):
        return _TAG_INT, struct.pack(">i", value)
    if isinstance(value, float):
        return _TAG_FLOAT, struct.pack(">f", value)
    if isinstance(value, str):
        return _TAG_STRING, _write_nbt_string_payload(value)
    if isinstance(value, dict):
        return _TAG_COMPOUND, _encode_compound_payload(value)
    if isinstance(value, list):
        if key in {"extra", "with"}:
            items = [_encode_compound_payload(_normalize_to_object(x)) for x in value]
            return _TAG_LIST, _encode_list_payload(_TAG_COMPOUND, items)
        if key == "shadow_color":
            items = [struct.pack(">f", float(x)) for x in value]
            return _TAG_LIST, _encode_list_payload(_TAG_FLOAT, items)
        if key == "uuid" and len(value) == 4 and all(isinstance(x, int) for x in value):
            payload = struct.pack(">i", 4) + b"".join(struct.pack(">i", x) for x in value)
            return _TAG_INT_ARRAY, payload

        if not value:
            return _TAG_LIST, _encode_list_payload(_TAG_END, [])

        first_tag, _ = _encode_value_as_named_tag_payload("", value[0])
        payload_items: list[bytes] = []
        for item in value:
            tag_id, item_payload = _encode_value_as_named_tag_payload("", item)
            if tag_id != first_tag:
                raise ValueError("NBT list values must share the same tag type")
            payload_items.append(item_payload)
        return _TAG_LIST, _encode_list_payload(first_tag, payload_items)

    raise TypeError(f"Unsupported text component value type: {type(value).__name__}")


def _read_payload_for_tag(data: bytes, offset: int, tag_id: int) -> tuple[Any, int]:
    match tag_id:
        case 1:  # TAG_Byte
            if len(data) < offset + 1:
                raise ValueError("Not enough bytes for TAG_Byte")
            return data[offset] != 0, offset + 1
        case 3:  # TAG_Int
            if len(data) < offset + 4:
                raise ValueError("Not enough bytes for TAG_Int")
            return struct.unpack(">i", data[offset : offset + 4])[0], offset + 4
        case 5:  # TAG_Float
            if len(data) < offset + 4:
                raise ValueError("Not enough bytes for TAG_Float")
            return struct.unpack(">f", data[offset : offset + 4])[0], offset + 4
        case 8:  # TAG_String
            return _read_nbt_string_payload(data, offset)
        case 9:  # TAG_List
            if len(data) < offset + 5:
                raise ValueError("Not enough bytes for TAG_List")
            item_tag = data[offset]
            length = struct.unpack(">i", data[offset + 1 : offset + 5])[0]
            offset += 5
            values: list[Any] = []
            if length <= 0:
                return values, offset
            for _ in range(length):
                item, offset = _read_payload_for_tag(data, offset, item_tag)
                values.append(item)
            return values, offset
        case 10:  # TAG_Compound
            return _read_compound_payload(data, offset)
        case 11:  # TAG_Int_Array
            if len(data) < offset + 4:
                raise ValueError("Not enough bytes for TAG_Int_Array length")
            length = struct.unpack(">i", data[offset : offset + 4])[0]
            offset += 4
            if len(data) < offset + (length * 4):
                raise ValueError("Not enough bytes for TAG_Int_Array payload")
            out = []
            for i in range(length):
                start = offset + (i * 4)
                out.append(struct.unpack(">i", data[start : start + 4])[0])
            return out, offset + (length * 4)
        case _:
            raise ValueError(f"Unsupported NBT tag id for text component: {tag_id}")


def _read_compound_payload(data: bytes, offset: int) -> tuple[dict[str, Any], int]:
    out: dict[str, Any] = {}
    while True:
        if len(data) < offset + 1:
            raise ValueError("Unexpected EOF in TAG_Compound")
        tag_id = data[offset]
        offset += 1
        if tag_id == _TAG_END:
            return out, offset
        name, offset = _read_nbt_string_payload(data, offset)
        value, offset = _read_payload_for_tag(data, offset, tag_id)
        out[name] = value


@dataclass(slots=True)
class TextComponent(DataType):
    """
    Java Edition text component encoded as NBT tag.

    Root encoding:
    - TAG_String for plain text-only components.
    - TAG_Compound for all other cases.
    """

    component: str | dict[str, Any] | list[Any]

    def __post_init__(self) -> None:
        normalized = _normalize_component(self.component)
        if isinstance(normalized, dict):
            _validate_component_object(normalized)
        self.component = normalized

    def __bytes__(self) -> bytes:
        if _is_simple_text_only(self.component):
            text = self.component if isinstance(self.component, str) else self.component["text"]
            return bytes([_TAG_STRING]) + _write_nbt_string_payload(text)

        root_obj = _normalize_to_object(self.component)
        _validate_component_object(root_obj)
        return bytes([_TAG_COMPOUND]) + _encode_compound_payload(root_obj)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["TextComponent", int]:
        if not data:
            raise ValueError("Data too short for TextComponent")
        tag_id = data[0]
        offset = 1
        if tag_id == _TAG_STRING:
            text, offset = _read_nbt_string_payload(data, offset)
            return cls(text), offset
        if tag_id == _TAG_COMPOUND:
            obj, offset = _read_compound_payload(data, offset)
            if "color" in obj and isinstance(obj["color"], str):
                _validate_color(obj["color"])
            return cls(obj), offset
        raise ValueError(
            f"Invalid root tag id for TextComponent: {tag_id} (expected TAG_String or TAG_Compound)"
        )
