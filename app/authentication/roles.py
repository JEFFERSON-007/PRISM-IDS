"""Role-Based Access Control (RBAC) Enums and Helpers."""

from enum import Enum


class Role(str, Enum):
    """System User Roles."""

    ADMIN = "admin"
    ANALYST = "analyst"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    SYSTEM = "system"

    def __str__(self) -> str:
        return self.value
