import json
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from pydantic import BaseModel, Field

# from .format_functions import to_camel


class TaskStatusEnum(str, Enum):
    DRAFT = 'draft'
    QUEUED = 'queued'
    REQUESTING = 'requesting'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELED = 'canceled'


class TaskAccessLevelEnum(str, Enum):
    USER = 'user'
    APP = 'app'


class BaseTask(BaseModel):
    Id: UUID = Field(default_factory=uuid4)
    Name: str
    Description: Optional[str]
    UserSub: UUID
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    ModifiedAt: datetime = Field(default_factory=datetime.utcnow)
    TaskStatus: TaskStatusEnum = TaskStatusEnum.DRAFT
    AccessLevel: TaskAccessLevelEnum = TaskAccessLevelEnum.APP
    AppServiceSlug: str
    Inputs: Optional[dict]
    Outputs: Optional[dict]
    OutputMessage: Optional[str]

    class Config:
        extra = 'ignore'
        validate_assignment = True
        # alias_generator = to_camel
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.replace(tzinfo=None).isoformat(timespec='milliseconds') + 'Z'
        }

    def raw_dict(self) -> dict:
        # It's messy I know but it's the best I can do right now.
        return json.loads(self.json(by_alias=True))

    @staticmethod
    def build_dynamodb_key(task_id: str) -> dict:
        return {
            'Pk': 'TASK#{}'.format(task_id),
            # 'Sk': 'metadata'
        }

    @property
    def dynamodb_key(self) -> dict:
        return self.build_dynamodb_key(self.Id)

    @property
    def dynamodb_record(self) -> dict:
        return {
            **self.dynamodb_key,
            **self.raw_dict(),
            '__typename': 'Task'
            # 'Gsi1Pk': 'TASK'
        }

    def build_event_payload(self) -> dict:
        inputs = {
            key: getattr(value, 'payload_content', value)
            for key, value in self.Inputs
        }

        payload = {
            key: value
            for key, value in self.raw_dict().items()
            if key in ['Id', 'Name', 'AccessLevel', 'AppServiceSlug', 'UserSub']
        }

        payload['Inputs'] = inputs
        return payload
