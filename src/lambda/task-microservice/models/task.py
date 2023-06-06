from typing import Optional, Literal, Annotated, Union
from copy import deepcopy

from pydantic import BaseModel, Field


from .base_task import BaseTask
from .s3_object import InputS3Content, InputS3ItemContent, InputS3ArrayContent, OutputS3ItemContent


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
        kwargs.setdefault('ImageBundle', {
            'Content': [deepcopy(kwargs.get('_S3BaseContent'))]
        })

        super().__init__(**kwargs)


class ImageBundleGpsInput(BaseModel):
    Geography: str
    ImageBundle: ImageBundle
    GpsFile: GpsFile
    Type: Literal['image_bundle_gps']

    def __init__(self, **kwargs):
        kwargs.setdefault('ImageBundle', {
            'Content': [deepcopy(kwargs.get('_S3BaseContent'))]
        })
        kwargs.setdefault('GpsFile', {
            'Content': deepcopy(kwargs.get('_S3BaseContent'))
        })

        super().__init__(**kwargs)


class VideoGpsInput(BaseModel):
    Geography: str
    VideoFile: VideoFile
    GpsFile: GpsFile
    Type: Literal['video_gps']

    def __init__(self, **kwargs):
        kwargs.setdefault('VideoFile', {
            'Content': deepcopy(kwargs.get('_S3BaseContent'))
        })
        kwargs.setdefault('GpsFile', {
            'Content': deepcopy(kwargs.get('_S3BaseContent'))
        })

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

    @property
    def s3_key_path(self):
        application, service = self.AppServiceSlug.split('#')
        return f'{application}/user:{self.UserId}/{service}/{self.Id}/inputs'

    def initialize_inputs(self, inputs: dict, bucket_name: str) -> None:
        s3_base_path = {
            'Bucket': bucket_name,
            'Key': self.s3_key_path
        }

        self.Inputs = {**inputs, '_S3BaseContent': s3_base_path}

    def update_attachment_input(self, payload: dict, bucket_name: str) -> None:
        attachment_field = getattr(self.Inputs, payload['FieldName'])
        attachment_field.Extension = payload['Extension']

        if not isinstance(attachment_field, InputS3Content):
            raise Exception(f"Field '{payload['FieldName']}' is not available to upload attachments.")

        if not attachment_field.is_array:
            if payload.get('ArrayLength', 1) != 1:
                raise Exception(f"Field '{payload['FieldName']}' can only handle one attachment.")

            attachment_field.Content = {
                'Bucket': bucket_name,
                'Key': '/'.join([
                    self.s3_key_path,
                    attachment_field.build_file_name(payload['Extension'])
                ]),
                'Uploaded': False
            }

        else:
            attachment_field.Content = [
                {
                    'Bucket': bucket_name,
                    'Key': '/'.join([
                        self.s3_key_path,
                        attachment_field.build_indexed_file_name(payload['Extension'], index)
                    ]),
                    'Uploaded': False
                }
                for index in range(payload.get('ArrayLength', 1))
            ]

        setattr(self.Inputs, payload['FieldName'], attachment_field)

    def update(self, payload: dict) -> None:
        updateable_fields = []
