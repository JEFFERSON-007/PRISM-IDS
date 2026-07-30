# Alert Management & Deduplication Specification

## Deduplication Strategy

To prevent alert fatigue, repeat security events matching `(src_ip, dst_ip, dst_port, protocol, rule_id)` within `ALERT_DEDUP_WINDOW` ($60\text{s}$) update the cached alert in-place:
1. Increments `occurrence_count`.
2. Updates `last_seen` timestamp to current UTC time.
3. Recalculates `risk_score` using frequency multiplier.
4. Suppresses creation of redundant duplicate alert objects.
