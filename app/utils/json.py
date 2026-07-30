"""JSON Encoding Helpers."""

import json
from datetime import datetime
import uuid
from typing import Any


class PRISMJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder handling UUID and datetime instances."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def dumps(obj: Any) -> str:
    """Serialize object to JSON string using PRISM encoder."""
    return json.dumps(obj, cls=PRISMJSONEncoder)
