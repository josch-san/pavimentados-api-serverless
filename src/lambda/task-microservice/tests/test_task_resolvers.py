import os
from dataclasses import dataclass
import pytest

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['TABLE_NAME'] = 'infra-dev'
os.environ['ATTACHMENTS_BUCKET_NAME'] = 'bucket-dev'
os.environ['TASK_QUEUE_URL'] = 'pavimentados-queue-dev'
os.environ['API_STAGE'] = 'dev'

import sys
sys.path.append('..')
import app

# Example of API Gateway REST API request event:
# https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html#apigateway-example-event
EVENT_TEMPLATE = {
        # 'path': '/dev/tasks',
        # 'httpMethod': 'GET',
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': '6b456b08-fa1d-4e24-9fbd-be990e023299',
                    'cognito:username': '6b456b08-fa1d-4e24-9fbd-be990e023299',
                    'given_name': 'Jose',
                    'family_name': 'Hernandez',
                    'email': 'jhernandez@sample.co'
                }
            },
            'requestId': '227b78aa-779d-47d4-a48e-ce62120393b8'  # correlation ID
        }
    }


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
    minimal_rest_event = {
        **EVENT_TEMPLATE,
        'path': '/dev/tasks',
        'httpMethod': 'GET'
    }

    response = app.lambda_handler(minimal_rest_event, lambda_context)

    assert response['statusCode'] == 200


def test_retrieve_task(lambda_context):
    minimal_rest_event = {
        **EVENT_TEMPLATE,
        'path': '/dev/tasks/db4e6a6c-d768-4b43-ad8c-99b579c8c23b',
        'httpMethod': 'GET'
    }

    response = app.lambda_handler(minimal_rest_event, lambda_context)
    assert response['statusCode'] == 200


def test_retrieve_task_404(lambda_context):
    # This task_id doesn't exists in db.
    minimal_rest_event = {
        **EVENT_TEMPLATE,
        'path': '/dev/tasks/a52bc1e1-9f2e-48ab-98f2-b5e4cc059154',
        'httpMethod': 'GET'
    }

    response = app.lambda_handler(minimal_rest_event, lambda_context)
    assert response['statusCode'] == 404


def test_generate_attachment_upload_url_unauthorized(lambda_context):
    payload = {
        'FieldName': 'VideoFile',
        'ArrayLength': 1,
        'Extension': 'mp4'
    }

    minimal_rest_event = {
        **EVENT_TEMPLATE,
        'path': '/dev/tasks/69688b53-960b-45f8-9b03-476e73148b06/generateAttachmentUploadUrl',
        'httpMethod': 'POST',
        'body': json.dumps(payload)
    }

    response = app.lambda_handler(minimal_rest_event, lambda_context)
    assert response['statusCode'] == 401
