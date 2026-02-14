# src/codec/data_types/complex/nbt.py

from __future__ import annotations

import gzip
import zlib
import struct
from typing import Dict, List, Tuple, Type, Optional

from codec.data_types.constants import (
    _TAG_END,
    _TAG_BYTE,
    _TAG_SHORT,
    _TAG_INT,
    _TAG_LONG,
    _TAG_FLOAT,
    _TAG_DOUBLE,
    _TAG_BYTE_ARRAY,
    _TAG_STRING,
    _TAG_LIST,
    _TAG_COMPOUND,
    _TAG_INT_ARRAY,
    _TAG_LONG_ARRAY,
    _TAG_NAMES,
    _MAX_NBT_STRING,
    _MAX_NBT_ARRAY,
)


# -------------------------
# Exceptions
# -------------------------


class NbtParseError(ValueError):
    """Raised when NBT parsing encounters malformed data."""


# -------------------------
# Base Tag
# -------------------------


class NBT:
    """Base class for all NBT tags."""

    tag_id: int = -1
    __slots__ = ("name",)

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

    def to_bytes(self, network: bool = False, is_root: bool = False) -> bytes:
        """
        Serialize tag including its named header (if applicable).
        For network mode and root compound, the root compound header is special.
        """
        raise NotImplementedError

    @classmethod
    def from_bytes(
        cls, data: bytes, *, network: bool = False, is_root: bool = False
    ) -> Tuple["NBT", int]:
        """
        Parse a named tag from bytes (data begins with the tag id byte).
        Returns (instance, consumed).
        """
        raise NotImplementedError

    @classmethod
    def from_payload(cls, data: bytes, *, network: bool = False) -> Tuple["NBT", int]:
        """
        Parse only the payload (no leading tag id / name header).
        Used for list element parsing. Returns (instance, consumed).
        """
        raise NotImplementedError


# -------------------------
# Helpers for headers
# -------------------------


def _ensure_bytes(data: bytes, needed: int) -> None:
    if len(data) < needed:
        raise NbtParseError(f"Not enough bytes: needed {needed}, have {len(data)}")


def _mutf8_encode(value: str) -> bytes:
    """
    Encode string using Java Modified UTF-8 (used by NBT names/strings).
    """
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


def _mutf8_decode(data: bytes) -> str:
    """
    Decode Java Modified UTF-8 bytes into a Python string.
    """
    code_units: List[int] = []
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
                raise NbtParseError("Invalid modified UTF-8 sequence")
            b1 = data[i + 1]
            if (b1 & 0xC0) != 0x80:
                raise NbtParseError("Invalid modified UTF-8 continuation byte")
            code_units.append(((b0 & 0x1F) << 6) | (b1 & 0x3F))
            i += 2
            continue

        if (b0 & 0xF0) == 0xE0:
            if i + 2 >= n:
                raise NbtParseError("Invalid modified UTF-8 sequence")
            b1 = data[i + 1]
            b2 = data[i + 2]
            if (b1 & 0xC0) != 0x80 or (b2 & 0xC0) != 0x80:
                raise NbtParseError("Invalid modified UTF-8 continuation byte")
            code_units.append(
                ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F)
            )
            i += 3
            continue

        raise NbtParseError("Invalid modified UTF-8 leading byte")

    utf16 = bytearray()
    for cu in code_units:
        utf16.append((cu >> 8) & 0xFF)
        utf16.append(cu & 0xFF)
    return utf16.decode("utf-16-be", errors="surrogatepass")


def _encode_named_header(
    name: Optional[str], tag_id: int, network: bool, is_root: bool
) -> bytes:
    """
    Encode the tag id and optional name header.
    For network & is_root & TAG_COMPOUND, omit the name header.
    """
    header = bytes([tag_id])
    if network and is_root and tag_id == _TAG_COMPOUND:
        return header
    name_bytes = _mutf8_encode(name or "")
    return header + struct.pack(">H", len(name_bytes)) + name_bytes


