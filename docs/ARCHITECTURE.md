# Minecraft Codec Project Architecture

This document outlines the structure, responsibilities, and relationships of modules in the `mcprotocol` project.

---

## Project Structure

```text
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
    |   test_main.py
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

```

---

## Module Responsibilities

### `data_types/primitives`

- Define all **base types** used by the Minecraft protocol.
- Each primitive type:
  - Is **immutable** (`frozen=True` dataclass) and optionally `slots=True`.
  - Implements `__bytes__()` for serialization.
  - Validates values according to protocol limits.
- Examples: `Boolean`, `String`, `UnsignedShort`, `UUID`, `VarInt`, `VarLong`.

### `data_types/complex`

- Build **higher-level types** by combining primitives or other complex types.
- Example: `Position`, `EntityMetadata`, or custom packet fields.

### `packets`

- Implements the **base `Packet` class**:
  - Handles serialization with optional compression.
  - Enforces protocol rules (length limits, VarInt encoding size, compression thresholds).
- Subclasses must define `packet_id` and `_iter_fields()` to yield serialized fields.
- Contains packet-specific constants.

### `constants.py`

- **`data_types/constants.py`**: type-specific constants (limits, defaults, segment bits, etc.)
- **`packets/constants.py`**: packet-specific constants (max length, compression thresholds, etc.)

### `main.py`

- Entry point for testing or demonstrating packet construction and encoding.
- Shows example usage of primitives, complex types, and packets.

---

## Design Notes

- **Immutability**: All primitives are frozen dataclasses, ensuring safe usage in packets without accidental modification.
- **Serialization Logic**: Each type implements `__bytes__()`. Packet serialization is handled by `Packet.serialize()`, respecting Minecraft protocol limits.
- **Compression**: Packet serialization respects optional zlib compression thresholds and follows the official Minecraft specification.
- **Separation of Concerns**: Primitives, complex types, and packets are strictly separated to maintain clean modular architecture.
- **Private Constants**:
  - Private/internal constants use a leading underscore (e.g., `_DEFAULT_MAX_CODE_UNITS`) if meant only for the module.

---

## Relationships

- **Packets** depend on both **primitives** and **complex types** for field encoding.
- **Complex types** are composed of primitives and/or other complex types.
- **Primitives** are self-contained and independent.

---

## Notes

- The architecture is designed to be **modular, extendable, and protocol-compliant**.
- Adding new packet types or complex fields requires only subclassing `Packet` and/or creating new types in `complex`.
- All encoding rules strictly follow Minecraft protocol documentation for all data types, and packet serialization.
