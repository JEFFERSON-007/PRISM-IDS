# Flow Generation Engine Architecture

The **Flow Generation Engine** converts raw packet streams into structured bidirectional 5-tuple network flows.

```
┌────────────────────────────────────────────────────────────┐
│                    Capture Engine Queue                    │
│                 (Pushes ParsedPacket DTOs)                 │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Flow Manager Worker                     │
│    (Extracts canonical 5-tuple & matches FlowDirection)    │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                   In-Memory Flow Table                     │
│    (Updates packet/byte counters & TCP connection state)   │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                 Flow Expiration Daemon                     │
│     (Checks Idle Timeout 15s & Active Timeout 120s)        │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                   Output Flow Queue                        │
│     (Buffers completed Flow records for Feature Engine)    │
└────────────────────────────────────────────────────────────┘
```

---

## 1. 5-Tuple Key Canonicalization (`flow_key.py`)
- Standardizes 5-tuple: `(src_ip, dst_ip, src_port, dst_port, protocol)`.
- Ensures bidirectional packet matching so forward traffic `A -> B` and reverse traffic `B -> A` update the same active flow record.

## 2. Active Flow Table (`flow_table.py`)
- In-memory hashmap with configurable capacity (`FLOW_TABLE_MAX_SIZE = 50000`).
- Provides $O(1)$ flow lookup and packet accumulator update.

## 3. Flow Expiration Daemon (`flow_expiration.py`)
- **Idle Timeout**: Purges flows inactive for $> 15$ seconds (`FLOW_IDLE_TIMEOUT`).
- **Active Timeout**: Purges flows exceeding maximum lifespan of $> 120$ seconds (`FLOW_ACTIVE_TIMEOUT`).
- **TCP Closed**: Evicts TCP flows upon observing TCP FIN/RST flags.

## 4. Output Flow Queue (`flow_queue.py`)
- Buffers completed flow records (`FlowQueue`) for downstream feature extraction.
