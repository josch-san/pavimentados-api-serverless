class LambdaDynamoDB:
    def __init__(self, lambda_dynamodb_resource):
        self.resource = lambda_dynamodb_resource['resource']
        self.table_name = lambda_dynamodb_resource['table_name']
        self.table = self.resource.Table(self.table_name)


class LambdaS3:
    def __init__(self, lambda_s3_resource):  
        self.resource = lambda_s3_resource['resource']
        self.bucket_name = lambda_s3_resource['bucket_name']
        self.bucket = self.resource.Bucket(self.bucket_name)


class LambdaSQS:
    def __init__(self, lambda_s3_resource):  
        self.resource = lambda_s3_resource['resource']
        self.queue_url = lambda_s3_resource['queue_url']
        self.bucket = self.resource.Queue(self.queue_url)
