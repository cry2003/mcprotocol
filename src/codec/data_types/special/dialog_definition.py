# src/codec/data_types/special/dialog_definition.py

from codec.data_types.complex.nbt import (
    NBT,
    TagByte,
    TagCompound,
    TagInt,
    TagList,
    TagString,
)


_DIALOG_TYPES = {
    "minecraft:notice",
    "minecraft:confirmation",
    "minecraft:multi_action",
    "minecraft:server_links",
    "minecraft:dialog_list",
}

_AFTER_ACTIONS = {"close", "none", "wait_for_response"}


def _expect_compound_field(root: TagCompound, name: str) -> TagCompound:
    field = root.value.get(name)
    if not isinstance(field, TagCompound):
        raise ValueError(f"Dialog field '{name}' must be a compound")
    return field


def _expect_string_field(root: TagCompound, name: str) -> str:
    field = root.value.get(name)
    if not isinstance(field, TagString):
        raise ValueError(f"Dialog field '{name}' must be a string")
    return field.value


def _optional_string_field(root: TagCompound, name: str) -> str | None:
    field = root.value.get(name)
    if field is None:
        return None
    if not isinstance(field, TagString):
        raise ValueError(f"Dialog field '{name}' must be a string")
    return field.value


def _optional_bool_field(root: TagCompound, name: str) -> bool | None:
    field = root.value.get(name)
    if field is None:
        return None
    if not isinstance(field, TagByte):
        raise ValueError(f"Dialog field '{name}' must be a boolean (TagByte)")
    return field.value != 0


def _optional_positive_int(root: TagCompound, name: str) -> None:
    field = root.value.get(name)
    if field is None:
        return
    if not isinstance(field, TagInt):
        raise ValueError(f"Dialog field '{name}' must be an int")
    if field.value <= 0:
        raise ValueError(f"Dialog field '{name}' must be > 0")


def _optional_ranged_int(root: TagCompound, name: str, min_v: int, max_v: int) -> None:
    field = root.value.get(name)
    if field is None:
        return
    if not isinstance(field, TagInt):
        raise ValueError(f"Dialog field '{name}' must be an int")
    if not (min_v <= field.value <= max_v):
        raise ValueError(
            f"Dialog field '{name}' out of range: {field.value} (expected {min_v}..{max_v})"
        )


def _is_text_component_tag(tag: NBT) -> bool:
    # Dialog fields that accept text components can be string/object/list.
    return isinstance(tag, (TagString, TagCompound, TagList))


def _require_text_component(root: TagCompound, name: str) -> None:
    field = root.value.get(name)
    if field is None:
        raise ValueError(f"Dialog field '{name}' is required")
    if not _is_text_component_tag(field):
        raise ValueError(
            f"Dialog field '{name}' must be a text component (string/list/compound)"
        )


def validate_dialog_definition(dialog: TagCompound) -> None:
    """
    Validate top-level dialog definition constraints used by Show Dialog packet.

    The validator is intentionally strict on fundamental structure and required
    fields, while leaving deep action/input-body schema expansion for future work.
    """
    dialog_type = _expect_string_field(dialog, "type")
    if dialog_type not in _DIALOG_TYPES:
        raise ValueError(f"Unsupported dialog type: {dialog_type}")

    _require_text_component(dialog, "title")

    after_action = _optional_string_field(dialog, "after_action")
    if after_action is not None and after_action not in _AFTER_ACTIONS:
        raise ValueError(
            f"Invalid dialog after_action: {after_action} "
            f"(expected one of {sorted(_AFTER_ACTIONS)})"
        )

    pause_value = _optional_bool_field(dialog, "pause")
    if after_action == "none" and pause_value is not False:
        raise ValueError("Dialog after_action='none' requires pause=false")

    _optional_positive_int(dialog, "columns")
    _optional_ranged_int(dialog, "button_width", 1, 1024)

    if dialog_type == "minecraft:confirmation":
        _expect_compound_field(dialog, "yes")
        _expect_compound_field(dialog, "no")
    elif dialog_type == "minecraft:multi_action":
        actions = dialog.value.get("actions")
        if not isinstance(actions, TagList):
            raise ValueError("Dialog type minecraft:multi_action requires list field 'actions'")
        if len(actions.value) == 0:
            raise ValueError("Dialog type minecraft:multi_action requires non-empty 'actions'")
    elif dialog_type == "minecraft:dialog_list":
        if "dialogs" not in dialog.value:
            raise ValueError("Dialog type minecraft:dialog_list requires field 'dialogs'")
