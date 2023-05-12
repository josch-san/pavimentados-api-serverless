from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Literal, Annotated, Union

from pydantic import BaseModel, Field, constr

from models.s3_object import InputS3ItemContent, InputS3ArrayContent, OutputS3ItemContent


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


class ImageBundleInput(BaseModel):
    Geography: str
    ImageBundle: InputS3ArrayContent[
        constr(regex=r'^zip$')
    ]
    Type: Literal['image_bundle']


class ImageBundleGpsInput(BaseModel):
    Geography: str
    ImageBundle: InputS3ArrayContent[
        constr(regex=r'^zip$')
    ]
    GpsFile: InputS3ItemContent[
        constr(regex=r'^log|txt$')
    ]
    Type: Literal['image_bundle_gps']


class VideoGpsInput(BaseModel):
    Geography: str
    VideoFile: InputS3ItemContent[
        constr(regex=r'^mp4$')
    ]
    GpsFile: InputS3ItemContent[
        constr(regex=r'^log|txt$')
    ]
    Type: Literal['video_gps']


PavimentadosTaskInput = Annotated[
    Union[
        ImageBundleInput,
        ImageBundleGpsInput,
        VideoGpsInput
    ],
    Field(discriminator='Type')
]


class PavimentadosTaskOutput(BaseModel):
    DetectionsOverPhotogram: OutputS3ItemContent
    FailuresDetected: OutputS3ItemContent
    SignalsDetected: OutputS3ItemContent
    Sections: OutputS3ItemContent


class Task(BaseModel):
    Id: UUID = Field(default_factory=uuid4)
    Name: str
    Description: Optional[str]
    UserId: UUID
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    ModifiedAt: datetime = Field(default_factory=datetime.utcnow)
    AppServiceSlug: Literal['pavimenta2#road_sections_inference']
    TaskStatus: TaskStatusEnum = TaskStatusEnum.DRAFT
    AccessLevel: AccessLevelEnum = AccessLevelEnum.APP
    Inputs: PavimentadosTaskInput
    Outputs: Optional[PavimentadosTaskOutput]
    OutputMessage: Optional[str]
