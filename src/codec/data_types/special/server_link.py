# src/codec/data_types/special/server_link.py

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from codec.data_types.data_type import DataType
from codec.data_types.complex.text_component import TextComponent
from codec.data_types.primitives.boolean import Boolean
from codec.data_types.primitives.string import String
from codec.data_types.primitives.varint import VarInt


@dataclass(slots=True, frozen=True)
class ServerLinkLabel(DataType):
    """
    One server-link label, encoded as built-in ID or custom text component.

    Wire format:
        is_builtin (Boolean)
        if is_builtin: label_id (VarInt)
        else: label_text (TextComponent)
    """

    label_id: Optional[VarInt]
    label_text: Optional[TextComponent]

    def __post_init__(self) -> None:
        if self.label_id is None and self.label_text is None:
            raise ValueError("ServerLinkLabel requires either label_id or label_text")
        if self.label_id is not None and self.label_text is not None:
            raise ValueError("ServerLinkLabel cannot contain both label_id and label_text")

        if self.label_id is not None:
            if not isinstance(self.label_id, VarInt):
                raise TypeError("ServerLinkLabel.label_id must be VarInt or None")
            # Built-in labels currently documented as IDs 0..9.
            if not (0 <= self.label_id.value <= 9):
                raise ValueError(
                    f"ServerLinkLabel built-in label id out of range: "
                    f"{self.label_id.value} (expected 0..9)"
                )

        if self.label_text is not None and not isinstance(self.label_text, TextComponent):
            raise TypeError("ServerLinkLabel.label_text must be TextComponent or None")

    def __bytes__(self) -> bytes:
        if self.label_id is not None:
            return bytes(Boolean(True)) + bytes(self.label_id)
        return bytes(Boolean(False)) + bytes(self.label_text)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["ServerLinkLabel", int]:
        offset = 0

        is_builtin, consumed = Boolean.from_bytes(data[offset:])
        offset += consumed

        if is_builtin.value:
            label_id, consumed = VarInt.from_bytes(data[offset:])
            offset += consumed
            return cls(label_id=label_id, label_text=None), offset

        label_text, consumed = TextComponent.from_bytes(data[offset:])
        offset += consumed
        return cls(label_id=None, label_text=label_text), offset


@dataclass(slots=True, frozen=True)
class ServerLink(DataType):
    """
    One server link entry.

    Fields:
        label (ServerLinkLabel): Built-in or custom label.
        url (String): Link URL.
    """

    label: ServerLinkLabel
    url: String

    def __post_init__(self) -> None:
        if not isinstance(self.label, ServerLinkLabel):
            raise TypeError("ServerLink.label must be a ServerLinkLabel")
        if not isinstance(self.url, String):
            raise TypeError("ServerLink.url must be a String")

        parsed = urlparse(self.url.value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"ServerLink URL is not valid: {self.url.value!r}")

    def __bytes__(self) -> bytes:
        return bytes(self.label) + bytes(self.url)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple["ServerLink", int]:
        offset = 0

        label, consumed = ServerLinkLabel.from_bytes(data[offset:])
        offset += consumed

        url, consumed = String.from_bytes(data[offset:])
        offset += consumed

        return cls(label=label, url=url), offset
