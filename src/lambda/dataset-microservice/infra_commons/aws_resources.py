"""AWS resources utilities for Lambda functions."""
from typing import Optional
import boto3
from botocore.config import Config
from boto3.dynamodb.types import TypeDeserializer


class LambdaDynamoDB:
    """DynamoDB resource wrapper for Lambda functions."""
    
    def __init__(self, config: dict):
        self.client = config.get('client')
        self.resource = config.get('resource')
        self.table_name = config.get('table_name')
    
    @property
    def table(self):
        """Get DynamoDB table resource for direct access."""
        if self.resource:
            return self.resource.Table(self.table_name)
        # Fallback: return a wrapper that uses client
        return DynamoDBTableWrapper(self.client, self.table_name)
    
    def get_item(self, key: dict) -> dict:
        """Get item from DynamoDB table."""
        if self.client:
            return self.client.get_item(
                TableName=self.table_name,
                Key=key
            )
        return {}
    
    def put_item(self, item: dict) -> dict:
        """Put item into DynamoDB table."""
        if self.client:
            return self.client.put_item(
                TableName=self.table_name,
                Item=item
            )
        return {}
    
    def update_item(self, key: dict, update_expression: str, expression_values: dict) -> dict:
        """Update item in DynamoDB table."""
        if self.client:
            return self.client.update_item(
                TableName=self.table_name,
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
        return {}
    
    def scan(self, filter_expression: Optional[str] = None) -> dict:
        """Scan DynamoDB table."""
        if self.client:
            kwargs = {'TableName': self.table_name}
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            return self.client.scan(**kwargs)
        return {}


class DynamoDBTableWrapper:
    """Wrapper for DynamoDB Table when resource is not available."""
    
    def __init__(self, client, table_name: str):
        self._client = client
        self._table_name = table_name
        self._deserializer = TypeDeserializer()
    
    def _deserialize_item(self, item: dict) -> dict:
        """Deserialize DynamoDB item to Python dict."""
        if item:
            return self._deserializer.deserialize(item)
        return {}
    
    def scan(self, **kwargs):
        """Scan table and return items with deserialized types."""
        kwargs['TableName'] = self._table_name
        response = self._client.scan(**kwargs)
        # Deserialize each item
        items = response.get('Items', [])
        return {
            'Items': [self._deserialize_item(item) for item in items],
            'Count': response.get('Count', 0),
            'ScannedCount': response.get('ScannedCount', 0)
        }
    
    def get_item(self, Key: dict):
        """Get item from table with deserialized types."""
        response = self._client.get_item(TableName=self._table_name, Key=Key)
        item = response.get('Item')
        return {'Item': self._deserialize_item(item) if item else {}}


class LambdaS3:
    """S3 resource wrapper for Lambda functions."""
    
    def __init__(self, config: dict):
        self.client = config.get('client')
        self.bucket_name = config.get('bucket_name')
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for S3 object using default bucket."""
        return self._generate_presigned_url_for_bucket(self.bucket_name, key, expiration)
    
    def generate_presigned_url_for_config(self, config: dict, expiration: int = 3600) -> str:
        """Generate presigned URL for S3 object using config bucket and key."""
        bucket = config.get('bucket')
        key = config.get('key')
        if bucket and key:
            return self._generate_presigned_url_for_bucket(bucket, key, expiration)
        return ""
    
    def _generate_presigned_url_for_bucket(self, bucket: str, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for a specific bucket and key."""
        if self.client:
            try:
                url = self.client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': bucket,
                        'Key': key
                    },
                    ExpiresIn=expiration
                )
                return url
            except Exception:
                return ""
        return ""
    
    def list_objects(self, prefix: Optional[str] = None) -> dict:
        """List objects in S3 bucket."""
        if self.client:
            kwargs = {'Bucket': self.bucket_name}
            if prefix:
                kwargs['Prefix'] = prefix
            return self.client.list_objects_v2(**kwargs)
        return {}
    
    def get_object(self, key: str) -> dict:
        """Get object from S3 bucket."""
        if self.client:
            return self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
        return {}
    
    def put_object(self, key: str, body: bytes, content_type: Optional[str] = None) -> dict:
        """Put object into S3 bucket."""
        if self.client:
            kwargs = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Body': body
            }
            if content_type:
                kwargs['ContentType'] = content_type
            return self.client.put_object(**kwargs)
        return {}
