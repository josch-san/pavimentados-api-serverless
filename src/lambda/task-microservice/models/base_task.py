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


class AccessLevelEnum(str, Enum):
    USER = 'user'
    APP = 'app'


class BaseTask(BaseModel):
    Id: UUID = Field(default_factory=uuid4)
    Name: str
    Description: Optional[str]
    UserId: UUID
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    ModifiedAt: datetime = Field(default_factory=datetime.utcnow)
    TaskStatus: TaskStatusEnum = TaskStatusEnum.DRAFT
    AccessLevel: AccessLevelEnum = AccessLevelEnum.APP
    AppServiceSlug: str
    Inputs: dict
    Outputs: Optional[dict]
    OutputMessage: Optional[str]

    class Config:
        extra = 'ignore'
        # alias_generator = to_camel

    @staticmethod
    def build_dynamodb_key(task_id):
        return {
            'Pk': 'TASK#{}'.format(task_id),
            # 'Sk': 'metadata'
        }

    @property
    def dynamodb_key(self):
        return self.build_dynamodb_key(self.Id)

    @property
    def dynamodb_record(self) -> dict:
        return {
            **self.dynamodb_key,
            **self.dict(by_alias=True),
            # 'Gsi1Pk': 'TASK'
        }

    def build_sqs_message(self) -> dict:
        return {
            **self.dynamodb_key,
            **self.dict(by_alias=True),
            # 'Gsi1Pk': 'TASK'
        }
