<!-- markdownlint-disable MD033 -->

# Minecraft Protocol Packets - Implementation Status

This table is based on the official Minecraft protocol Packet format. Status indicates whether the type is already implemented in this project.

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
      <td>Handshake</td>
      <td>0x00</td>
      <td>Server</td>
      <td>
        Protocol Version (VarInt)<br>
        Server Address (String, max 255)<br>
        Server Port (Unsigned Short)<br>
        Intent (VarInt Enum: 1=Status, 2=Login, 3=Transfer)
      </td>
      <td>Sent immediately after opening TCP connection. Causes server to switch to target state.</td>
      <td>Implemented</td>
    </tr>
    <tr>
      <td>Legacy Server List Ping (LSLP)</td>
      <td>0xFE</td>
      <td>Server</td>
      <td>Payload (Unsigned Byte, always 1)</td>
      <td>Nonstandard format for legacy clients (<=1.6). No length prefix. Modern servers should handle it correctly.</td>
      <td>Implemented</td>
    </tr>
  </tbody>
</table>
