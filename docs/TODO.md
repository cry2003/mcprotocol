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

## Integration / Testing

1. Add integration tests for `StoreCookie` decode + runtime storage behavior.
2. Add integration tests for `Transfer` packet handling and reconnect flow.
3. Add regression tests to ensure cookies survive transfer.
