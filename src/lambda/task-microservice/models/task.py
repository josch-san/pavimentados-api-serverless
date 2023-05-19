from typing import Optional, Literal, Annotated, Union
from copy import deepcopy

from pydantic import BaseModel, Field


from .base_task import BaseTask
from .s3_object import InputS3ItemContent, InputS3ArrayContent, OutputS3ItemContent


class GpsFile(InputS3ItemContent):
    Extension: Literal['log', 'txt'] = 'log'


class ImageBundle(InputS3ArrayContent):
    Extension: str = Field('zip', const=True)


class VideoFile(InputS3ItemContent):
    Extension: str = Field('mp4', const=True)


class ImageBundleInput(BaseModel):
    Geography: str
    ImageBundle: ImageBundle
    Type: Literal['image_bundle']

    def __init__(self, **kwargs):
        kwargs.setdefault('ImageBundle', kwargs.get('_S3BaseContent'))
        super().__init__(**kwargs)


class ImageBundleGpsInput(BaseModel):
    Geography: str
    ImageBundle: ImageBundle
    GpsFile: GpsFile
    Type: Literal['image_bundle_gps']

    def __init__(self, **kwargs):
        kwargs.setdefault('ImageBundle', kwargs.get('_S3BaseContent'))
        kwargs.setdefault('GpsFile', deepcopy(kwargs.get('_S3BaseContent')))
        super().__init__(**kwargs)


class VideoGpsInput(BaseModel):
    Geography: str
    VideoFile: VideoFile
    GpsFile: GpsFile
    Type: Literal['video_gps']

    def __init__(self, **kwargs):
        kwargs.setdefault('VideoFile', kwargs.get('_S3BaseContent'))
        kwargs.setdefault('GpsFile', deepcopy(kwargs.get('_S3BaseContent')))
        super().__init__(**kwargs)


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
    Inputs: Optional[PavimentadosTaskInput]
    Outputs: Optional[PavimentadosTaskOutput]

    def initialize_inputs(self, inputs: dict, bucket_name: str) -> None:
        application, service = self.AppServiceSlug.split('#')
        s3_base_path = {
            'Bucket': bucket_name,
            'Key': '/'.join([
                application,
                'user:{}'.format(self.UserId),
                service,
                str(self.Id),
                'inputs'
            ])
        }

        self.Inputs = {**inputs, '_S3BaseContent': {'Content': s3_base_path}}
