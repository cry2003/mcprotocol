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

## Integration / Testing

1. Add integration tests for `StoreCookie` decode + runtime storage behavior.
2. Add integration tests for `Transfer` packet handling and reconnect flow.
3. Add regression tests to ensure cookies survive transfer.
