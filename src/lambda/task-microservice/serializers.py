import json
from json import JSONEncoder

from pydantic import BaseModel
from models.base_task import BaseTask


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseTask):
            return obj.raw_dict()
        if isinstance(obj, BaseModel):
            return obj.dict(by_alias=True)
        return super().default(obj)


def custom_serializer(obj) -> str:
    return json.dumps(obj, separators=(',', ':'), cls=CustomEncoder)
