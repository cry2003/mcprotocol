<!-- markdownlint-disable MD033 -->

# Minecraft Protocol Packets - Implementation Reference

This document tracks the implementation status of all Minecraft protocol packets, organized by protocol state and direction.

**Reference:** [Minecraft Wiki – Java Edition Protocol / Packets](https://minecraft.wiki/w/Java_Edition_protocol/Packets)

---

## Packet Implementation Overview

| State | Direction | Total (in repo) | Implemented | Status |
| ----- | --------- | --------------- | ----------- | ------ |
| **Handshaking** | Serverbound | 2 | 2 ✓ | Complete |
| **Status** | Serverbound | 2 | 2 ✓ | Complete |
| **Status** | Clientbound | 2 | 2 ✓ | Complete |
| **Login** | Serverbound | 5 | 5 ✓ | Complete |
| **Login** | Clientbound | 6 | 6 ✓ | Complete |
| **Configuration** | Clientbound | 12 | 12 ✓ | WIP |
| **Configuration** | Serverbound | 0 | 0 | TODO |
| **Play** | Serverbound | 0 | 0 | TODO |
| **Play** | Clientbound | 0 | 0 | TODO |

Totals above reflect packet classes currently implemented in this repository (not the full Minecraft protocol list).

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
   - No automated tests are currently tracked in this repository.

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
<td>Name (String)<br>UUID (UUID)</td>
<td>Initial login with username and UUID (UUID defaults to UUIDv5 if omitted)</td>
<td>Implemented</td>
</tr>

<tr>
<td>Encryption Response</td>
<td>0x01</td>
<td>Shared Secret (PrefixedArray[Byte])<br>Verify Token (PrefixedArray[Byte])</td>
<td>Online-mode auth</td>
<td>Implemented</td>
</tr>

<tr>
<td>Custom Query Answer</td>
<td>0x02</td>
<td>Message ID (VarInt)<br>Data (bytes)</td>
<td>Custom login plugins (payload optional)</td>
<td>Implemented</td>
</tr>

<tr>
<td>Login Acknowledged</td>
<td>0x03</td>
<td>(none)</td>
<td>Signals end of Login state</td>
<td>Implemented</td>
</tr>

<tr>
<td>Cookie Response</td>
<td>0x04</td>
<td>Key (Identifier)<br>Payload (PrefixedArray[Byte], optional)</td>
<td>Responds to cookie request</td>
<td>Implemented</td>
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
<td>Reason (JsonTextComponent)</td>
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
<td>Login Finished</td>
<td>0x02</td>
<td>Profile (GameProfile)</td>
<td>Final login success payload</td>
<td>Implemented</td>
</tr>

<tr>
<td>Set Compression</td>
<td>0x03</td>
<td>Threshold (VarInt)</td>
<td>Enables compression</td>
<td>Implemented</td>
</tr>

<tr>
<td>Custom Query</td>
<td>0x04</td>
<td>Message ID (VarInt)<br>Channel (Identifier)<br>Data (bytes)</td>
<td>Custom authentication plugins</td>
<td>Implemented</td>
</tr>

<tr>
<td>Cookie Request</td>
<td>0x05</td>
<td>Key (Identifier)</td>
<td>Requests a login cookie</td>
<td>Implemented</td>
</tr>
</tbody>
</table>

---

## 4. Play

No Play packets are implemented yet. This section will be populated once Play-state packet classes exist in `src/codec/packets/play/`.

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
<tr><td>Cookie Request</td><td>0x00</td><td>Client</td><td>Requests a configuration cookie</td><td>Implemented</td></tr>
<tr><td>Custom Payload</td><td>0x01</td><td>Client</td><td>Plugin channel payload during configuration</td><td>Implemented</td></tr>
<tr><td>Disconnect</td><td>0x02</td><td>Client</td><td>Disconnect reason as text component</td><td>Implemented</td></tr>
<tr><td>Finish Configuration</td><td>0x03</td><td>Client</td><td>Marks end of configuration phase</td><td>Implemented</td></tr>
<tr><td>Keep Alive</td><td>0x04</td><td>Client</td><td>Configuration keep-alive identifier</td><td>Implemented</td></tr>
<tr><td>Ping</td><td>0x05</td><td>Client</td><td>Configuration ping packet</td><td>Implemented</td></tr>
<tr><td>Reset Chat</td><td>0x06</td><td>Client</td><td>Reset chat state/settings</td><td>Implemented</td></tr>
<tr><td>Registry Data</td><td>0x07</td><td>Client</td><td>Synchronized registry entries (Identifier + optional NBT)</td><td>Implemented</td></tr>
<tr><td>Resource Pack Pop</td><td>0x08</td><td>Client</td><td>Remove resource pack by UUID (or all)</td><td>Implemented</td></tr>
<tr><td>Resource Pack Push</td><td>0x09</td><td>Client</td><td>Add resource pack metadata and optional prompt</td><td>Implemented</td></tr>
<tr><td>Store Cookie</td><td>0x0A</td><td>Client</td><td>Store cookie data on client (max 5 KiB)</td><td>Implemented</td></tr>
<tr><td>Transfer</td><td>0x0B</td><td>Client</td><td>Redirect client to another server host/port</td><td>Implemented</td></tr>
</tbody>
</table>

---

## Runtime TODO (Outside Codec Layer)

- Implement client cookie persistence behavior for `Store Cookie` (0x0A).
- Implement transfer workflow for `Transfer` (0x0B):
  - close current socket
  - connect to target host/port
  - send Handshake with intent `3`
  - continue login flow
