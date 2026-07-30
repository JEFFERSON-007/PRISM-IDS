"""UUID Utilities."""

import uuid


def generate_uuid() -> uuid.UUID:
    """Generate a v4 UUID instance."""
    return uuid.uuid4()


def is_valid_uuid(val: str) -> bool:
    """Check if string is valid UUID representation."""
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError, TypeError):
        return False
