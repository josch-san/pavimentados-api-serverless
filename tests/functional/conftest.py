import json
from dataclasses import dataclass
import pytest

from tests import mocks


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = 'task-microservice-mock'
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = 'arn:aws:lambda:us-east-1:123456789012:function:task-microservice-mock'
        aws_request_id: str = 'da658bd3-2d6f-4e7b-8ec2-937234644fdc'

    return LambdaContext()


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
