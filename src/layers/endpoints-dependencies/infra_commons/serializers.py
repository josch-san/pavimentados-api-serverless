import json
from datetime import datetime
from json import JSONEncoder
from pydantic import BaseModel


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'raw_dict'):
            return obj.raw_dict()
        if isinstance(obj, BaseModel):
            return obj.dict(by_alias=True)
        if isinstance(obj, datetime):
            return obj.replace(tzinfo=None).isoformat(timespec='milliseconds') + 'Z'
        return super().default(obj)


def custom_serializer(obj) -> str:
    return json.dumps(obj, separators=(',', ':'), cls=CustomEncoder)
