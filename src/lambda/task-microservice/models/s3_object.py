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

    @validator('Content', pre=True, always=True)
    def set_content(cls, content, values):
        if not content['Key'].endswith(values['Extension']):
            file_name = f'{cls.__name__}_{datetime.utcnow():%Y%m%d%H%M%S}.{values["Extension"]}'
            content['Key'] = '/'.join([content['Key'], file_name])
        return content


class InputS3ArrayContent(BaseModel):
    Extension: str
    Content: list[FlaggedS3ObjectReference]
