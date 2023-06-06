import os
import sys
import json
from http import HTTPStatus

import boto3
import pytest
from moto import mock_dynamodb

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
sys.path.append('./src/lambda/task-microservice')

from models.task import TaskStatusEnum, Task
import app

from tests import mocks

TABLE_NAME = 'infra-mock'
BUCKET_NAME = 'infra-attachments-mock'
OUTPUT_PATH_TEMPLATE = 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/{}/outputs'


def parse_body(response):
    return json.loads(response['body'])


@pytest.fixture
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
            TableName = TABLE_NAME,
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

        response_body = parse_body(response)
        assert len(response_body['items']) == len(mocks.TASK_LIST)

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


class TestTaskWorkflow:
    def test_request_task_and_submit(self, api_client, dynamodb):
        # Step 1: Create task
        base_task_url = '/dev/tasks'
        create_form = {
            'Name': 'Analizando imagenes',
            'Description': 'larga descripcion...',
            'Inputs': {
                'Geography': 'Pichincha',
                'Type': 'image_bundle'
            }
        }

        response = api_client('POST', base_task_url, body=create_form)
        assert response['statusCode'] == HTTPStatus.CREATED

        created_task = parse_body(response)
        task_id = created_task['Id']


        # Step 2: Update task content (optional)
        detail_task_url = '/'.join([base_task_url, task_id])
        update_form = {
            'Name': 'Autopista Nacional TC-153',
            'Description': 'Un analisis muy importante'
        }

        response = api_client('PUT', detail_task_url, body=update_form)
        assert response['statusCode'] == HTTPStatus.OK

        updated_task = parse_body(response)
        # TODO: Assert changed updated data.


        # Step 3: Request S3 signed urls to upload input files.
        generate_attachment_upload_url = '/'.join([detail_task_url, 'generateAttachmentUploadUrl'])
        request_upload_urls_form = {
            'FieldName': 'ImageBundle',
            'ArrayLength': 3,
            'Extension': 'zip'
        }

        response = api_client('POST', generate_attachment_upload_url, body=request_upload_urls_form)
        assert response['statusCode'] == HTTPStatus.OK

        # TODO: Check upload urls.


        # Step 4: Submit task.
        submit_task_url = '/'.join([detail_task_url, 'submit'])

        response = api_client('POST', submit_task_url)
        assert response['statusCode'] == HTTPStatus.ACCEPTED


        # Step 5: Wait until task execution is completed.
        response = api_client('GET', detail_task_url)
        assert parse_body(response)['TaskStatus'] == TaskStatusEnum.QUEUED

        self.update_task_to_completed(task_id, dynamodb)
        response = api_client('GET', detail_task_url)
        assert parse_body(response)['TaskStatus'] == TaskStatusEnum.COMPLETED


        # Step 6: Request S3 signed urls to download outputs files.
        generate_output_download_urls = '/'.join([detail_task_url, 'generateOutputDownloadUrl'])

        response = api_client('POST', generate_output_download_urls)
        assert response['statusCode'] == HTTPStatus.OK

        # TODO: Check download urls.


    def update_task_to_completed(self, task_id, dynamodb):
        table = dynamodb.Table(TABLE_NAME)

        mock_output = {
            'DetectionsOverPhotogram': {
                'Content': {
                    'Bucket': BUCKET_NAME,
                    'Key': OUTPUT_PATH_TEMPLATE.format(task_id) + '/detections_over_photogram.csv'
                }
            },
            'FailuresDetected': {
                'Content': {
                    'Bucket': BUCKET_NAME,
                    'Key': OUTPUT_PATH_TEMPLATE.format(task_id) + '/failures_detected.csv'
                }
            },
            'Sections': {
                'Content': {
                    'Bucket': BUCKET_NAME,
                    'Key': OUTPUT_PATH_TEMPLATE.format(task_id) + '/sections.csv'
                }
            },
            'SignalsDetected': {
                'Content': {
                    'Bucket': BUCKET_NAME,
                    'Key': OUTPUT_PATH_TEMPLATE.format(task_id) + '/signals_detected.csv'
                }
            }
        }

        table.update_item(
            Key=Task.build_dynamodb_key(task_id),
            UpdateExpression=f'SET TaskStatus = :status, OutputMessage = :message, Outputs = :outputs',
            ExpressionAttributeValues={
                ':status': TaskStatusEnum.COMPLETED,
                ':message': 'Task processed successfully',
                ':outputs': mock_output
            }
        )
