
from infra_commons.aws_resources import LambdaS3
from infra_commons.models.s3_object import InputS3Content, S3ObjectReference


class StorageService:
    def __init__(self, resource: LambdaS3):
        self.resource = resource

    def sign_upload_url(self, object_reference: S3ObjectReference):
        return self.resource.client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': object_reference.Bucket,
                'Key': object_reference.Key
            },
            ExpiresIn=3600
        )

    def generate_presign_upload_url(self, input_reference: InputS3Content):
        if input_reference.is_array:
            presigned_content = [
                self.sign_upload_url(item)
                for item in input_reference.Content
            ]

        else:
            presigned_content = self.sign_upload_url(input_reference.Content)

        return presigned_content

    def generate_signed_download_url(self, object_reference: S3ObjectReference):
        return self.resource.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': object_reference.Bucket,
                'Key': object_reference.Key
            },
            ExpiresIn=3600
        )

    def list_objects(self, object_reference: S3ObjectReference):
        return self.resource.client.list_objects_v2(
            Bucket=object_reference.Bucket,
            Prefix=object_reference.Key
        )
