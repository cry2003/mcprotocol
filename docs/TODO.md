# TODO

This file tracks pending work that is intentionally outside the pure codec layer.

## Client Runtime

1. Implement cookie persistence for `StoreCookie` (`Configuration`, `0x0A`).
2. Add a cookie store keyed by `Identifier`.
3. Enforce per-cookie size limit (5 KiB) when storing/replacing values.
4. Preserve cookies across server transfer flow.

## Transfer Flow

1. Handle `Transfer` (`Configuration`, `0x0B`) at runtime:
2. Close current connection.
3. Connect to target `host:port`.
4. Send Handshake with intent `3` (Transfer).
5. Continue with normal login flow if accepted.

## Registry / Tag Session State (MC-249007 semantics)

1. Add a stateful registry/tag store across configuration/play phases.
2. Apply `UpdateTags` (`Configuration`, `0x0D`) as per-tag replacement (not full registry reset).
3. If `FinishConfiguration` arrives without any `RegistryData` in that phase, retain previously known synchronized registry tags.
4. If any `RegistryData` is received during reconfiguration, forget previous synchronized registries and their tags before applying new data.
5. Support tag updates in Play state against the same runtime store.
6. Add regression tests for the above retention/reset behavior.

## Chat Runtime / App-Layer Policy

1. Add client preference policy for `ClientInformation.chat_mode`:
2. Enforce outbound behavior:
3. Full: allow chat messages + chat commands.
4. Commands only: allow commands, block normal chat messages.
5. Hidden: block chat messages and chat commands.
6. Enforce inbound filtering policy:
7. Hidden: suppress non-overlay system/player chat in UI layer.
8. Commands only: suppress player/disguised chat, allow command/system feedback.
9. Keep overlay system messages visible regardless of mode.
10. Add runtime tests for mode matrix behavior.

## Social Interactions / Blocking

1. Add blocklist-aware filtering for player chat by sender UUID.
2. Add optional “hide matched names” policy for system chat text.
3. Keep disguised chat unblocked by social filtering rules.
4. Add tests for blocked/unblocked message paths.

## Mojang/Microsoft Services Integration (Optional Runtime)

1. Add optional API client module (not in codec core) for:
2. Querying `/player/attributes` (profanity filter preferences and privileges).
3. Querying `/privacy/blocklist` (blocked profiles).
4. Optional profile lookup helpers for account metadata.
5. Add token-management and retry/backoff handling for rate-limited endpoints.
6. Add clear fallback behavior when APIs are unavailable or offline-mode is used.

## Client Information Persistence

1. Persist latest `ClientInformation` preferences in session/app settings.
2. Keep `chat_colors` value stored even if server does not enforce it (MC-64867).
3. Expose skin-part bitmask helpers for UI and settings screens.
4. Add integration tests for preference roundtrip serialization.

## Integration / Testing

1. Add integration tests for `StoreCookie` decode + runtime storage behavior.
2. Add integration tests for `Transfer` packet handling and reconnect flow.
3. Add regression tests to ensure cookies survive transfer.