def _decode_named_header(
    data: bytes, expected_id: int, network: bool, is_root: bool
) -> Tuple[Optional[str], int]:
    """
    Decode named header from data starting with tag id byte.
    Returns (name_or_None, offset_after_header).
    """
    _ensure_bytes(data, 1)
    tag_id = data[0]
    if tag_id != expected_id:
        raise NbtParseError(
            f"Unexpected tag id {tag_id}, expected {_TAG_NAMES.get(expected_id, expected_id)}"
        )
    offset = 1
    if network and is_root and tag_id == _TAG_COMPOUND:
        return None, offset
    _ensure_bytes(data[offset:], 2)
    name_len = struct.unpack(">H", data[offset : offset + 2])[0]
    offset += 2
    _ensure_bytes(data[offset:], name_len)
    name = _mutf8_decode(data[offset : offset + name_len])
    offset += name_len
    return name, offset


# -------------------------
# Primitive tags implementations
# -------------------------


class TagEnd(NBT):
    tag_id = _TAG_END
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(None)

    def to_bytes(self, network: bool = False, is_root: bool = False) -> bytes:
        return bytes([_TAG_END])

    @classmethod
    def from_bytes(cls, data: bytes, *, network: bool = False, is_root: bool = False):
        _ensure_bytes(data, 1)
        if data[0] != _TAG_END:
            raise NbtParseError("TAG_End expected")
        return cls(), 1

    @classmethod
    def from_payload(cls, data: bytes, *, network: bool = False):
        # payload-less for TAG_End
        return cls(), 0


class TagByte(NBT):
    tag_id = _TAG_BYTE
    __slots__ = ("value",)

    def __init__(self, value: int, name: Optional[str] = None):
        super().__init__(name)
        self.value = int(value)

    def to_bytes(self, network=False, is_root=False) -> bytes:
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        return header + struct.pack(">b", self.value)

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 1)
        value = struct.unpack(">b", data[offset : offset + 1])[0]
        return cls(value, name), offset + 1

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 1)
        value = struct.unpack(">b", data[0:1])[0]
        return cls(value, None), 1


class TagShort(NBT):
    tag_id = _TAG_SHORT
    __slots__ = ("value",)

    def __init__(self, value: int, name: Optional[str] = None):
        super().__init__(name)
        self.value = int(value)

    def to_bytes(self, network=False, is_root=False) -> bytes:
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        return header + struct.pack(">h", self.value)

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 2)
        value = struct.unpack(">h", data[offset : offset + 2])[0]
        return cls(value, name), offset + 2

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 2)
        value = struct.unpack(">h", data[0:2])[0]
        return cls(value, None), 2


class TagInt(NBT):
    tag_id = _TAG_INT
    __slots__ = ("value",)

    def __init__(self, value: int, name: Optional[str] = None):
        super().__init__(name)
        self.value = int(value)

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        return header + struct.pack(">i", self.value)

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 4)
        value = struct.unpack(">i", data[offset : offset + 4])[0]
        return cls(value, name), offset + 4

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 4)
        value = struct.unpack(">i", data[0:4])[0]
        return cls(value, None), 4


class TagLong(NBT):
    tag_id = _TAG_LONG
    __slots__ = ("value",)

    def __init__(self, value: int, name: Optional[str] = None):
        super().__init__(name)
        self.value = int(value)

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        return header + struct.pack(">q", self.value)

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 8)
        value = struct.unpack(">q", data[offset : offset + 8])[0]
        return cls(value, name), offset + 8

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 8)
        value = struct.unpack(">q", data[0:8])[0]
        return cls(value, None), 8


class TagFloat(NBT):
    tag_id = _TAG_FLOAT
    __slots__ = ("value",)

    def __init__(self, value: float, name: Optional[str] = None):
        super().__init__(name)
        self.value = float(value)

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        return header + struct.pack(">f", self.value)

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 4)
        value = struct.unpack(">f", data[offset : offset + 4])[0]
        return cls(value, name), offset + 4

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 4)
        value = struct.unpack(">f", data[0:4])[0]
        return cls(value, None), 4


class TagDouble(NBT):
    tag_id = _TAG_DOUBLE
    __slots__ = ("value",)

    def __init__(self, value: float, name: Optional[str] = None):
        super().__init__(name)
        self.value = float(value)

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        return header + struct.pack(">d", self.value)

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 8)
        value = struct.unpack(">d", data[offset : offset + 8])[0]
        return cls(value, name), offset + 8

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 8)
        value = struct.unpack(">d", data[0:8])[0]
        return cls(value, None), 8


# -------------------------
# Array / String / List / Compound / IntArray / LongArray
# -------------------------


