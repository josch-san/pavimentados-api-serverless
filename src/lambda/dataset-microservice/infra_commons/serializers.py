"""Custom serializers for API responses."""
import json
from datetime import datetime, date
from decimal import Decimal


def custom_serializer(obj):
    """Custom JSON serializer for objects not serializable by default json code.
    
    This is used by Powertools to serialize the response body.
    """
    # Handle None
    if obj is None:
        return None
    # Handle primitives
    if isinstance(obj, (str, int, float, bool)):
        return obj
    # Handle datetime/date
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    # Handle Decimal
    if isinstance(obj, Decimal):
        return float(obj)
    # Handle dict
    if isinstance(obj, dict):
        return {k: custom_serializer(v) for k, v in obj.items()}
    # Handle list
    if isinstance(obj, (list, tuple)):
        return [custom_serializer(item) for item in obj]
    # Handle Pydantic models
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    if hasattr(obj, 'dict'):
        return obj.dict()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def to_json(obj):
    """Convert object to JSON string."""
    return json.dumps(obj, default=custom_serializer)
