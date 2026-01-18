# Minecraft Protocol (mcprotocol)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue)](LICENSE)

A compact Python library that implements a **Minecraft protocol codec** (Java Edition). The project provides typed primitives, complex types and packet classes for encoding and decoding Minecraft network traffic, following the official protocol specification.

- Repository: protocol-compliant encoding/decoding for packet bodies, length framing and optional zlib compression.
- Goal: safe, testable building blocks for implementing clients, bots, testing tools or servers that speak the Minecraft Java Edition protocol.

---

## Features

- Strictly typed primitive and complex data types:
  - `Boolean`, `UnsignedShort`, `String`, `UUID`, `VarInt`, `VarLong`, `Long`, `Enum` and more.

- Packet serialization / deserialization:
  - Support for compressed and uncompressed packets (zlib compression).
  - Enforces framing rules and size limits (VarInt length prefixes, max body length).

- Fail-fast data validation:
  - Strings, integers and UUID values validated at construction time.

- Extensible packet model:
  - Define new packets by subclassing `Packet` and implementing `_iter_fields()`.

- Small, dependency-free codebase:
  - Pure Python; no external runtime dependencies required.

---

## Requirements

- Python 3.9+ (dataclasses with `slots` and `frozen` are used).
- No third-party dependencies are necessary for core functionality.

---

## Installation

Clone the repository and import it in your project:

```bash
git clone https://github.com/your-username/mcprotocol.git
cd mcprotocol
```

Use the package in your code by adding `src` to `PYTHONPATH` or installing the package into a virtualenv (project-specific packaging not provided by default).

Example running from repo root:

```bash
python -m src.main
```

---

## Quickstart

This quickstart shows constructing primitives and serializing a packet. The `Packet` base class handles packet id framing and optional compression. Subclasses provide the `packet_id` and implement `_iter_fields()` to yield serialized field bytes.

### Handshake packet example (corrected)

Use primitives directly; do not mix raw `to_bytes` calls inside `_iter_fields()` — yield primitives or other bytes-ready objects.

```python
from codec.data_types.primitives.varint import VarInt
from codec.data_types.primitives.string import String
from codec.data_types.primitives.unsigned_short import UnsignedShort
from codec.data_types.primitives.enum import Enum
from codec.packets.packet import Packet

class HandshakePacket(Packet):
    """
    Handshake (clientbound or serverbound depending on state) example.
    Packet ID: 0x00 (VarInt)
    Fields: protocol_version (VarInt), server_address (String), server_port (UnsignedShort), intent (Enum[VarInt])
    """
    def __init__(self, protocol_version: int, server_address: str, server_port: int, intent: int):
        # packet_id must be provided as VarInt when initializing Packet base
        super().__init__(packet_id=VarInt(0x00))

        # validate intent externally or rely on Enum wrapper
        self.protocol_version = VarInt(protocol_version)
        self.server_address = String(server_address)
        self.server_port = UnsignedShort(server_port)
        # Enum stores its value and encodes via the specified base type
        self.intent = Enum(intent, VarInt)

    def _iter_fields(self):
        yield self.protocol_version
        yield self.server_address
        yield self.server_port
        yield self.intent

# Serialize without compression
packet = HandshakePacket(773, "localhost", 25565, 2)
serialized = packet.serialize()  # compression_threshold defaults to None (no compression)
print(serialized)  # bytes ready for sending on a TCP socket
```

### Compression example

`Packet.serialize(compression_threshold: Optional[int])` accepts either `None` (no compression) or a non-negative integer threshold.

- `None` → uncompressed frame: `[VarInt: body_len][body]`
- `threshold >= 0`:
  - if `body_len < threshold`: send `Data Length = VarInt(0)` and `Packet Length = VarInt(len(Data Length) + body_len)`, then `Data Length + body`
  - if `body_len >= threshold`: compress `body` with `zlib.compress`, `Data Length = VarInt(body_len)`, `Packet Length = VarInt(len(Data Length) + len(compressed))`, then `Packet Length + Data Length + compressed_body`

Example with compression threshold of 256 bytes:

```python
serialized_compressed = packet.serialize(compression_threshold=256)
```

---

## Example: status `PongResponse`

A serverbound or clientbound response class can accept raw bytes or typed values. Example shows constructing a simple `PongResponse` for the status state:

```python
from codec.packets.packet import Packet
from codec.data_types.primitives.long import Long
from codec.data_types.primitives.varint import VarInt

class PongResponse(Packet):
    def __init__(self, timestamp: int):
        super().__init__(packet_id=VarInt(0x01))
        self.timestamp = Long(timestamp)

    def _iter_fields(self):
        yield self.timestamp

pong = PongResponse(1234567890123456789)
data = pong.serialize()
```

---

## API summary

### Primitives

All primitives follow the same contract:

- Implement `__bytes__()` returning the protocol-compliant byte representation.
- Validate input during construction and raise `ValueError` for invalid values.
- Prefer `@dataclass(slots=True, frozen=True)`.

Common primitives and methods:

- `VarInt(value: int)`
  - `__bytes__()` — 1–5 bytes varint encoding
  - `from_bytes(data, offset=0) -> (VarInt, bytes_consumed)`

- `VarLong(value: int)`
  - `__bytes__()` — 1–10 bytes varlong encoding

- `String(value: str)`
  - `__bytes__()` — VarInt length + UTF-8 bytes
  - `from_bytes(data, offset=0) -> (String, bytes_consumed)`

- `UnsignedShort(value: int)`
  - `__bytes__()` — 2 bytes big-endian

- `Long(value: int)`
  - `__bytes__()` — 8 bytes big-endian signed
  - `from_bytes(data) -> Long`

- `UUID(value: uuid.UUID | str)`
  - `__bytes__()` — 16 bytes big-endian
  - `decode(buf, offset=0) -> (UUID, 16)`

- `Boolean(value: bool)`
  - `__bytes__()` — single byte: `0x00` or `0x01`

- `Enum(value: int, base_type: Type)`
  - Encapsulates an integer and encodes via `base_type` (commonly `VarInt`)

### Packet

`Packet` is an abstract base class. Contract:

- `__init__(packet_id: VarInt)`
- `_iter_fields()` must yield byte-serializable fields in the exact order required by the protocol.
- `serialize(compression_threshold: Optional[int] = None) -> bytes` returns a fully framed packet (length prefix + optional compression wrapper + body).
- `__str__()` returns a concise, human-friendly representation (packet name, id and public fields).

---

## Contributing

- Follow existing code conventions: classes in `CamelCase`, functions and methods in `snake_case`, docstrings for public API.
- Add unit tests for any new primitive or packet. Tests should demonstrate both valid and invalid inputs.
- Ensure all new primitives and packets validate input and follow the contract described above.

---

## License

This project is licensed under the GNU General Public License v3 (GPL-3.0). See the `LICENSE` file for details.
