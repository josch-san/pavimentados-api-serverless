import os
from dataclasses import dataclass
import pytest

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['TABLE_NAME'] = 'infra-mock'
os.environ['API_STAGE'] = 'mock'

import sys
sys.path.append('..')
import app


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = 'task-microservice'
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = 'arn:aws:lambda:eu-east-1:123456789012:function:task-microservice-mock'
        aws_request_id: str = 'da658bd3-2d6f-4e7b-8ec2-937234644fdc'

    return LambdaContext()


def test_list_tasks(lambda_context):
    minimal_event = {
        'path': '/dev/tasks',
        'httpMethod': 'GET',
        'requestContext': {
            'requestId': '227b78aa-779d-47d4-a48e-ce62120393b8'  # correlation ID
        }
    }

    # Example of API Gateway REST API request event:
    # https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html#apigateway-example-event
    ret = app.lambda_handler(minimal_event, lambda_context)

    assert ret['statusCode'] == 200
    assert type(ret['body']) == str