class TagByteArray(NBT):
    tag_id = _TAG_BYTE_ARRAY
    __slots__ = ("value",)

    def __init__(self, value: bytes, name: Optional[str] = None):
        super().__init__(name)
        self.value = bytes(value)

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        return header + struct.pack(">i", len(self.value)) + self.value

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 4)
        length = struct.unpack(">i", data[offset : offset + 4])[0]
        offset += 4
        if length < 0 or length > _MAX_NBT_ARRAY:
            raise NbtParseError(f"Invalid byte array length: {length}")
        _ensure_bytes(data[offset:], length)
        value = data[offset : offset + length]
        return cls(value, name), offset + length

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 4)
        length = struct.unpack(">i", data[0:4])[0]
        if length < 0 or length > _MAX_NBT_ARRAY:
            raise NbtParseError(f"Invalid byte array length: {length}")
        _ensure_bytes(data[4:], length)
        value = data[4 : 4 + length]
        return cls(value, None), 4 + length


class TagString(NBT):
    tag_id = _TAG_STRING
    __slots__ = ("value",)

    def __init__(self, value: str, name: Optional[str] = None):
        super().__init__(name)
        self.value = str(value)

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        b = _mutf8_encode(self.value)
        return header + struct.pack(">H", len(b)) + b

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 2)
        length = struct.unpack(">H", data[offset : offset + 2])[0]
        offset += 2
        if length < 0 or length > _MAX_NBT_STRING:
            raise NbtParseError(f"Invalid string length: {length}")
        _ensure_bytes(data[offset:], length)
        value = _mutf8_decode(data[offset : offset + length])
        return cls(value, name), offset + length

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 2)
        length = struct.unpack(">H", data[0:2])[0]
        if length < 0 or length > _MAX_NBT_STRING:
            raise NbtParseError(f"Invalid string length: {length}")
        _ensure_bytes(data[2:], length)
        value = _mutf8_decode(data[2 : 2 + length])
        return cls(value, None), 2 + length


class TagList(NBT):
    tag_id = _TAG_LIST
    __slots__ = ("item_type", "value")

    def __init__(self, item_type: int, value: List[NBT], name: Optional[str] = None):
        super().__init__(name)
        self.item_type = int(item_type)
        self.value = list(value)
        for item in self.value:
            if item.tag_id != self.item_type:
                raise NbtParseError(
                    f"List item type mismatch: expected {self.item_type}, got {item.tag_id}"
                )

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        payload = bytes([self.item_type]) + struct.pack(">i", len(self.value))
        for item in self.value:
            payload += _serialize_payload_only(item, network=network)
        return header + payload

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        # parse payload (item_type + length + items)
        _ensure_bytes(data[offset:], 1)
        item_type = data[offset]
        offset += 1
        _ensure_bytes(data[offset:], 4)
        length = struct.unpack(">i", data[offset : offset + 4])[0]
        offset += 4
        items: List[NBT] = []
        if length <= 0:
            # consume nothing more (spec allows item_type be 0 or any)
            return cls(item_type, items, name), offset
        tag_cls = _TAG_CLASSES.get(item_type)
        if tag_cls is None:
            raise NbtParseError(f"Unknown list item tag id: {item_type}")
        for _ in range(length):
            item, consumed = tag_cls.from_payload(data[offset:], network=network)
            items.append(item)
            offset += consumed
        return cls(item_type, items, name), offset

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 5)
        item_type = data[0]
        length = struct.unpack(">i", data[1:5])[0]
        offset = 5
        items: List[NBT] = []
        if length <= 0:
            return cls(item_type, items, None), offset
        tag_cls = _TAG_CLASSES.get(item_type)
        if tag_cls is None:
            raise NbtParseError(f"Unknown list item tag id: {item_type}")
        for _ in range(length):
            item, consumed = tag_cls.from_payload(data[offset:], network=network)
            items.append(item)
            offset += consumed
        return cls(item_type, items, None), offset


