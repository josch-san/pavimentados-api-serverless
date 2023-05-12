from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

ExtensionT = TypeVar('ExtensionT')


class S3ObjectReference(BaseModel):
    Key: str
    Bucket: str


class FlaggedS3ObjectReference(S3ObjectReference):
    Uploaded: bool = False


class OutputS3ItemContent(BaseModel):
    Content: S3ObjectReference


class InputS3ItemContent(GenericModel, Generic[ExtensionT]):
# class InputS3ItemContent(BaseModel):
    Extension: ExtensionT
    # Extension: str
    Content: FlaggedS3ObjectReference


class InputS3ArrayContent(GenericModel, Generic[ExtensionT]):
# class InputS3ArrayContent(BaseModel):
    Extension: ExtensionT
    # Extension: str
    Content: list[FlaggedS3ObjectReference]
