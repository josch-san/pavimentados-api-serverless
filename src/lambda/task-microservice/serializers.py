import json
from json import JSONEncoder
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, (datetime)):
            return obj.replace(tzinfo=None).isoformat(timespec='milliseconds')
        if isinstance(obj, BaseModel):
            return obj.dict()
        return super().default(obj)


def custom_serializer(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), cls=CustomEncoder)
