<!-- markdownlint-disable MD033 -->

# Minecraft Protocol Packets - Implementation Status

Reference: Java Edition Protocol  
Source: [Minecraft Wiki – Java Edition Protocol / Packets](https://minecraft.wiki/w/Java_Edition_protocol/Packets)

---

## Protocol Packet Standards

All implemented packets follow these standards:

1. **Packet Identification**
   - Each packet has a unique `packet_id` of type `VarInt`.
   - Packet ID identifies the packet type and corresponds to its protocol state (`Handshaking`, `Status`, `Login`, `Play`) and direction (`Serverbound` or `Clientbound`).

2. **State and Bound**
   - Packets are tied to a protocol state:
     - `Handshaking`: Initial client-server connection negotiation.
     - `Status`: Queries for server status and latency.
     - `Login`: Authentication and session setup.
     - `Play`: Game actions and world updates.
   - Packets are either `Serverbound` (sent from client) or `Clientbound` (sent from server).

3. **Field Types**
   - Packet fields are strongly typed and support serialization:
     - `VarInt`: Variable-length signed integer.
     - `UnsignedShort`: 16-bit unsigned integer.
     - `Long`: 64-bit signed integer.
     - `String`: UTF-8 string with VarInt length prefix.
     - `Enum`: Restricted set of values stored as VarInt.
   - Fields are yielded in the order required by the protocol for correct serialization.

4. **Initialization and Validation**
   - Packets validate input on creation (e.g., range checks for enums, correct field types).
   - Can accept raw bytes for deserialization where appropriate (e.g., server responses).

5. **Serialization**
   - `_iter_fields()` must be implemented to yield fields sequentially.
   - `serialize()` handles:
     - Adding the packet length prefix (VarInt).
     - Optional compression using zlib if packet size exceeds the threshold.
     - Enforcing protocol size limits for both compressed and uncompressed packets.
   - Ensures the serialized output is fully compatible with the Minecraft Java protocol.

6. **Memory Optimization**
   - `__slots__` is used in packet classes to reduce memory footprint and speed up frequent packet instantiation.

7. **Error Handling**
   - Invalid field types or out-of-range values raise exceptions (`TypeError` or `ValueError`) to prevent malformed packets from being sent.
   - Compression and packet length are strictly validated to comply with protocol restrictions.

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
<td>Status Request</td>
<td>0x00</td>
<td>Pending</td>
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
<td>Login Start</td>
<td>0x00</td>
<td>Player Name (String)</td>
<td>Initial login</td>
<td>Pending</td>
</tr>

<tr>
<td>Encryption Response</td>
<td>0x01</td>
<td>Shared Secret<br>Verify Token</td>
<td>Online-mode auth</td>
<td>Pending</td>
</tr>

<tr>
<td>Login Plugin Response</td>
<td>0x02</td>
<td>Message ID<br>Data</td>
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
<td>Reason (Text)</td>
<td>Login failure</td>
<td>Pending</td>
</tr>

<tr>
<td>Encryption Request</td>
<td>0x01</td>
<td>
Server ID<br>
Public Key<br>
Verify Token
</td>
<td>Online-mode</td>
<td>Pending</td>
</tr>

<tr>
<td>Login Success</td>
<td>0x02</td>
<td>UUID<br>Username</td>
<td>Switches to Play</td>
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
<td>Message ID<br>Channel<br>Data</td>
<td>Custom plugins</td>
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
