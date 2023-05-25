from datetime import datetime
from pydantic import BaseModel, validator


class S3ObjectReference(BaseModel):
    Key: str
    Bucket: str


class FlaggedS3ObjectReference(S3ObjectReference):
    Uploaded: bool = False


class OutputS3ItemContent(BaseModel):
    Content: S3ObjectReference


class InputS3ItemContent(BaseModel):
    Extension: str
    Content: FlaggedS3ObjectReference

    class Config:
        extra = 'ignore'
        validate_assignment = True

    @classmethod
    def build_file_name(cls, extension):
        return f'{cls.__name__}_{datetime.utcnow():%Y%m%d%H%M%S}.{extension}'

    @validator('Content', pre=True, always=True)
    def set_content(cls, content, values):
        if not content['Key'].endswith(values['Extension']):
            file_name = cls.build_file_name(values['Extension'])
            content['Key'] = '/'.join([content['Key'], file_name])

        return content


class InputS3ArrayContent(BaseModel):
    Extension: str
    Content: list[FlaggedS3ObjectReference]

    class Config:
        extra = 'ignore'
        validate_assignment = True

    @classmethod
    def build_indexed_file_name(cls, extension, index):
        return f'{cls.__name__}_{datetime.utcnow():%Y%m%d%H%M%S}_{index:02}.{extension}'

    @validator('Content', pre=True, always=True)
    def set_content(cls, content, values):
        if not content[0]['Key'].endswith(values['Extension']):
            file_name = cls.build_indexed_file_name(values['Extension'], 0)
            content[0]['Key'] = '/'.join([content[0]['Key'], file_name])

        return content
