# Database Schema & Entity Relationship Model

PRISM IDS Phase 2 implements a normalized PostgreSQL relational database schema.

```
  ┌────────────────┐           ┌────────────────┐           ┌──────────────────┐
  │     Roles      │1        * │     Users      │1         *│    Audit Logs    │
  │────────────────│───────────│────────────────│───────────│──────────────────│
  │ id (PK)        │           │ id (PK)        │           │ id (PK)          │
  │ name           │           │ username       │           │ user_id (FK)     │
  │ description    │           │ email          │           │ agent_id (FK)    │
  └───────┬────────┘           │ password_hash  │           │ action           │
          │1                   │ role_id (FK)   │           │ resource         │
          │                    │ is_active      │           │ timestamp        │
          │*                   │ locked_until   │           └──────────────────┘
  ┌───────┴────────┐           └────────────────┘
  │Role_Permissions│
  │────────────────│
  │ role_id (FK)   │
  │ permission_id  │
  └───────┬────────┘
          │*
          │1                   ┌────────────────┐           ┌──────────────────┐
  ┌───────┴────────┐           │     Agents     │1         *│    Heartbeats    │
  │  Permissions   │           │────────────────│───────────│──────────────────│
  │────────────────│           │ id (PK)        │           │ id (PK)          │
  │ id (PK)        │           │ agent_name     │           │ agent_id (FK)    │
  │ name           │           │ hostname       │           │ timestamp        │
  │ category       │           │ ip_address     │           │ cpu_usage        │
  └────────────────┘           │ secret_hash    │           │ ram_usage        │
                               │ is_online      │           │ disk_usage       │
                               │ health_status  │           └──────────────────┘
                               └───────┬────────┘
                                       │1
                                       │1
                               ┌───────┴────────┐
                               │ Agent_Configs  │
                               │────────────────│
                               │ id (PK)        │
                               │ agent_id (FK)  │
                               │ version        │
                               │ packet_filters │
                               │ log_level      │
                               └────────────────┘
```

---

## Tables Overview

### 1. `users`
- Primary Key: `id` (UUID)
- Attributes: `username`, `email`, `password_hash`, `full_name`, `role_id` (FK), `is_active`, `failed_login_attempts`, `locked_until`, `last_login`, `deleted_at`, `created_at`, `updated_at`.

### 2. `roles` & `permissions`
- `roles`: `id` (UUID), `name`, `description`.
- `permissions`: `id` (UUID), `name`, `description`, `category`.
- `role_permissions`: Join table (`role_id`, `permission_id`).

### 3. `agents`
- Primary Key: `id` (UUID)
- Attributes: `agent_name`, `hostname`, `ip_address`, `operating_system`, `version`, `secret_key_hash`, `registration_time`, `last_heartbeat`, `is_online`, `health_status`.

### 4. `heartbeats`
- Primary Key: `id` (UUID)
- Attributes: `agent_id` (FK), `timestamp`, `cpu_usage`, `ram_usage`, `disk_usage`, `network_status`, `agent_version`.

### 5. `agent_configurations`
- Primary Key: `id` (UUID)
- Attributes: `agent_id` (FK, Unique), `version`, `capture_interface`, `packet_filters`, `log_level`, `sampling_rate`, `custom_config` (JSONB).

### 6. `audit_logs`
- Primary Key: `id` (UUID)
- Attributes: `user_id` (FK), `agent_id` (FK), `action`, `resource`, `ip_address`, `user_agent`, `details` (JSONB), `status`, `timestamp`.
