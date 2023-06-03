import boto3
from botocore.config import Config

from models.s3_object import InputS3Content

s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))


class StorageService:
    def sign_upload_url(self, bucket, key):
        return s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=3600
        )

    def generate_presign_upload_url(self, content: InputS3Content):
        pass
    #     if content.is_array:
    #         return [
    #             sign_upload_url()
    #             for item in content
    #         ]
