# Flow Lifecycle Specification

## Flow State Machine

```
  ┌──────────┐      Packet Received       ┌──────────┐
  │  Start   │ ─────────────────────────> │  ACTIVE  │
  └──────────┘                            └────┬─────┘
                                               │
               ┌───────────────────────────────┼───────────────────────────────┐
               │ Idle > 15s                    │ Active > 120s                 │ TCP FIN / RST
               ▼                               ▼                               ▼
     ┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
     │   IDLE_TIMEOUT   │            │  ACTIVE_TIMEOUT  │            │    TCP_CLOSED    │
     └────────┬─────────┘            └────────┬─────────┘            └────────┬─────────┘
              │                               │                               │
              └───────────────────────────────┼───────────────────────────────┘
                                              │ Push to FlowQueue
                                              ▼
                                   ┌─────────────────────┐
                                   │  Output Flow Queue  │
                                   └─────────────────────┘
```

---

## State Descriptions

- **`ACTIVE`**: Flow is actively accumulating incoming packets and byte counters.
- **`IDLE_TIMEOUT`**: Flow was evicted because no packets were observed for $> 15$ seconds.
- **`ACTIVE_TIMEOUT`**: Flow was evicted because total duration exceeded $> 120$ seconds.
- **`TCP_CLOSED`**: TCP session gracefully or abruptly terminated via FIN/RST control flags.
