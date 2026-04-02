"""Storage service for S3 operations."""
from typing import Optional, List, Dict, Any


class StorageService:
    """Service for S3 storage operations."""
    
    def __init__(self, s3_resource):
        """Initialize storage service with S3 resource."""
        self.s3_resource = s3_resource
    
    def generate_signed_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for downloading an object."""
        return self.s3_resource.generate_presigned_url(key, expiration)
    
    def generate_signed_download_url(self, s3_config: dict, expiration: int = 3600) -> str:
        """Generate presigned URL using S3 config (bucket and key)."""
        return self.s3_resource.generate_presigned_url_for_config(s3_config, expiration)
    
    def list_objects(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """List objects in the bucket."""
        result = self.s3_resource.list_objects(prefix)
        contents = result.get('Contents', [])
        return [
            {
                'Key': obj['Key'],
                'Size': obj['Size'],
                'LastModified': obj['LastModified'].isoformat() if hasattr(obj['LastModified'], 'isoformat') else str(obj['LastModified'])
            }
            for obj in contents
        ]
    
    def get_object_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for an object."""
        result = self.s3_resource.get_object(key)
        return {
            'ContentLength': result.get('ContentLength', 0),
            'ContentType': result.get('ContentType', 'application/octet-stream'),
            'LastModified': str(result.get('LastModified', ''))
        }
