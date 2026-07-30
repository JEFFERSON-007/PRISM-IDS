"""Granular System Permissions and Role Mapping Matrix."""

from enum import Enum
from typing import Dict, Set
from app.authentication.roles import Role


class Permission(str, Enum):
    """System Fine-Grained Permissions."""

    # System & Server Management
    READ_HEALTH = "system:health:read"
    READ_METRICS = "system:metrics:read"
    MANAGE_SYSTEM = "system:admin:manage"

    # User & Auth Management
    READ_USERS = "users:read"
    WRITE_USERS = "users:write"
    DELETE_USERS = "users:delete"

    # IDS Future Module Readiness Permissions
    READ_ALERTS = "alerts:read"
    WRITE_ALERTS = "alerts:write"
    MANAGE_RULES = "rules:manage"
    VIEW_REPORTS = "reports:view"


# Role to Permission Matrix
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.READ_HEALTH,
        Permission.READ_METRICS,
        Permission.MANAGE_SYSTEM,
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_ALERTS,
        Permission.WRITE_ALERTS,
        Permission.MANAGE_RULES,
        Permission.VIEW_REPORTS,
    },
    Role.ANALYST: {
        Permission.READ_HEALTH,
        Permission.READ_METRICS,
        Permission.READ_ALERTS,
        Permission.WRITE_ALERTS,
        Permission.VIEW_REPORTS,
    },
    Role.OPERATOR: {
        Permission.READ_HEALTH,
        Permission.READ_ALERTS,
    },
    Role.AUDITOR: {
        Permission.READ_HEALTH,
        Permission.READ_METRICS,
        Permission.READ_ALERTS,
        Permission.VIEW_REPORTS,
    },
    Role.SYSTEM: {
        Permission.READ_HEALTH,
        Permission.READ_METRICS,
        Permission.MANAGE_SYSTEM,
        Permission.WRITE_ALERTS,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    """Check whether a given role holds a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())
