import os
import sys
import json
from http import HTTPStatus
from unittest.mock import patch
from dataclasses import dataclass

import pytest

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
sys.path.append('src/layers/endpoints-dependencies')
sys.path.append('src/lambda/task-microservice')

from models.task import TaskStatusEnum, Task
from services.queue_service import QueueService
import app

from tests.mocks import task_microservice as mocks

OUTPUT_PATH_TEMPLATE = 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/{}/outputs'
def parse_body(response):
    return json.loads(response['body'])


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
def api_client(lambda_context, build_api_request):
    def _resolve_request(*args, **kwargs):
        event = build_api_request(*args, **kwargs)
        return app.lambda_handler(event, lambda_context)

    return _resolve_request


@pytest.fixture(autouse=True)
def set_aws_resources(monkeypatch, dynamodb, sqs, s3):
    dynamodb_resource, dynamodb_client = dynamodb

    monkeypatch.setattr(app, '_DYNAMODB_RESOURCE', {
        'client': dynamodb_client,
        'resource': dynamodb_resource,
        'table_name': mocks.TABLE_NAME
    })
    monkeypatch.setattr(app, '_SQS_RESOURCE', {
        'resource': sqs,
        'queue_url': mocks.QUEUE_URL
    })
    monkeypatch.setattr(app, '_S3_RESOURCE', {
        'client': s3,
        'bucket_name': mocks.BUCKET_NAME
    })


class TestTaskEndpoints:
    def test_list_tasks(self, api_client):
        response = api_client('GET', '/dev/tasks')
        assert response['statusCode'] == HTTPStatus.OK

        response_body = parse_body(response)
        assert len(response_body['items']) == len(mocks.TASK_LIST)

    @pytest.mark.parametrize('task_id, expected_http_status', [
        ('a52bc1e1-9f2e-48ab-98f2-b5e4cc059154', HTTPStatus.NOT_FOUND),
        (mocks.NOT_OWNED_DRAFT_TASK['Id'], HTTPStatus.OK)
    ])
    def test_retrieve_task(self, api_client, task_id: str, expected_http_status: int):
        response = api_client('GET', f'/dev/tasks/{task_id}')
        assert response['statusCode'] == expected_http_status

    @pytest.mark.parametrize('task_id, expected_http_status', [
        (mocks.NOT_OWNED_DRAFT_TASK['Id'], HTTPStatus.UNAUTHORIZED),
        (mocks.COMPLETED_TASK['Id'], HTTPStatus.BAD_REQUEST),
        (mocks.DRAFT_TASK['Id'], HTTPStatus.OK)
    ])
    def test_update_task(self, api_client, task_id: str, expected_http_status: int):
        response = api_client(
            'PUT',
            f'/dev/tasks/{task_id}',
            body=mocks.UPDATE_FORM
        )
        assert response['statusCode'] == expected_http_status

    @pytest.mark.parametrize('task_id, expected_http_status', [
        (mocks.NOT_OWNED_DRAFT_TASK['Id'], HTTPStatus.UNAUTHORIZED),
        (mocks.COMPLETED_TASK['Id'], HTTPStatus.BAD_REQUEST),
        (mocks.DRAFT_TASK_TO_SUBMIT['Id'], HTTPStatus.ACCEPTED)
    ])
    def test_task_submit(self, api_client, task_id: str, expected_http_status: int):
        with patch.object(QueueService, 'send_message') as send_message_mock:
            response = api_client(
                'POST',
                f'/dev/tasks/{task_id}/submit',
                body=mocks.UPDATE_FORM
            )

        assert response['statusCode'] == expected_http_status

        if expected_http_status == HTTPStatus.ACCEPTED:
            send_message_mock.assert_called_once()
        else:
            send_message_mock.assert_not_called()


class TestTaskWorkflow:
    def test_request_task_and_submit(self, api_client, dynamodb):
        dynamodb_resource, _ = dynamodb
        
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

        self.update_task_to_completed(task_id, dynamodb_resource)
        response = api_client('GET', detail_task_url)
        assert parse_body(response)['TaskStatus'] == TaskStatusEnum.COMPLETED


        # Step 6: Request S3 signed urls to download outputs files.
        # generate_output_download_urls = '/'.join([detail_task_url, 'generateOutputDownloadUrl'])

        # response = api_client('POST', generate_output_download_urls)
        # assert response['statusCode'] == HTTPStatus.OK

        # TODO: Check download urls.


    def update_task_to_completed(self, task_id, dynamodb):
        table = dynamodb.Table(mocks.TABLE_NAME)

        mock_output = {
            'DetectionsOverPhotogram': {
                'Content': {
                    'Bucket': mocks.BUCKET_NAME,
                    'Key': OUTPUT_PATH_TEMPLATE.format(task_id) + '/detections_over_photogram.csv'
                }
            },
            'FailuresDetected': {
                'Content': {
                    'Bucket': mocks.BUCKET_NAME,
                    'Key': OUTPUT_PATH_TEMPLATE.format(task_id) + '/failures_detected.csv'
                }
            },
            'Sections': {
                'Content': {
                    'Bucket': mocks.BUCKET_NAME,
                    'Key': OUTPUT_PATH_TEMPLATE.format(task_id) + '/sections.csv'
                }
            },
            'SignalsDetected': {
                'Content': {
                    'Bucket': mocks.BUCKET_NAME,
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
