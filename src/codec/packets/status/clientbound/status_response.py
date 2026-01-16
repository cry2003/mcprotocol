import json
from typing import List, Optional
from codec.packets.packet import Packet
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.string import String


class StatusResponse(Packet):
    """
    Status Response packet (clientbound).

    Packet ID: 0x00
    State: Status
    Bound to: Client

    Contains a JSON-formatted string describing server status.
    The string is encoded as a Minecraft String (VarInt length + UTF-8 bytes).
    """

    __slots__ = (
        "_json_string",  # Raw JSON string for serialization
        "version_name",
        "version_protocol",
        "max_players",
        "online_players",
        "sample_players",
        "description",
        "favicon",
        "enforces_secure_chat",
    )

    def __init__(self, data: bytes) -> None:
        """
        Initialize from raw bytes received from the server.

        Args:
            data (bytes): Raw packet data containing a single String field.
        """
        super().__init__(VarInt(0x00))

        # Deserialize the JSON string
        string_field, _ = String.from_bytes(data)
        self._json_string = string_field.value

        # Parse JSON safely
        obj = json.loads(self._json_string)

        # Version info
        version = obj.get("version", {})
        self.version_name: str = version.get("name", "Unknown")
        self.version_protocol: int = version.get("protocol", -1)

        # Players info
        players = obj.get("players", {})
        self.max_players: int = players.get("max", 0)
        self.online_players: int = players.get("online", 0)
        self.sample_players: Optional[List[dict]] = players.get("sample", [])

        # Description (can be complex JSON)
        description_field = obj.get("description")
        if isinstance(description_field, dict) and "text" in description_field:
            self.description: str = description_field["text"]
        else:
            # fallback: serialize object as string
            self.description: str = (
                json.dumps(description_field) if description_field else ""
            )

        # Optional fields
        self.favicon: Optional[str] = obj.get("favicon")
        self.enforces_secure_chat: bool = obj.get("enforcesSecureChat", False)

    def _iter_fields(self):
        """Yield the JSON string as a single String field for serialization."""
        yield String(self._json_string)
