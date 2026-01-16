# src/codec/data_types/primitives/string.py

from dataclasses import dataclass
from .varint import VarInt
from ..constants import _DEFAULT_MAX_CODE_UNITS


@dataclass(slots=True, frozen=True)
class String:
    """
    Represents a UTF-8 string in the Minecraft protocol with a VarInt length prefix.

    Minecraft encodes strings as follows:
        [VarInt length of UTF-8 bytes][UTF-8 bytes]

    This class handles:
        - Serialization (`__bytes__`) to network-ready bytes.
        - Deserialization (`from_bytes`) from raw network bytes.
        - Validation of string length against protocol limits.

    Protocol rules enforced:
        - Maximum UTF-16 code units: `_DEFAULT_MAX_CODE_UNITS` (32767)
        - Maximum UTF-8 encoded length: `_DEFAULT_MAX_CODE_UNITS * 3` bytes
        - Length VarInt must not exceed 3 bytes

    Attributes:
        value (str): The actual string content.

    Methods:
        __bytes__():
            Serialize the string to bytes with a VarInt length prefix.
            Raises ValueError if the VarInt length exceeds 3 bytes.

        from_bytes(data: bytes, offset: int = 0) -> tuple[String, int]:
            Deserialize a string from bytes starting at `offset`.
            Returns a tuple:
                - String instance
                - Total bytes consumed (length VarInt + UTF-8 bytes)
            Raises ValueError if data is too short for the expected string length.

    Example usage:
        >>> s = String("Hello")
        >>> b = bytes(s)
        >>> b
        b'\x05Hello'

        >>> s2, consumed = String.from_bytes(b)
        >>> s2.value
        'Hello'
        >>> consumed
        6

    Notes:
        - The UTF-16 code unit limit ensures compatibility with the official protocol.
        - The UTF-8 byte length limit ensures the length prefix fits in a 3-byte VarInt.
        - Offset support in `from_bytes` allows parsing a string embedded inside a packet buffer.
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
    def from_bytes(cls, data: bytes, offset: int = 0) -> tuple["String", int]:
        """Deserialize a String from a byte buffer starting at `offset`.

        Args:
            data (bytes): Byte buffer containing the string.
            offset (int, optional): Starting index in the buffer. Defaults to 0.

        Returns:
            tuple[String, int]: A tuple containing:
                - String instance
                - Number of bytes consumed (length VarInt + UTF-8 string)

        Raises:
            ValueError: If data is too short for the expected string length.
        """
        length_varint, varint_size = VarInt.from_bytes(data, offset)
        str_len = length_varint.value
        start = offset + varint_size
        end = start + str_len

        if len(data) < end:
            raise ValueError("Data too short for expected string length")

        utf8_bytes = data[start:end]
        value = utf8_bytes.decode("utf-8")
        total_consumed = varint_size + str_len
        return cls(value), total_consumed
