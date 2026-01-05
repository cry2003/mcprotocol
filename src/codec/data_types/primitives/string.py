# src/codec/data_types/primitives/string.py

from dataclasses import dataclass
from .varint import VarInt
from ..constants import _DEFAULT_MAX_CODE_UNITS


@dataclass(slots=True, frozen=True)
class String:
    """Represents a UTF-8 string in the Minecraft protocol.

    The string is prefixed with a VarInt representing the number of bytes
    of its UTF-8 encoding. The length is validated against both UTF-16 code units
    and UTF-8 byte length to ensure compliance with the protocol.

    The maximum allowed UTF-16 code units is `_DEFAULT_MAX_CODE_UNITS` (32767).
    The maximum allowed UTF-8 length is `n * 3` bytes, where `n` is the number
    of UTF-16 code units. The VarInt representing the length must not exceed 3 bytes.

    Example usage:
        >>> s = String("Hello")
        >>> bytes(s)
        b'\x05Hello'

    Attributes:
        value (str): The string value to be serialized.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the string after initialization.

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
        """Convert the string to bytes suitable for network transmission.

        Returns:
            bytes: VarInt length prefix followed by UTF-8 encoded string.

        Raises:
            ValueError: If the VarInt-encoded length exceeds 3 bytes.
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
        """Deserialize a String from raw bytes.

        Args:
            data (bytes): Raw bytes received from the network.

        Returns:
            String: A new String instance with the decoded value.

        Raises:
            ValueError: If decoding fails or data is too short.
        """
        # Read VarInt length prefix
        length_varint = VarInt.from_bytes(data)
        str_len = length_varint.value

        # Remaining bytes must contain the UTF-8 string
        if len(data) < len(bytes(length_varint)) + str_len:
            raise ValueError("Data too short for expected string length")

        utf8_bytes = data[len(bytes(length_varint)) : len(bytes(length_varint)) + str_len]
        value = utf8_bytes.decode("utf-8")
        return cls(value)


