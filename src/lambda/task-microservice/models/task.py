from typing import Optional, Literal, Annotated, Union

from pydantic import BaseModel, Field, constr

from .base_task import BaseTask
from models.s3_object import InputS3ItemContent, InputS3ArrayContent, OutputS3ItemContent



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


class Task(BaseTask):
    AppServiceSlug: str = Field('pavimenta2#road_sections_inference', const=True)
    Inputs: PavimentadosTaskInput
    Outputs: Optional[PavimentadosTaskOutput]
