<!-- markdownlint-disable MD033 -->

# Minecraft Protocol Packets - Implementation Reference

This document tracks the implementation status of all Minecraft protocol packets, organized by protocol state and direction.

**Reference:** [Minecraft Wiki – Java Edition Protocol / Packets](https://minecraft.wiki/w/Java_Edition_protocol/Packets)

---

## Packet Implementation Overview

| State | Direction | Total | Implemented | Status |
| ----- | --------- | ----- | ----------- | ------ |
| **Handshaking** | Serverbound | 2 | 2 ✓ | Complete |
| **Status** | Serverbound | 2 | 2 ✓ | Complete |
| **Status** | Clientbound | 2 | 2 ✓ | Complete |
| **Login** | Serverbound | 3 | 1 | WIP |
| **Login** | Clientbound | 5 | 1 | WIP |
| **Play** | Serverbound | 50+ | 0 | TODO |
| **Play** | Clientbound | 100+ | 0 | TODO |
| **Configuration** | Serverbound | 2 | 0 | TODO |
| **Configuration** | Clientbound | 5+ | 0 | TODO |

---

## Implementation Standards

All implemented packets follow these standards:

1. **Packet Identification**
   - Each packet has a unique `packet_id` of type `VarInt`.
   - Packet ID identifies the packet type and corresponds to its protocol state and direction.

2. **State and Direction**
   - **Handshaking** (0): Initial connection negotiation.
   - **Status** (1): Server status and latency queries.
   - **Login** (2): Player authentication and session setup.
   - **Play** (3): In-game updates and player actions.
   - **Configuration** (4): Protocol configuration (1.20+).
   - **Direction**: `Serverbound` (client→server) or `Clientbound` (server→client).

3. **Packet Structure**
   - All packets inherit from `Packet` base class.
   - Each packet defines `__slots__` for memory efficiency.
   - `_iter_fields()` yields fields in exact protocol order.
   - `serialize(compression_threshold)` handles framing and optional compression.

4. **Field Validation**
   - All field values validated at construction time.
   - Out-of-range values raise `ValueError` with descriptive messages.
   - Type mismatches raise `TypeError`.

5. **Testing**
   - Example test: [debug/test/test_login_disconnect_server.py](../../debug/test/test_login_disconnect_server.py)
   - Tests verify serialization and real Minecraft server connectivity.

---

## 1. Handshaking

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>Packet ID</th>
<th>Bound To</th>
<th>Fields (Type)</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>Intention</td>
<td>0x00</td>
<td>Server</td>
<td>
Protocol Version (VarInt)<br>
Server Address (String)<br>
Server Port (Unsigned Short)<br>
Next State (VarInt)
</td>
<td>Switches protocol state</td>
<td>Implemented</td>
</tr>

<tr>
<td>Legacy Server List Ping</td>
<td>0xFE</td>
<td>Server</td>
<td>Payload (Unsigned Byte)</td>
<td>Legacy ≤1.6 support</td>
<td>Implemented</td>
</tr>
</tbody>
</table>

---

## 2. Status

### Status Clientbound

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>ID</th>
<th>Fields</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>Status Response</td>
<td>0x00</td>
<td>JSON Response (String)</td>
<td>Server MOTD, players, version</td>
<td>Implemented</td>
</tr>

<tr>
<td>Pong Response</td>
<td>0x01</td>
<td>Payload (Long)</td>
<td>Ping reply</td>
<td>Implemented</td>
</tr>
</tbody>
</table>

### Status Serverbound

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>ID</th>
<th>Fields</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>Status Request</td>
<td>0x00</td>
<td>(none)</td>
<td>Empty packet to request status</td>
<td>Implemented</td>
</tr>
<td>Requests status</td>
<td>Implemented</td>
</tr>

<tr>
<td>Ping Request</td>
<td>0x01</td>
<td>Payload (Long)</td>
<td>Latency measurement</td>
<td>Implemented</td>
</tr>
</tbody>
</table>

---

## 3. Login

### Serverbound

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>ID</th>
<th>Fields</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>Hello</td>
<td>0x00</td>
<td>Name (String)<br>UUID (UUID, optional)</td>
<td>Initial login with username/UUID</td>
<td>Implemented</td>
</tr>

<tr>
<td>Encryption Response</td>
<td>0x01</td>
<td>Shared Secret (PrefixedArray[Byte])<br>Verify Token (PrefixedArray[Byte])</td>
<td>Online-mode auth</td>
<td>Pending</td>
</tr>

<tr>
<td>Login Plugin Response</td>
<td>0x02</td>
<td>Message ID (VarInt)<br>Data (PrefixedArray[Byte])</td>
<td>Custom login plugins</td>
<td>Pending</td>
</tr>
</tbody>
</table>

### Clientbound

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>ID</th>
<th>Fields</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>Disconnect</td>
<td>0x00</td>
<td>Reason (JSONTextComponent)</td>
<td>Login failure message</td>
<td>Implemented</td>
</tr>

<tr>
<td>Hello</td>
<td>0x01</td>
<td>
Server ID (String)<br>
Public Key (PrefixedArray[Byte])<br>
Verify Token (PrefixedArray[Byte])<br>
Should Authenticate (Boolean)
</td>
<td>Encryption request</td>
<td>Implemented</td>
</tr>

<tr>
<td>Login Success</td>
<td>0x02</td>
<td>UUID (UUID)<br>Username (String)</td>
<td>Switches to Play state</td>
<td>Pending</td>
</tr>

<tr>
<td>Set Compression</td>
<td>0x03</td>
<td>Threshold (VarInt)</td>
<td>Enables compression</td>
<td>Pending</td>
</tr>

<tr>
<td>Login Plugin Request</td>
<td>0x04</td>
<td>Message ID (VarInt)<br>Channel (String)<br>Data (PrefixedArray[Byte])</td>
<td>Custom authentication plugins</td>
<td>Pending</td>
</tr>
</tbody>
</table>

---

## 4. Play

### Serverbound (Play)

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>ID</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr><td>Confirm Teleportation</td><td>0x00</td><td>Teleport ACK</td><td>Pending</td></tr>
<tr><td>Query Block NBT</td><td>0x01</td><td>Block entity data</td><td>Pending</td></tr>
<tr><td>Set Difficulty</td><td>0x02</td><td>Legacy</td><td>Pending</td></tr>
<tr><td>Chat Command</td><td>0x03</td><td>Slash commands</td><td>Pending</td></tr>
<tr><td>Chat Message</td><td>0x04</td><td>Player chat</td><td>Pending</td></tr>
<tr><td>Client Status</td><td>0x05</td><td>Respawn, etc.</td><td>Pending</td></tr>
<tr><td>Client Settings</td><td>0x06</td><td>Locale, view distance</td><td>Pending</td></tr>
<tr><td>Interact Entity</td><td>0x07</td><td>Attack/use</td><td>Pending</td></tr>
<tr><td>Keep Alive</td><td>0x08</td><td>Connection keepalive</td><td>Pending</td></tr>
<tr><td>Player Position</td><td>0x09</td><td>Movement</td><td>Pending</td></tr>
<tr><td>Player Position and Rotation</td><td>0x0A</td><td>Movement</td><td>Pending</td></tr>
<tr><td>Player Rotation</td><td>0x0B</td><td>Look only</td><td>Pending</td></tr>
<tr><td>Player Movement</td><td>0x0C</td><td>On ground flag</td><td>Pending</td></tr>
<tr><td>Vehicle Move</td><td>0x0D</td><td>Vehicle control</td><td>Pending</td></tr>
<tr><td>Steer Boat</td><td>0x0E</td><td>Boat control</td><td>Pending</td></tr>
<tr><td>Pick Item</td><td>0x0F</td><td>Creative pick</td><td>Pending</td></tr>
<tr><td>Player Abilities</td><td>0x10</td><td>Flying, etc.</td><td>Pending</td></tr>
<tr><td>Player Digging</td><td>0x11</td><td>Block breaking</td><td>Pending</td></tr>
<tr><td>Entity Action</td><td>0x12</td><td>Sneak, sprint</td><td>Pending</td></tr>
<tr><td>Use Item On</td><td>0x13</td><td>Right click block</td><td>Pending</td></tr>
<tr><td>Use Item</td><td>0x14</td><td>Right click air</td><td>Pending</td></tr>
</tbody>
</table>

---

### Clientbound (Play)

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>ID</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr><td>Spawn Entity</td><td>0x00</td><td>Generic entity</td><td>Pending</td></tr>
<tr><td>Spawn Experience Orb</td><td>0x01</td><td>XP orb</td><td>Pending</td></tr>
<tr><td>Spawn Player</td><td>0x02</td><td>Player entity</td><td>Pending</td></tr>
<tr><td>Entity Animation</td><td>0x03</td><td>Swing arm</td><td>Pending</td></tr>
<tr><td>Award Statistics</td><td>0x04</td><td>Stats update</td><td>Pending</td></tr>
<tr><td>Acknowledge Block Change</td><td>0x05</td><td>Sync block state</td><td>Pending</td></tr>
<tr><td>Block Break Animation</td><td>0x06</td><td>Cracks</td><td>Pending</td></tr>
<tr><td>Block Entity Data</td><td>0x07</td><td>Tile entities</td><td>Pending</td></tr>
<tr><td>Block Action</td><td>0x08</td><td>Note blocks, etc.</td><td>Pending</td></tr>
<tr><td>Block Change</td><td>0x09</td><td>Single block</td><td>Pending</td></tr>
<tr><td>Boss Bar</td><td>0x0A</td><td>Boss HUD</td><td>Pending</td></tr>
<tr><td>Server Difficulty</td><td>0x0B</td><td>Difficulty</td><td>Pending</td></tr>
<tr><td>Chat Message</td><td>0x0C</td><td>System chat</td><td>Pending</td></tr>
<tr><td>Clear Titles</td><td>0x0D</td><td>Title reset</td><td>Pending</td></tr>
<tr><td>Disconnect</td><td>0x0E</td><td>Kick reason</td><td>Pending</td></tr>
<tr><td>Entity Status</td><td>0x1A</td><td>Hurt, death</td><td>Pending</td></tr>
<tr><td>Keep Alive</td><td>0x21</td><td>Latency</td><td>Pending</td></tr>
<tr><td>Player Position and Look</td><td>0x38</td><td>Teleport</td><td>Pending</td></tr>
<tr><td>Update Health</td><td>0x52</td><td>Health/food</td><td>Pending</td></tr>
<tr><td>Time Update</td><td>0x5E</td><td>World time</td><td>Pending</td></tr>
</tbody>
</table>

---

## 5. Configuration (1.20+)

<table>
<thead>
<tr>
<th>Packet Name</th>
<th>ID</th>
<th>Bound To</th>
<th>Notes</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr><td>Client Information</td><td>0x00</td><td>Server</td><td>Settings sync</td><td>Pending</td></tr>
<tr><td>Finish Configuration</td><td>0x02</td><td>Server</td><td>Ready for Play</td><td>Pending</td></tr>
<tr><td>Registry Data</td><td>0x05</td><td>Client</td><td>Dimension, biomes</td><td>Pending</td></tr>
</tbody>
</table>
