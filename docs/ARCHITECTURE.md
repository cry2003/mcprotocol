# Minecraft Codec — Architecture

This document outlines responsibilities, contracts, and expected behaviors of modules in the `mcprotocol` project. It focuses on **type validation, serialization, and protocol compliance**, excluding the directory structure.

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

## Overview

This document defines formal contracts between components of the Minecraft codec (primitive types, complex types, packets, network layer) and specifies invariants to ensure compatibility with the Java Edition protocol. Key requirements include:

* Correct encoding/decoding
* Fail-fast validation
* Readability and maintainability
* Extensibility for future packet types

---

## Module Responsibilities

### `data_types.primitives`

**Primary responsibilities:**

* Provide immutable, memory-efficient implementations of all protocol primitive types.
* Implement `__bytes__()` for protocol-compliant serialization.
* Provide deserialization methods where applicable (`from_bytes` or `decode()`), with integrity checks.
* Validate values at construction to prevent invalid data.

**Contract for each primitive:**

* Use `@dataclass(slots=True, frozen=True)` unless justified otherwise.
* `__bytes__()` must return bytes ready to concatenate into a packet body.
* If `from_bytes`/`decode(buf, offset)` exists:

  * Return `(instance, bytes_consumed)`
  * Raise `ValueError` if data is incomplete or malformed.

**Implemented primitives:**

* `Boolean` — 1 byte (`0x00` = False, `0x01` = True)
* `Enum` — integer restricted to a predefined set; encoded via a base type (VarInt, UnsignedShort)
* `Long` — signed 64-bit integer, big-endian
* `UnsignedShort` — 16-bit unsigned integer, big-endian
* `String` — UTF-8 string prefixed by VarInt length; max 32767 UTF-16 code units
* `UUID` — 128-bit value (16 bytes), big-endian (MSB + LSB)
* `VarInt` — variable-length 32-bit integer (1–5 bytes)
* `VarLong` — variable-length 64-bit integer (1–10 bytes)

---

### `data_types.complex`

**Primary responsibilities:**

* Compose primitives and other complex types into higher-level structures (e.g., `Position`, `EntityMetadata`).
* Expose `__bytes__()` and optionally `from_bytes()`/`decode()` for incremental parsing.
* Validate collective constraints (e.g., coordinate ranges, array lengths).

**Contract:**

* No I/O or network logic.
* Reusable by multiple packets without circular dependencies.

---

### `packets`

**Primary responsibilities:**

* Define common packet behavior through the `Packet` base class.
* Serialize packets with optional zlib compression.
* Enforce protocol rules:

  * Maximum packet size
  * VarInt length prefix ≤ 3 bytes
  * Compression thresholds for large packets

**`Packet` contract:**

* `packet_id: VarInt` (provided in constructor)
* Abstract `_iter_fields()` method yields serialized field bytes in network order.
* `serialize(compression_threshold: Optional[int]) -> bytes`:

  * Builds `body = packet_id + concatenated fields`.
  * If `compression_threshold is None` → uncompressed with `VarInt(body_len)` as length prefix.
  * If `compression_threshold >= 0`:

    * If `body_len < threshold`: `Data Length = VarInt(0)`, `Packet Length = VarInt(len(data_length) + body_len)`, return `packet_length + data_length + body`.
    * If `body_len >= threshold`: compress body with `zlib.compress`, `Data Length = VarInt(body_len)`, `Packet Length = VarInt(len(data_length) + len(compressed_body))`, return `packet_length + data_length + compressed_body`.
  * Validate body length, packet length, and VarInt length prefix ≤ 3 bytes; raise `ValueError` if exceeded.
* Use `__slots__` for memory efficiency.
* `__str__` provides concise representation with `packet_id` and public fields only.

---

### `constants.py`

* `data_types/constants.py`: primitive type constants (limits, defaults, segment bits, max values)
* `packets/constants.py`: packet limits and serialization parameters (max packet length, compression thresholds)
* Private constants use a leading `_` and must be documented.

---

### `network` (e.g., `packet_io.py`)

* Handles reading/writing packets over sockets (framing, decompression, VarInt length prefix parsing).
* Responsibilities:

  * Read VarInt packet length
  * Read payload
  * Decompress if necessary (`data_length != 0`)
  * Delegate field parsing to packet registry
* Should **not** create or construct packets — this is the responsibility of the `packets` module.

---

### `main.py`

* Entry point for demos and manual tests.
* Shows examples of packet construction and serialization.
* Should not contain reusable production logic.

---

## Design Principles

1. **Fail-fast**: all constructors and parsers validate input immediately; raise `TypeError` or `ValueError` with descriptive messages.
2. **Immutability**: primitives and complex types are frozen to prevent side effects in multi-packet usage.
3. **Deterministic serialization**: `_iter_fields()` defines the only order of bytes in a packet; order must match the protocol spec.
4. **Separation of concerns**: network parsing, packet construction, and type definitions are isolated.
5. **Use `__slots__`** where appropriate to reduce memory footprint in high-frequency packet scenarios.
6. **Explicit error handling**: error messages must include observed values and expected limits.
7. **Embedded documentation**: every public type and class must have docstrings specifying encoding, limits, and usage examples.

---

## Packet Serialization & Compression Contract

`Packet.serialize(compression_threshold)` workflow:

1. Build `body`:

   * `body = bytes(packet.packet_id)` (VarInt)
   * `body.extend(bytes(field))` for each field in `_iter_fields()`
2. Compute `body_len = len(body)`

   * If `body_len > _MAX_UNCOMPRESSED_SERVERBOUND` → raise `ValueError`
3. If `compression_threshold is None`:

   * `length_prefix = bytes(VarInt(body_len))`
   * Validate `len(length_prefix) ≤ 3`
   * Return `length_prefix + body`
4. If `threshold >= 0`:

   * If `body_len < threshold`:

     * `data_length = bytes(VarInt(0))`
     * `packet_length = bytes(VarInt(len(data_length) + body_len))`
     * Validate `len(packet_length) ≤ 3`
     * Return `packet_length + data_length + body`
   * If `body_len >= threshold`:

     * `compressed = zlib.compress(body)`
     * `data_length = bytes(VarInt(body_len))`
     * `packet_length = bytes(VarInt(len(data_length) + len(compressed)))`
     * Validate `len(packet_length) ≤ 3`
     * Return `packet_length + data_length + compressed`

* `compression_threshold` must be `None` or `>= 0`; otherwise raise `ValueError`
* `data_length` indicates uncompressed size to the receiver
