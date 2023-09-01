
from infra_commons.aws_resources import LambdaS3
from infra_commons.models.s3_object import InputS3Content


class StorageService:
    def __init__(self, resource: LambdaS3):
        self.resource = resource

    def sign_upload_url(self, bucket, key):
        return self.resource.client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=3600
        )

    def generate_presign_upload_url(self, input_reference: InputS3Content):
        if input_reference.is_array:
            presigned_content = [
                self.sign_upload_url(item.Bucket, item.Key)
                for item in input_reference.Content
            ]

        else:
            presigned_content = self.sign_upload_url(input_reference.Content.Bucket, input_reference.Content.Key)

        return presigned_content
