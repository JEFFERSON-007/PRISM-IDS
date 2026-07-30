# Statistics and Analytics Specification

The Statistics API aggregates data stored in PostgreSQL to serve real-time SOC metrics.

## Aggregation Metrics

1. **Severity Distribution**: Group by `severity` column on `alerts` table.
2. **Average Risk Score**: `AVG(risk_score)` on `alerts` table.
3. **Top Attacker IPs**: `GROUP BY src_ip ORDER BY COUNT(id) DESC LIMIT 5`.
4. **Top Target Hosts**: `GROUP BY dst_ip ORDER BY COUNT(id) DESC LIMIT 5`.
5. **Protocol Distribution**: `GROUP BY protocol COUNT(id) / Total * 100.0`.
