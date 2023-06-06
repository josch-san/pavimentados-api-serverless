import os
import sys
import json
from http import HTTPStatus

import boto3
import pytest
from moto import mock_dynamodb

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
sys.path.append('./src/lambda/task-microservice')

from tests import mocks
import app


@ pytest.fixture
def api_client(lambda_context, build_api_request):
    def _resolve_request(*args, **kwargs):
        event = build_api_request(*args, **kwargs)
        return app.lambda_handler(event, lambda_context)

    return _resolve_request


@pytest.fixture(scope='class')
def dynamodb():
    print('Mocking dynamodb...')
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName = 'infra-mock',
            KeySchema=[{'AttributeName': 'Pk', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'Pk', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        print('Filling table with tasks...')
        with table.batch_writer() as batch:
            for record in mocks.TASK_LIST:
                batch.put_item(Item=record)

        yield dynamodb


@pytest.fixture(autouse=True)
def set_aws_resources(monkeypatch, dynamodb):
    monkeypatch.setitem(app._S3_RESOURCE, 'bucket_name', 'infra-attachments-mock')
    monkeypatch.setitem(app._SQS_RESOURCE, 'queue_url', 'pavimentados-queue-mock')

    monkeypatch.setattr(app, '_DYNAMODB_RESOURCE', {
        'resource': dynamodb,
        'table_name': 'infra-mock'
    })


class TestTaskEndpoints:
    def test_list_tasks(self, api_client):
        response = api_client('GET', '/dev/tasks')
        assert response['statusCode'] == HTTPStatus.OK

        parsed_body = json.loads(response['body'])
        assert len(parsed_body['items']) == len(mocks.TASK_LIST)

    def test_retrieve_task(self, api_client):
        task_id = mocks.NOT_OWNED_DRAFT_TASK['Id']

        response = api_client('GET', f'/dev/tasks/{task_id}')
        assert response['statusCode'] == HTTPStatus.OK

    def test_retrieve_not_found_task(self, api_client):
        # This task_id doesn't exists in db.
        task_id = 'a52bc1e1-9f2e-48ab-98f2-b5e4cc059154'

        response = api_client('GET', f'/dev/tasks/{task_id}')
        assert response['statusCode'] == HTTPStatus.NOT_FOUND

    def test_update_unauthorized_task(self, api_client):
        task_id = mocks.NOT_OWNED_DRAFT_TASK['Id']

        response = api_client(
            'PUT',
            f'/dev/tasks/{task_id}',
            body={
                'Name': 'Cambio nombre',
                'Description': 'Larga descripcion'
            }
        )
        assert response['statusCode'] == HTTPStatus.UNAUTHORIZED
