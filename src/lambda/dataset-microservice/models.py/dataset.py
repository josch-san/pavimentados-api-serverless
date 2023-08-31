import json
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from pydantic import BaseModel, Field, constr

DATASET_SLUG_PATTERN = r'^[a-z]{2}[a-z0-9\_]*(?:#[a-z]{2}[a-z0-9\_]*)*$'


class AccessLevelEnum(str, Enum):
    PUBLIC = 'public'
    PRIVATE_INFRA = 'private-infra'
    PRIVATE_APP = 'private-app'


class RepositoryTypeEnum(str, Enum):
    AMAZON_S3 = 'amazon-s3'
    AMAZON_ATHENA = 'amazon-athena'
    SQL = 'sql'


class Dataset(BaseModel):
    Id: UUID = Field(default=uuid4)
    Name: str
    Slug: constr(regex=DATASET_SLUG_PATTERN)
    Config: Optional[dict]
    AccessLevel: AccessLevelEnum = AccessLevelEnum.PUBLIC
    RepositoryType: RepositoryTypeEnum
    IsDeleted: bool = False
    UserSub: Optional[UUID]
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    ModifiedAt: datetime = Field(default_factory=datetime.utcnow)
    Description: Optional[str]
    Owner: Optional[str]

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
            'Pk': 'DATASET#{}'.format(task_id),
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
            '__typename': 'DATASET'
            # 'Gsi1Pk': 'TASK'
        }
