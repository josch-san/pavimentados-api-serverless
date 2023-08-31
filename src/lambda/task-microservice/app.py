import os

import boto3
from botocore.config import Config
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

from infra_commons.aws_resources import LambdaDynamoDB, LambdaS3, LambdaSQS
from infra_commons.serializers import custom_serializer
from controllers import task_controller

tracer = Tracer()
logger = Logger()

STAGE_PREFIX = '/' + os.getenv('API_STAGE', 'dev')
_DYNAMODB_RESOURCE = {
    'resource' : boto3.resource('dynamodb'),
    'table_name' : os.getenv('TABLE_NAME')
}
_S3_RESOURCE = {
    'client' : boto3.client('s3', config=Config(signature_version='s3v4')),
    'bucket_name' : os.getenv('ATTACHMENTS_BUCKET_NAME')
}
_SQS_RESOURCE = {
    'resource' : boto3.resource('sqs'),
    'queue_url' : os.getenv('TASK_QUEUE_URL')
}

app = APIGatewayRestResolver(strip_prefixes=[STAGE_PREFIX], serializer=custom_serializer)
app.include_router(task_controller.router, prefix='/tasks')


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    global _DYNAMODB_RESOURCE
    global _S3_RESOURCE
    global _SQS_RESOURCE

    app.append_context(
        dynamodb_resource=LambdaDynamoDB(_DYNAMODB_RESOURCE),
        s3_resource=LambdaS3(_S3_RESOURCE),
        sqs_resource=LambdaSQS(_SQS_RESOURCE)
    )

    return app.resolve(event, context)
