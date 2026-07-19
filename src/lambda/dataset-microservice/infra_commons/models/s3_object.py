"""S3 object reference model."""
from typing import Optional
from pydantic import BaseModel, Field


class S3ObjectReference(BaseModel):
    """Reference to an S3 object."""
    
    bucket: str = Field(alias='Bucket')
    key: str = Field(alias='Key')
    size: Optional[int] = Field(default=None, alias='Size')
    content_type: Optional[str] = Field(default=None, alias='ContentType')
    last_modified: Optional[str] = Field(default=None, alias='LastModified')
    
    class Config:
        """Pydantic config."""
        populate_by_name = True
        extra = 'ignore'
