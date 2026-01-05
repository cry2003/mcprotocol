# Minecraft Protocol Codec

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue)](LICENSE)

A Python library implementing a **Minecraft protocol codec**. This project provides tools for encoding and decoding **packets** and **data types** used in Minecraft networking, fully compliant with the [official protocol specification](https://minecraft.wiki/w/Java_Edition_protocol/Packets).

## Features

- Fully typed **primitive and complex data types**:
  - `Boolean`, `UnsignedShort`, `String`, `UUID`, `VarInt`, `VarLong`, and more.
- **Packet serialization and deserialization** following Minecraft protocol:
  - Supports compressed and uncompressed packets.
  - Enforces maximum size limits.
- **Data validation**:
  - Ensures strings, integers, and UUIDs are within protocol-defined bounds.
- Designed for **serverbound and clientbound packets**.
- **Extensible**: easily add new packets or custom data types.

## Installation

Clone the repository:

````bash
git clone https://github.com/your-username/mcprotocol.git
cd mcprotocol
````

You can then import the codec in your Python project:

````python
from codec.data_types.primitives.string import String
from codec.packets.packet import Packet
````

No external dependencies required.

## Usage

Usage Example

````python
from codec.data_types.primitives import VarInt, String
from codec.packets.packet import Packet

class HandshakePacket(Packet):
    packet_id = VarInt(0x00)

    def __init__(self, protocol_version: int, server_address: str, server_port: int, intent: int):
        self.protocol_version = VarInt(protocol_version)
        self.server_address = String(server_address)
        self.server_port = server_port
        self.intent = VarInt(intent)

    def _iter_fields(self):
        yield self.protocol_version
        yield self.server_address
        yield self.server_port.to_bytes(2, "big")
        yield self.intent

packet = HandshakePacket(773, "localhost", 25565, 2)
serialized = packet.serialize()
print(serialized)
````

### Project Structure

```bash
mcprotocol
|   .gitignore
|   LICENSE.md
|   README.md
|   
+---docs
|       ARCHITECTURE.md
|       data_types.md
|       
\---src
    |   main.py
    |   
    \---codec
        |   __init__.py
        |   
        +---data_types
        |   |   constants.py
        |   |   
        |   \---primitives
        |           boolean.py
        |           long.py
        |           string.py
        |           unsigned_short.py
        |           uuid.py
        |           varint.py
        |           varlong.py
        |           
        \---packets
            |   constants.py
            |   packet.py
            |   registry.py
            |   __init__.py
            |   
            +---clientbound
            |   \---status
            |           pong_response.py
            |           status_response.py
            |           
            \---serverbound
````

## License

This project is licensed under the GNU General Public License v3 (GPL-3.0). See the LICENSE file for details.