class TagCompound(NBT):
    tag_id = _TAG_COMPOUND
    __slots__ = ("value",)

    def __init__(self, value: Dict[str, NBT], name: Optional[str] = None):
        super().__init__(name)
        self.value = dict(value)

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        payload = b""
        for tag in self.value.values():
            payload += tag.to_bytes(network=network, is_root=False)
        payload += bytes([_TAG_END])
        return header + payload

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        # decode header (name) first
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        # parse compound payload: sequence of named tags until TAG_END
        tags: Dict[str, NBT] = {}
        while True:
            _ensure_bytes(data[offset:], 1)
            tag_id = data[offset]
            offset += 1
            if tag_id == _TAG_END:
                break
            tag_cls = _TAG_CLASSES.get(tag_id)
            if tag_cls is None:
                raise NbtParseError(f"Unknown tag id in compound: {tag_id}")
            # pass the slice starting at the tag id (offset-1)
            tag, consumed = tag_cls.from_bytes(
                data[offset - 1 :], network=network, is_root=False
            )
            if tag.name is None:
                raise NbtParseError("Compound nested tag has no name")
            tags[tag.name] = tag
            offset += consumed - 1
        return cls(tags, name), offset

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        # no name header: data begins with first tag id
        offset = 0
        tags: Dict[str, NBT] = {}
        while True:
            _ensure_bytes(data[offset:], 1)
            tag_id = data[offset]
            offset += 1
            if tag_id == _TAG_END:
                break
            tag_cls = _TAG_CLASSES.get(tag_id)
            if tag_cls is None:
                raise NbtParseError(f"Unknown tag id in compound: {tag_id}")
            tag, consumed = tag_cls.from_bytes(
                data[offset - 1 :], network=network, is_root=False
            )
            if tag.name is None:
                raise NbtParseError("Compound nested tag has no name")
            tags[tag.name] = tag
            offset += consumed - 1
        return cls(tags, None), offset


class TagIntArray(NBT):
    tag_id = _TAG_INT_ARRAY
    __slots__ = ("value",)

    def __init__(self, value: List[int], name: Optional[str] = None):
        super().__init__(name)
        self.value = [int(v) for v in value]

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        payload = struct.pack(">i", len(self.value))
        for v in self.value:
            payload += struct.pack(">i", v)
        return header + payload

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 4)
        length = struct.unpack(">i", data[offset : offset + 4])[0]
        offset += 4
        if length < 0 or length > _MAX_NBT_ARRAY:
            raise NbtParseError(f"Invalid int array length: {length}")
        _ensure_bytes(data[offset:], length * 4)
        vals = []
        for i in range(length):
            vals.append(
                struct.unpack(">i", data[offset + i * 4 : offset + (i + 1) * 4])[0]
            )
        return cls(vals, name), offset + length * 4

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 4)
        length = struct.unpack(">i", data[0:4])[0]
        if length < 0 or length > _MAX_NBT_ARRAY:
            raise NbtParseError(f"Invalid int array length: {length}")
        _ensure_bytes(data[4:], length * 4)
        vals = []
        offset = 4
        for i in range(length):
            vals.append(
                struct.unpack(">i", data[offset + i * 4 : offset + (i + 1) * 4])[0]
            )
        return cls(vals, None), 4 + length * 4


class TagLongArray(NBT):
    tag_id = _TAG_LONG_ARRAY
    __slots__ = ("value",)

    def __init__(self, value: List[int], name: Optional[str] = None):
        super().__init__(name)
        self.value = [int(v) for v in value]

    def to_bytes(self, network=False, is_root=False):
        header = _encode_named_header(self.name, self.tag_id, network, is_root)
        payload = struct.pack(">i", len(self.value))
        for v in self.value:
            payload += struct.pack(">q", v)
        return header + payload

    @classmethod
    def from_bytes(cls, data: bytes, *, network=False, is_root=False):
        name, offset = _decode_named_header(data, cls.tag_id, network, is_root)
        _ensure_bytes(data[offset:], 4)
        length = struct.unpack(">i", data[offset : offset + 4])[0]
        offset += 4
        if length < 0 or length > _MAX_NBT_ARRAY:
            raise NbtParseError(f"Invalid long array length: {length}")
        _ensure_bytes(data[offset:], length * 8)
        vals = []
        for i in range(length):
            vals.append(
                struct.unpack(">q", data[offset + i * 8 : offset + (i + 1) * 8])[0]
            )
        return cls(vals, name), offset + length * 8

    @classmethod
    def from_payload(cls, data: bytes, *, network=False):
        _ensure_bytes(data, 4)
        length = struct.unpack(">i", data[0:4])[0]
        if length < 0 or length > _MAX_NBT_ARRAY:
            raise NbtParseError(f"Invalid long array length: {length}")
        _ensure_bytes(data[4:], length * 8)
        vals = []
        offset = 4
        for i in range(length):
            vals.append(
                struct.unpack(">q", data[offset + i * 8 : offset + (i + 1) * 8])[0]
            )
        return cls(vals, None), 4 + length * 8


