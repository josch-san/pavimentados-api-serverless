class LambdaDynamoDB:
    def __init__(self, lambda_dynamodb_resource):
        self.resource = lambda_dynamodb_resource['resource']
        self.table_name = lambda_dynamodb_resource['table_name']
        self.table = self.resource.Table(self.table_name)


class LambdaS3:
    def __init__(self, lambda_s3_resource):
        self.client = lambda_s3_resource['client']
        self.bucket_name = lambda_s3_resource['bucket_name']
