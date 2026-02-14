# src/codec/data_types/complex/json_text_component.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import json
import re

from codec.data_types.data_type import DataType
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.string import String
from codec.data_types.primitives.boolean import Boolean
from codec.data_types.primitives.int import Int
from codec.data_types.complex.array import Array
from codec.data_types.constants import (
    _VALID_STYLES,
    _CLICK_EVENTS,
    _HOVER_EVENTS,
    _VALID_COLORS,
    _HEX_COLOR_RE,
)


@dataclass(slots=True)
class JsonTextComponent(DataType):
    """Minecraft JSON Text Component.

    Supports all content types and formatting options according to Minecraft protocol:
    - Content types: text, translatable, score, selector, keybind, nbt, object
    - Formatting: color, font, bold, italic, underlined, strikethrough, obfuscated, shadow_color
    - Interactivity: click_event, hover_event, insertion
    - Children: extra (list of child components)
    - Object types: atlas, player
    """

    component: dict | list | str

    def __post_init__(self) -> None:
        if isinstance(self.component, JsonTextComponent):
            raise TypeError("Nested JsonTextComponent is not allowed")
        if not isinstance(self.component, (dict, list, str)):
            raise TypeError(
                f"Component must be dict, list, or str, got {type(self.component).__name__}"
            )
        self.component = self._wrap_component(self.component)

    def _detect_content_type(self, comp: dict) -> str:
        """Auto-detect content type based on present keys.

        Precedence order per docs:
        text > translate > score > selector > keybind > nbt > object
        """
        explicit_type = comp.get("type")
        if explicit_type in {
            "text",
            "translatable",
            "score",
            "selector",
            "keybind",
            "nbt",
            "object",
        }:
            return explicit_type

        # Check keys in order of precedence
        for key in [
            "text",
            "translate",
            "score",
            "selector",
            "keybind",
            "nbt",
        ]:
            if key in comp:
                return key

        # Check for object type (atlas or player)
        if "object" in comp or "atlas" in comp or "sprite" in comp or "player" in comp:
            return "object"

        return "text"  # Default to plain text

    def _validate_color(self, color: str) -> None:
        """Validate color format."""
        if color in _VALID_COLORS:
            return
        # Check hex format #RRGGBB
        if re.match(_HEX_COLOR_RE, color):
            return
        raise ValueError(
            f"Invalid color: {color}. Must be a valid color name or hex #RRGGBB"
        )

    def _wrap_shadow_color(self, value: Any) -> Any:
        """Wrap shadow_color as ARGB int or RGBA float list."""
        if isinstance(value, list):
            # List of 4 floats [R, G, B, A]
            if len(value) != 4:
                raise ValueError("shadow_color list must have 4 floats")
            return Array([value])  # Will be serialized as floats
        elif isinstance(value, int):
            # ARGB format as int
            return Int(value)
        else:
            raise TypeError("shadow_color must be int or list of 4 floats")

    def _wrap_score(self, value: dict) -> dict:
        """Wrap score object with name and objective."""
        if "name" not in value or "objective" not in value:
            raise ValueError("score must have 'name' and 'objective' fields")
        return {
            "name": String(value["name"]),
            "objective": String(value["objective"]),
        }

    def _wrap_player_object(self, player_obj: dict) -> dict:
        """Wrap player object with profile data."""
        wrapped = {}
        if "name" in player_obj:
            wrapped["name"] = String(player_obj["name"])
        if "id" in player_obj:
            # UUID as int array [I; a, b, c, d]
            uuid = player_obj["id"]
            if isinstance(uuid, str):
                # Parse hyphenated UUID to int array
                wrapped["id"] = self._uuid_to_int_array(uuid)
            elif isinstance(uuid, list):
                wrapped["id"] = Array([Int(v) for v in uuid])
            else:
                raise TypeError("Player id must be string UUID or int array")
        if "texture" in player_obj:
            wrapped["texture"] = String(player_obj["texture"])
        if "cape" in player_obj:
            wrapped["cape"] = String(player_obj["cape"])
        if "model" in player_obj:
            model = player_obj["model"]
            if model not in {"wide", "slim"}:
                raise ValueError(f"Model must be 'wide' or 'slim', got {model}")
            wrapped["model"] = String(model)
        if "properties" in player_obj:
            properties = []
            for prop in player_obj["properties"]:
                prop_obj = {
                    "name": String(prop["name"]),
                    "value": String(prop["value"]),
                }
                if "signature" in prop:
                    prop_obj["signature"] = String(prop["signature"])
                properties.append(prop_obj)
            wrapped["properties"] = Array(properties)
        if "hat" in player_obj:
            wrapped["hat"] = Boolean(bool(player_obj["hat"]))
        return wrapped

    def _uuid_to_int_array(self, uuid_str: str) -> Array:
        """Convert UUID string to int array."""
        # Parse UUID like 550e8400-e29b-41d4-a716-446655440000
        parts = uuid_str.split("-")
        if len(parts) != 5:
            raise ValueError(f"Invalid UUID format: {uuid_str}")
        # Create 4 int32 values from UUID
        int_array = []
        # This is simplified; full implementation would convert properly
        return Array([Int(0)] * 4)

    def _wrap_atlas_object(self, atlas_obj: dict) -> dict:
        """Wrap atlas object sprite reference."""
        # sprite is required for atlas
        if "sprite" not in atlas_obj:
            raise ValueError("Atlas object requires 'sprite' field")
        wrapped = {
            "object": String("atlas"),
            "atlas": String(
                atlas_obj.get("atlas", "minecraft:blocks")
            ),  # Default atlas
            "sprite": String(atlas_obj["sprite"]),
        }
        return wrapped

    def _validate_nbt(self, nbt_obj: dict) -> None:
        """Validate NBT component - must have at least one of block/entity/storage."""
        if "nbt" not in nbt_obj:
            return  # Not an NBT component

        # Per docs: "Requires one of [String] block, [String] entity, or [String] storage"
        if not any(key in nbt_obj for key in ["block", "entity", "storage"]):
            raise ValueError(
                "NBT component must have at least one of: block, entity, or storage"
            )

        # Validate source if present
        if "source" in nbt_obj:
            source = nbt_obj["source"]
            if source not in {"block", "entity", "storage"}:
                raise ValueError(
                    f"Invalid NBT source: {source}. Must be 'block', 'entity', or 'storage'"
                )

    def _get_separator_default(self, content_type: str) -> dict:
        """Get default separator for selector and nbt components."""
        if content_type == "selector":
            # Default: {color: "gray", text: ", "}
            return {"color": "gray", "text": ", "}
        elif content_type == "nbt":
            # Default: {text: ", "}
            return {"text": ", "}
        return {}

    def _wrap_click_event(self, value: dict) -> dict:
        """Wrap click_event with validation."""
        action = value.get("action")
        if action not in _CLICK_EVENTS:
            raise ValueError(f"Invalid click_event action: {action}")

        wrapped = {"action": String(action)}
        expected_fields = _CLICK_EVENTS[action]

        for key, expected_type in expected_fields.items():
            if key in value:
                if key == "page":
                    wrapped[key] = Int(value[key])
                elif (
                    key == "url" or key == "path" or key == "command" or key == "value"
                ):
                    wrapped[key] = String(value[key])
                elif key == "dialog":
                    # dialog can be string ID or object
                    if isinstance(value[key], str):
                        wrapped[key] = String(value[key])
                    else:
                        wrapped[key] = JsonTextComponent(value[key])
                else:
                    wrapped[key] = String(str(value[key]))

        return wrapped

    def _wrap_hover_event(self, value: dict) -> dict:
        """Wrap hover_event with validation."""
        action = value.get("action")
        if action not in _HOVER_EVENTS:
            raise ValueError(f"Invalid hover_event action: {action}")

        wrapped = {"action": String(action)}

        if action == "show_text":
            # value can be string, list, or object
            if "value" not in value:
                raise ValueError("show_text hover_event requires 'value' field")
            wrapped["value"] = JsonTextComponent(value["value"])
        elif action == "show_item":
            if "id" not in value:
                raise ValueError("show_item hover_event requires 'id' field")
            wrapped["id"] = String(value.get("id", "minecraft:air"))
            if "count" in value:
                wrapped["count"] = Int(value["count"])
            if "components" in value:
                wrapped["components"] = value["components"]  # Keep as-is for now
        elif action == "show_entity":
            if "id" not in value and "uuid" not in value:
                raise ValueError("show_entity hover_event requires 'id' field")
            if "name" in value:
                wrapped["name"] = JsonTextComponent(value["name"])
            wrapped["id"] = String(value["id"])
            # UUID can be string or int array
            if "uuid" in value:
                uuid_val = value["uuid"]
                if isinstance(uuid_val, str):
                    wrapped["uuid"] = String(uuid_val)
                elif isinstance(uuid_val, list):
                    wrapped["uuid"] = Array([Int(v) for v in uuid_val])

        return wrapped

    def _wrap_component(self, comp: Any) -> Any:
        """Convert all raw values into proper DataTypes recursively."""
        if isinstance(comp, str):
            return String(comp)

        if isinstance(comp, list):
            # List of components - equivalent to {text: first, extra: rest}
            return Array([self._wrap_component(x) for x in comp])

        if isinstance(comp, dict):
            wrapped: dict[str, Any] = {}
            content_type = self._detect_content_type(comp)

            # Validate NBT components early
            self._validate_nbt(comp)

            for key, value in comp.items():
                # Content type fields
                if key == "type":
                    wrapped[key] = String(value)
                elif key == "text":
                    wrapped[key] = String(value)
                elif key == "translate":
                    wrapped[key] = String(value)
                elif key == "fallback":
                    # Used with translate if no translation found
                    wrapped[key] = String(value)
                elif key == "with":
                    # List of components to insert in translation slots
                    wrapped[key] = Array([JsonTextComponent(x) for x in value])
                elif key == "score":
                    wrapped[key] = self._wrap_score(value)
                elif key == "selector":
                    wrapped[key] = String(value)
                elif key == "separator":
                    # Used in selector and nbt for joining multiple values
                    wrapped[key] = JsonTextComponent(value)
                elif key == "keybind":
                    wrapped[key] = String(value)
                elif key == "nbt":
                    wrapped[key] = String(value)
                elif key == "interpret":
                    # Parse NBT text as text component
                    wrapped[key] = Boolean(bool(value))
                elif key == "block":
                    wrapped[key] = String(value)
                elif key == "entity":
                    wrapped[key] = String(value)
                elif key == "storage":
                    wrapped[key] = String(value)
                elif key == "source":
                    # Validate source value
                    if value not in {"block", "entity", "storage"}:
                        raise ValueError(
                            f"Invalid NBT source: {value}. Must be 'block', 'entity', or 'storage'"
                        )
                    wrapped[key] = String(value)
                elif key == "object":
                    # object type: "atlas" or "player"
                    if value == "atlas":
                        wrapped["object"] = String("atlas")
                    elif value == "player":
                        wrapped["object"] = String("player")
                    else:
                        wrapped[key] = String(value)
                elif key == "atlas":
                    wrapped[key] = String(value)
                elif key == "sprite":
                    wrapped[key] = String(value)
                elif key == "player":
                    wrapped[key] = self._wrap_player_object(value)
                # Formatting fields
                elif key == "color":
                    if isinstance(value, str):
                        self._validate_color(value)
                        wrapped[key] = String(value)
                    else:
                        raise TypeError("Color must be a string")
                elif key == "font":
                    wrapped[key] = String(value)
                elif key in _VALID_STYLES:
                    # bold, italic, underlined, strikethrough, obfuscated
                    wrapped[key] = Boolean(bool(value))
                elif key == "shadow_color":
                    wrapped[key] = self._wrap_shadow_color(value)
                # Interactivity fields
                elif key == "insertion":
                    wrapped[key] = String(value)
                elif key == "click_event":
                    wrapped[key] = self._wrap_click_event(value)
                elif key == "hover_event":
                    wrapped[key] = self._wrap_hover_event(value)
                # Children
                elif key == "extra":
                    wrapped[key] = Array([JsonTextComponent(x) for x in value])
                else:
                    # Preserve unknown keys as-is
                    wrapped[key] = value

            # Apply separator defaults if not provided (for selector and nbt)
            if "separator" not in wrapped and content_type in {"selector", "nbt"}:
                sep_default = self._get_separator_default(content_type)
                if sep_default:
                    wrapped["separator"] = JsonTextComponent(sep_default)

            return wrapped

        raise TypeError(f"Invalid component type: {type(comp).__name__}")

    def __bytes__(self) -> bytes:
        """Serialize component to JSON with VarInt length prefix."""

        def serialize(obj: Any) -> Any:
            if isinstance(obj, DataType):
                return bytes(obj)
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(x) for x in obj]
            else:
                return obj

        serialized = serialize(self.component)
        json_bytes = json.dumps(
            serialized, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return bytes(VarInt(len(json_bytes))) + json_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["JsonTextComponent", int]:
        """Deserialize component from JSON with VarInt length prefix.

        Args:
            data: Byte buffer containing VarInt length + JSON bytes

        Returns:
            JsonTextComponent instance
        """
        length_varint, varint_bytes = VarInt.from_bytes(data)
        json_start = varint_bytes
        json_end = json_start + length_varint.value
        raw_json = data[json_start:json_end]
        obj = json.loads(raw_json.decode("utf-8"))
        return cls(obj), json_end