# -------------------------
# Helper payload-only serializer
# -------------------------


def _serialize_payload_only(tag: NBT, network: bool = False) -> bytes:
    """
    Serialize a tag but produce payload-only bytes (no name header).
    Used for TagList item serialization.
    For primitive tags, the payload is the fixed-length binary; for compounds/lists/arrays it is their payload format.
    """
    # For payload-only, rely on specific implementations:
    if isinstance(tag, TagByte):
        return struct.pack(">b", tag.value)
    if isinstance(tag, TagShort):
        return struct.pack(">h", tag.value)
    if isinstance(tag, TagInt):
        return struct.pack(">i", tag.value)
    if isinstance(tag, TagLong):
        return struct.pack(">q", tag.value)
    if isinstance(tag, TagFloat):
        return struct.pack(">f", tag.value)
    if isinstance(tag, TagDouble):
        return struct.pack(">d", tag.value)
    if isinstance(tag, TagByteArray):
        return struct.pack(">i", len(tag.value)) + tag.value
    if isinstance(tag, TagString):
        b = _mutf8_encode(tag.value)
        return struct.pack(">H", len(b)) + b
    if isinstance(tag, TagList):
        # item type + length + items payload
        payload = bytes([tag.item_type]) + struct.pack(">i", len(tag.value))
        for item in tag.value:
            payload += _serialize_payload_only(item, network=network)
        return payload
    if isinstance(tag, TagCompound):
        payload = b""
        for t in tag.value.values():
            payload += t.to_bytes(network=network, is_root=False)
        payload += bytes([_TAG_END])
        return payload
    if isinstance(tag, TagIntArray):
        payload = struct.pack(">i", len(tag.value))
        for v in tag.value:
            payload += struct.pack(">i", v)
        return payload
    if isinstance(tag, TagLongArray):
        payload = struct.pack(">i", len(tag.value))
        for v in tag.value:
            payload += struct.pack(">q", v)
        return payload
    raise TypeError(
        f"Unsupported tag type for payload-only serialization: {type(tag).__name__}"
    )


# -------------------------
# Tag registry
# -------------------------

_TAG_CLASSES: Dict[int, Type[NBT]] = {
    _TAG_END: TagEnd,
    _TAG_BYTE: TagByte,
    _TAG_SHORT: TagShort,
    _TAG_INT: TagInt,
    _TAG_LONG: TagLong,
    _TAG_FLOAT: TagFloat,
    _TAG_DOUBLE: TagDouble,
    _TAG_BYTE_ARRAY: TagByteArray,
    _TAG_STRING: TagString,
    _TAG_LIST: TagList,
    _TAG_COMPOUND: TagCompound,
    _TAG_INT_ARRAY: TagIntArray,
    _TAG_LONG_ARRAY: TagLongArray,
}


# -------------------------
# High-level I/O helpers
# -------------------------


def load_nbt(data: bytes, *, network: bool = False) -> TagCompound:
    """
    Load NBT from raw bytes. Automatically handles gzip/zlib detection.
    Returns the root TagCompound instance.
    """
    # detect gzip header 0x1f8b
    if len(data) >= 2 and data[0:2] == b"\x1f\x8b":
        raw = gzip.decompress(data)
    else:
        # try zlib; if fails, assume uncompressed
        try:
            raw = zlib.decompress(data)
        except Exception:
            raw = data

    # parse root compound
    if not raw:
        raise NbtParseError("Empty NBT payload")
    tag, consumed = TagCompound.from_bytes(raw, network=network, is_root=True)
    if consumed != len(raw):
        raise NbtParseError("Trailing bytes after root tag")
    return tag


def dump_nbt(
    tag: TagCompound, *, compress: Optional[str] = None, network: bool = False
) -> bytes:
    """
    Serialize a TagCompound to bytes. Optionally compress using 'gzip' or 'zlib'.
    If network=True, root compound will be serialized without name header (protocol >=1.20.2).
    """
    if not isinstance(tag, TagCompound):
        raise TypeError("Root NBT tag must be TagCompound")

    raw = tag.to_bytes(network=network, is_root=True)
    if compress == "gzip":
        return gzip.compress(raw)
    if compress == "zlib":
        return zlib.compress(raw)
    return raw
