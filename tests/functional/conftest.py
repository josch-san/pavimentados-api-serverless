import json

import boto3
import pytest
from moto import mock_dynamodb, mock_sqs, mock_s3

from tests.mocks import task_microservice as mocks


@pytest.fixture
def build_api_request():
    def _build_api_request(http_method, path, *, body=None):
        return {
            'httpMethod': http_method,
            'path': path,
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': mocks.USER_SUB,
                        'cognito:username': mocks.USER_SUB,
                        'given_name': 'Jose',
                        'family_name': 'Hernandez',
                        'email': 'jhernandez@sample.co'
                    }
                },
                'requestId': '227b78aa-779d-47d4-a48e-ce62120393b8'  # correlation ID
            },
            'body': None if body == None else json.dumps(body)
        }

    yield _build_api_request


@pytest.fixture(scope='session')
def dynamodb():
    with mock_dynamodb():
        dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb_resource.create_table(
            TableName=mocks.TABLE_NAME,
            KeySchema=[{'AttributeName': 'Pk', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'Pk', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        with table.batch_writer() as batch:
            for record in mocks.TASK_LIST:
                batch.put_item(Item=record)

        yield dynamodb_resource, dynamodb_client

@pytest.fixture(scope='session')
def sqs():
    with mock_sqs():
        sqs = boto3.resource('sqs', region_name='us-east-1')
        sqs.create_queue(
            QueueName=mocks.QUEUE_URL.split('/')[-1],
        )

    yield sqs

@pytest.fixture(scope='session')
def s3():
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(
            Bucket=mocks.BUCKET_NAME
        )

    yield s3
