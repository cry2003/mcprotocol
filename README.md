# Minecraft Protocol (mcprotocol)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue)](LICENSE)

A compact, type-safe Python library that implements a **Minecraft protocol codec** (Java Edition). The project provides a complete type system with primitives, complex types, and packet classes for encoding and decoding Minecraft network traffic, following the official protocol specification.

- **Core**: Protocol-compliant encoding/decoding for packet bodies, length framing, and optional zlib compression.
- **Goal**: Safe, testable building blocks for implementing clients, bots, testing tools, or servers that speak the Minecraft Java Edition protocol.
- **Architecture**: Clean separation between type definitions, packet structures, and network I/O.

---

## Features

- **Comprehensive type system**:
  - Primitives: `Boolean`, `Byte`, `Int`, `Long`, `UnsignedShort`, `String`, `UUID`, `VarInt`, `VarLong`, `Enum`, and more.
  - Complex types: `Array`, `PrefixedArray`, `JSONTextComponent` with automatic serialization.
  - Base class `DataType` ensures consistent behavior across all types.

- **Protocol-compliant packet handling**:
  - Uncompressed and zlib-compressed packet support with automatic threshold-based switching.
  - Strict adherence to Minecraft packet framing (VarInt length prefixes, size limits).
  - Packet ID management and state-aware packet routing.

- **Fail-fast validation**:
  - All values validated at construction time (no silent errors).
  - Range checking for integers, length validation for strings/arrays.
  - Descriptive error messages with expected vs. actual values.

- **Extensible packet architecture**:
  - Define new packets by subclassing `Packet` and implementing `_iter_fields()`.
  - Support for both serverbound (client→server) and clientbound (server→client) packets.
  - Organized by protocol state: Handshaking, Status, Login, Play.

- **Pure Python, dependency-free**:
  - No external runtime dependencies required.
  - Python 3.9+ (uses dataclasses with `slots` and `frozen`).

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

### 1. Using Primitives

All primitives inherit from `DataType` and provide `__bytes__()` for serialization and `from_bytes()` for deserialization:

```python
from src.codec.data_types.primitives.varint import VarInt
from src.codec.data_types.primitives.string import String
from src.codec.data_types.primitives.unsigned_short import UnsignedShort

# Create and serialize primitives
version = VarInt(773)
address = String("localhost")
port = UnsignedShort(25565)

print(bytes(version))   # b'\xf5\x06'
print(bytes(address))   # VarInt length prefix + UTF-8 encoded string
print(bytes(port))      # b'\\x64\\x4d' (25565 in big-endian)

# Deserialize
version_decoded = VarInt.from_bytes(b'\xf5\x06')
print(version_decoded.value)  # 773
```

### 2. Creating a Custom Packet

Define packets by subclassing `Packet` and implementing `_iter_fields()`:

```python
from src.codec.packets.packet import Packet
from src.codec.data_types.primitives.varint import VarInt
from src.codec.data_types.primitives.string import String
from src.codec.data_types.primitives.unsigned_short import UnsignedShort
from src.codec.data_types.primitives.enum import Enum

class Intention(Packet):
    """Handshake packet (serverbound, packet state: Handshaking)."""
    
    __slots__ = ("protocol_version", "server_address", "server_port", "next_state")
    
    def __init__(self, protocol_version: int, server_address: str, server_port: int, next_state: int):
        super().__init__(packet_id=VarInt(0x00))
        self.protocol_version = VarInt(protocol_version)
        self.server_address = String(server_address)
        self.server_port = UnsignedShort(server_port)
        self.next_state = Enum(next_state, VarInt)  # 1=Status, 2=Login, 3=Transfer
    
    def _iter_fields(self):
        yield self.protocol_version
        yield self.server_address
        yield self.server_port
        yield self.next_state

# Serialize without compression
packet = Intention(773, "mc.example.com", 25565, 2)
data = packet.serialize()  # Returns bytes ready for transmission
print(f"Packet size: {len(data)} bytes")

# Serialize with compression threshold (e.g., 256 bytes)
data_compressed = packet.serialize(compression_threshold=256)
print(f"Compressed packet size: {len(data_compressed)} bytes")
```

### 3. Using Complex Types

Combine primitives into structured data:

```python
from src.codec.data_types.complex.prefixed_array import PrefixedArray
from src.codec.data_types.primitives.byte import Byte

# Create an array of bytes with VarInt length prefix
public_key_bytes = PrefixedArray([71, 34, 122, 19, 8, ...])
print(bytes(public_key_bytes))  # VarInt(length) + raw bytes
```

### 4. Available Packet Types

Pre-implemented packets organized by protocol state:

#### Handshaking (State 0)

- `Intention` (serverbound, 0x00): Initiates connection
- `LegacyServerListPing` (serverbound, 0xFE): Legacy ping support

#### Status (State 1)

- `StatusRequest` (serverbound, 0x00): Request server status
- `PingRequest` (serverbound, 0x01): Send ping with payload
- `StatusResponse` (clientbound, 0x00): Server status JSON
- `PongResponse` (clientbound, 0x01): Ping response

#### Login (State 2)

- `Hello` (serverbound, 0x00): Send username and UUID
- `Hello` (clientbound, 0x01): Server encryption/auth request
- `LoginDisconnect` (clientbound, 0x00): Disconnect during login

#### Play (State 3)

- Coming soon...

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

## Packet Compression

The library automatically handles packet compression when a threshold is provided:

```python
# No compression (development/testing)
serialized = packet.serialize(compression_threshold=None)

# Enable compression with 256 byte threshold
serialized = packet.serialize(compression_threshold=256)
```

**Compression behavior:**

- `compression_threshold = None` → all packets uncompressed: `[VarInt: body_len][body]`
- `compression_threshold >= 0`:
  - Packets < threshold: `[VarInt: packet_len][VarInt: 0][body]`
  - Packets >= threshold: `[VarInt: packet_len][VarInt: original_len][zlib_compressed_body]`

---

## Testing

Run tests from the workspace root:

```bash
python -m pytest debug/test/
```

---

## API Reference

### DataType Base Class

All primitives and complex types inherit from `DataType`:

```python
from src.codec.data_types.data_type import DataType

class MyType(DataType):
    def __bytes__(self) -> bytes:
        """Serialize to bytes."""
        pass
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "MyType":
        """Deserialize from bytes."""
        pass
```

### Primitive Types

| Type | Size | Range / Notes | Example |
| ------ | ------ | --------------- | --------- |
| `Boolean` | 1 byte | `0x00` (False) or `0x01` (True) | `Boolean(True)` |
| `Byte` | 1 byte | -128 to 127 | `Byte(-50)` |
| `Int` | 4 bytes | -2³¹ to 2³¹-1 | `Int(12345)` |
| `Long` | 8 bytes | -2⁶³ to 2⁶³-1 | `Long(9223372036854775807)` |
| `UnsignedShort` | 2 bytes | 0 to 65535 | `UnsignedShort(25565)` |
| `String` | Variable | UTF-8 + VarInt length (max 32767 chars) | `String("hello")` |
| `UUID` | 16 bytes | 128-bit UUID | `UUID(uuid.uuid4())` |
| `VarInt` | 1-5 bytes | Variable-length 32-bit int | `VarInt(300)` |
| `VarLong` | 1-10 bytes | Variable-length 64-bit int | `VarLong(99999999999)` |
| `Enum` | Depends on base | Restricted integer set | `Enum(2, VarInt)` |

### Complex Types

| Type | Purpose |
| ------ | --------- |
| `Array[T]` | Fixed-length array of items |
| `PrefixedArray[T]` | Array with VarInt length prefix |
| `JSONTextComponent` | Minecraft chat component (JSON) |

### Packet Class

```python
class Packet(ABC):
    def __init__(self, packet_id: VarInt) -> None:
        """Initialize with packet ID."""
    
    @abstractmethod
    def _iter_fields(self) -> Iterable[bytes]:
        """Yield field bytes in protocol order."""
    
    def serialize(self, compression_threshold: Optional[int] = None) -> bytes:
        """Serialize packet with optional compression."""
```

---

## Example: status `PongResponse`

A serverbound or clientbound response class can accept raw bytes or typed values. Example shows constructing a simple `PongResponse` for the status state:

---

## Contributing

- Follow existing code conventions: classes in `CamelCase`, functions and methods in `snake_case`, docstrings for public API.
- Add unit tests for any new primitive or packet. Tests should demonstrate both valid and invalid inputs.
- Ensure all new primitives and packets validate input and follow the contract described above.

---

## License

This project is licensed under the GNU General Public License v3 (GPL-3.0). See the `LICENSE` file for details.
