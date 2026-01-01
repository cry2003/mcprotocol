# src/codec/data_types/primitives/varlong.py

from dataclasses import dataclass
from ..constants import _SEGMENT_BITS, _CONTINUE_BIT, _MAX_VARLONG


@dataclass(slots=True, frozen=True)
class VarLong:
    """Represents a variable-length 64-bit signed integer in Minecraft protocol format.

    Encodes integers using 1 to 10 bytes, where each byte uses 7 bits for value
    and the most significant bit (MSB) as a continuation flag.

    Attributes:
        value (int): The integer value to be encoded (0 to _MAX_VARLONG).
    """

    value: int

    def __post_init__(self) -> None:
        """Validate the integer value after initialization.

        Raises:
            ValueError: If the value is not between 0 and _MAX_VARLONG.
        """
        if not 0 <= self.value <= _MAX_VARLONG:
            raise ValueError("VarLong must be between 0 and 18446744073709551615")

    def __bytes__(self) -> bytes:
        """Convert the integer to its variable-length byte representation.

        Returns:
            bytes: The VarLong-encoded bytes.
        """
        value = self.value
        result = bytearray()
        while True:
            if (value & ~_SEGMENT_BITS) == 0:
                result.append(value)
                break
            result.append((value & _SEGMENT_BITS) | _CONTINUE_BIT)
            value >>= 7
        return bytes(result)
