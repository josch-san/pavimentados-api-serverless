import json
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from pydantic import BaseModel, Field, constr
from infra_commons.models.s3_object import S3ObjectReference

DATASET_SLUG_PATTERN = r'^[a-z]{2}[a-z0-9\_]*(?:#[a-z]{2}[a-z0-9\_]*)*$'


class DatasetAccessLevelEnum(str, Enum):
    PUBLIC = 'public'
    # PRIVATE_INFRA = 'private-infra'
    PRIVATE_APP = 'private-app'


class DatasetRepositoryTypeEnum(str, Enum):
    AMAZON_S3 = 'amazon-s3'
    AMAZON_ATHENA = 'amazon-athena'
    SQL = 'sql'


class Dataset(BaseModel):
    Id: UUID = Field(default_factory=uuid4)
    Slug: constr(regex=DATASET_SLUG_PATTERN)
    Name: str
    Description: Optional[str]
    UserSub: Optional[UUID]
    Owner: Optional[str]
    AccessLevel: DatasetAccessLevelEnum = DatasetAccessLevelEnum.PRIVATE_APP
    RepositoryType: DatasetRepositoryTypeEnum = DatasetRepositoryTypeEnum.AMAZON_S3
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    ModifiedAt: datetime = Field(default_factory=datetime.utcnow)
    DatasetConfig: S3ObjectReference = Field(alias='Config')
    Metadata: Optional[dict]
    IsDeleted: bool = False

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
    def build_dynamodb_key(dataset_id: str) -> dict:
        return {
            'Pk': 'DATASET#{}'.format(dataset_id),
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
            '__typename': 'Dataset'
            # 'Gsi1Pk': 'DATASET'
        }

    @property
    def slug_dynamodb_key(self) -> dict:
        return {
            'Pk': 'DATASET#{}'.format(self.Slug)
        }

    @property
    def slug_dynamodb_record(self) -> dict:
        return {
            **self.slug_dynamodb_key,
            'Id': str(self.Id)
        }

    def is_dir(self) -> bool:
        return self.DatasetConfig.Key.endswith('/')
