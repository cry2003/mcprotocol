# src/codec/data_types/primitives/string.py

from dataclasses import dataclass
from .varint import VarInt
from ..constants import _DEFAULT_MAX_CODE_UNITS
from ..data_type import DataType


@dataclass(slots=True, frozen=True)
class String(DataType):
    """Represents a UTF-8 string in Minecraft protocol format.

    Encoding:
        - Prefix with a VarInt representing UTF-8 byte length.
        - Followed by UTF-8 encoded bytes of the string.

    Protocol constraints:
        - Maximum UTF-16 code units: `_DEFAULT_MAX_CODE_UNITS` (32767)
        - Maximum UTF-8 encoded length: `_DEFAULT_MAX_CODE_UNITS * 3` bytes
        - Length VarInt must not exceed 3 bytes

    Attributes:
        value (str): The string content.

    Serialization:
        - `__bytes__()` returns VarInt length + UTF-8 bytes.
        - `from_bytes(data)` parses a string from a byte buffer.

    Validation:
        - Raises ValueError if string exceeds UTF-16 or UTF-8 limits.
        - Ensures length prefix fits protocol requirements.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate string length according to protocol limits.

        Raises:
            ValueError: If the string exceeds maximum UTF-16 code units or
                        maximum UTF-8 byte length.
        """
        utf16_le = self.value.encode("utf-16-le")
        code_units = len(utf16_le) >> 1
        if code_units > _DEFAULT_MAX_CODE_UNITS:
            raise ValueError(
                f"String too long: {code_units} UTF-16 code units "
                f"(max {_DEFAULT_MAX_CODE_UNITS})"
            )

        utf8_bytes = self.value.encode("utf-8")
        if len(utf8_bytes) > _DEFAULT_MAX_CODE_UNITS * 3:
            raise ValueError(
                f"UTF-8 encoded length {len(utf8_bytes)} exceeds "
                f"maximum {_DEFAULT_MAX_CODE_UNITS * 3}"
            )

    def __bytes__(self) -> bytes:
        """Serialize the string with VarInt length prefix for network transmission.

        Returns:
            bytes: VarInt length + UTF-8 bytes.

        Raises:
            ValueError: If the length VarInt exceeds 3 bytes.
        """
        utf8_bytes = self.value.encode("utf-8")
        length_prefix = bytes(VarInt(len(utf8_bytes)))
        if len(length_prefix) > 3:
            raise ValueError(
                f"Encoded length VarInt exceeds 3 bytes: {len(length_prefix)}"
            )
        return length_prefix + utf8_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "String":
        """Deserialize a String from a byte buffer.

        Args:
            data (bytes): Byte buffer containing the string.

        Returns:
            String: String instance.

        Raises:
            ValueError: If data is too short for the expected string length.
        """
        length_varint = VarInt.from_bytes(data)
        str_len = length_varint.value
        
        # Calculate how many bytes the VarInt consumed
        varint_bytes = bytes(length_varint)
        varint_size = len(varint_bytes)
        
        start = varint_size
        end = start + str_len

        if len(data) < end:
            raise ValueError("Data too short for expected string length")

        utf8_bytes = data[start:end]
        value = utf8_bytes.decode("utf-8")
        return cls(value)
