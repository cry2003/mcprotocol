<!-- markdownlint-disable MD033 -->

# Minecraft Protocol Types - Implementation Status

This table is based on the official Minecraft protocol data types. Status indicates whether the type is already implemented in this project.

---

## 1. Primitives

<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Size (bytes)</th>
      <th>Encodes / Notes</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Boolean</td>
      <td>1</td>
      <td>Either false or true (0x00 = false, 0x01 = true)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Byte</td>
      <td>1</td>
      <td>Signed 8-bit integer (-128 to 127)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Unsigned Byte</td>
      <td>1</td>
      <td>Unsigned 8-bit integer (0 to 255)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Short</td>
      <td>2</td>
      <td>Signed 16-bit integer (-32768 to 32767)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Unsigned Short</td>
      <td>2</td>
      <td>Unsigned 16-bit integer (0 to 65535)</td>
      <td>Implemented</td>
    </tr>
    <tr>
      <td>Int</td>
      <td>4</td>
      <td>Signed 32-bit integer (-2³¹ to 2³¹-1)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Long</td>
      <td>8</td>
      <td>Signed 64-bit integer (-2⁶³ to 2⁶³-1)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Float</td>
      <td>4</td>
      <td>Single-precision 32-bit IEEE 754 floating point</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Double</td>
      <td>8</td>
      <td>Double-precision 64-bit IEEE 754 floating point</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>String (n)</td>
      <td>≥1 ≤ (n×3)+3</td>
      <td>
        UTF-8 string prefixed with its size as a VarInt; max n = 32767 UTF-16
        code units
      </td>
      <td>Implemented</td>
    </tr>
    <tr>
      <td>VarInt</td>
      <td>≥1 ≤5</td>
      <td>Variable-length signed 32-bit integer; LEB128-like</td>
      <td>Implemented</td>
    </tr>
    <tr>
      <td>VarLong</td>
      <td>≥1 ≤10</td>
      <td>Variable-length signed 64-bit integer; LEB128-like</td>
      <td>Implemented</td>
    </tr>
    <tr>
      <td>UUID</td>
      <td>16</td>
      <td>Encoded as unsigned 128-bit integer (or two 64-bit integers)</td>
      <td>Implemented</td>
    </tr>
    <tr>
      <td>Angle</td>
      <td>1</td>
      <td>Rotation in steps of 1/256 of a full turn</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Position</td>
      <td>8</td>
      <td>
        Packed 64-bit integer: x 26 bits, z 26 bits, y 12 bits, signed two’s
        complement
      </td>
      <td>Pending</td>
    </tr>
  </tbody>
</table>

--- ## 2. Structured / Complex Types

<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Size / Notes</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Text Component</td>
      <td>Varies; see Text component format</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>JSON Text Component</td>
      <td>≥1 ≤ (262144×3)+3</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Identifier</td>
      <td>≥1 ≤ (32767×3)+3</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Entity Metadata</td>
      <td>Varies; miscellaneous entity info</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Slot</td>
      <td>Varies; item stack in inventory</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Hashed Slot</td>
      <td>Varies; slot data sent as hash</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>NBT</td>
      <td>Varies; Named Binary Tag</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>BitSet</td>
      <td>Varies; length-prefixed bit set</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Fixed BitSet (n)</td>
      <td>ceil(n / 8)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Optional X</td>
      <td>0 or size of X</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Prefixed Optional X</td>
      <td>size of Boolean + (is present ? size of X : 0)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Array of X</td>
      <td>length × size of X</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Prefixed Array of X</td>
      <td>VarInt length + size of X × length</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>X Enum</td>
      <td>size of X</td>
      <td>Implemented</td>
    </tr>
    <tr>
      <td>EnumSet (n)</td>
      <td>ceil(n / 8)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Byte Array</td>
      <td>Varies</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>ID or X</td>
      <td>VarInt + (size of X or 0)</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>ID Set</td>
      <td>Varies</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Sound Event</td>
      <td>Varies; parameters for a sound event</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Chat Type</td>
      <td>Varies; parameters for direct chat</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Teleport Flags</td>
      <td>4</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Recipe Display</td>
      <td>Varies; see Recipes#Recipe Display</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Slot Display</td>
      <td>Varies; see Recipes#Slot Display</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Chunk Data</td>
      <td>Varies; see #Chunk Data</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Light Data</td>
      <td>Varies; see #Light Data</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Game Profile</td>
      <td>Varies; UUID + username + properties</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Resolvable Profile</td>
      <td>Varies; partial or complete game profile</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Debug Subscription Event</td>
      <td>Varies; see #Debug Subscription Event</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>Debug Subscription Update</td>
      <td>Varies; see #Debug Subscription Update</td>
      <td>Pending</td>
    </tr>
    <tr>
      <td>LpVec3</td>
      <td>Varies; usually used for low velocities</td>
      <td>Pending</td>
    </tr>
  </tbody>
</table>
