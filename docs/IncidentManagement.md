# Incident Management Workflow Specification

## Incident Lifecycle States

```
┌──────────────┐     Analyst Acknowledges     ┌──────────────────┐
│     OPEN     │ ───────────────────────────> │   ACKNOWLEDGED   │
└──────┬───────┘                              └────────┬─────────┘
       │                                               │ Analyst Resolves
       │ Analyst Resolves Directly                     ▼
       └───────────────────────────────────> ┌──────────────────┐
                                             │     RESOLVED     │
                                             └────────┬─────────┘
                                                      │
                                                      │ Analyst Reopens
                                                      ▼
                                             ┌──────────────────┐
                                             │     REOPENED     │
                                             └──────────────────┘
```

---

## State Transition Rules

1. **OPEN**: Initial state upon incident creation.
2. **ACKNOWLEDGED**: Analyst has taken ownership and initiated investigation.
3. **RESOLVED**: Containment/remediation completed.
4. **REOPENED**: Post-investigation revealed recurring threat or false resolution.
