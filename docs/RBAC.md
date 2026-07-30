# Role-Based Access Control (RBAC) Specification

PRISM IDS enforces strict Role-Based Access Control on every API endpoint.

---

## Pre-Defined Roles

1. **Administrator (`admin`)**: Full operational and administrative access over users, configuration, rules, and system probes.
2. **Security Analyst (`analyst`)**: Access to view alerts, system metrics, reports, and trigger rule updates.
3. **Operator (`operator`)**: Read-only access to alerts and system health status.
4. **Read Only (`auditor`)**: Compliance access to inspect audit logs, system metrics, and reports.

---

## Fine-Grained Permission Matrix

| Permission Name | Category | Admin | Analyst | Operator | Auditor |
|---|---|:---:|:---:|:---:|:---:|
| `system:health:read` | System | Yes | Yes | Yes | Yes |
| `system:metrics:read` | System | Yes | Yes | No | Yes |
| `system:admin:manage` | System | Yes | No | No | No |
| `users:read` | User | Yes | No | No | No |
| `users:write` | User | Yes | No | No | No |
| `users:delete` | User | Yes | No | No | No |
| `alerts:read` | Alert | Yes | Yes | Yes | Yes |
| `alerts:write` | Alert | Yes | Yes | No | No |
| `rules:manage` | Rules | Yes | Yes | No | No |
| `reports:view` | Reports | Yes | Yes | No | Yes |
