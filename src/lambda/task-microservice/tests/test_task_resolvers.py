import os
from http import HTTPStatus

from boto3.dynamodb.types import TypeSerializer
from botocore.stub import Stubber, ANY
import pytest

import sys
sys.path.append('..')
from tests import mocks

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

from services.repositories.task_repository import dynamodb
from services.queue_service import sqs_client
# from models.task import Task
import app

ddb_serializer = TypeSerializer()
serialize_to_ddb_record = lambda item: {key: ddb_serializer.serialize(value) for key, value in item.items()}


@pytest.fixture(autouse=True)
def set_environment_varibles(monkeypatch):
    monkeypatch.setattr(app, 'TABLE_NAME', 'infra-mock')
    monkeypatch.setattr(app, 'ATTACHMENTS_BUCKET_NAME', 'infra-attachments-mock')
    monkeypatch.setattr(app, 'TASK_QUEUE_URL', 'pavimentados-queue-mock')


@pytest.fixture(autouse=True)
def dynamodb_stub():
    with Stubber(dynamodb.meta.client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


@pytest.fixture
def sqs_stub():
    with Stubber(sqs_client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


def test_list_tasks(lambda_context, build_api_request, dynamodb_stub):
    event = build_api_request('GET', '/dev/tasks')

    dynamodb_stub.add_response(
        'scan',
        expected_params={
            'TableName': 'infra-mock',
            'FilterExpression': ANY
        },
        service_response={
            **mocks.BOTO3_RESPONSE_TEMPLATE,
            'Items': [serialize_to_ddb_record(task) for task in mocks.TASK_LIST]
        }
    )

    response = app.lambda_handler(event, lambda_context)
    assert response['statusCode'] == HTTPStatus.OK


def test_retrieve_task(lambda_context, build_api_request, dynamodb_stub):
    event = build_api_request('GET', '/dev/tasks/145fe967-e83a-4f66-821c-b883c9afebca')

    dynamodb_stub.add_response(
        'get_item',
        expected_params={
            'TableName': 'infra-mock',
            'Key': {'Pk': 'TASK#145fe967-e83a-4f66-821c-b883c9afebca'}
        },
        service_response={
            **mocks.BOTO3_RESPONSE_TEMPLATE,
            'Item': serialize_to_ddb_record(mocks.NOT_OWNED_DRAFT_TASK)
        }
    )

    response = app.lambda_handler(event, lambda_context)
    assert response['statusCode'] == HTTPStatus.OK


def test_retrieve_task_404(lambda_context, build_api_request, dynamodb_stub):
    # This task_id doesn't exists in db.
    event = build_api_request('GET', '/dev/tasks/a52bc1e1-9f2e-48ab-98f2-b5e4cc059154')

    dynamodb_stub.add_response(
        'get_item',
        expected_params={
            'TableName': 'infra-mock',
            'Key': {'Pk': 'TASK#a52bc1e1-9f2e-48ab-98f2-b5e4cc059154'}
        },
        service_response=mocks.BOTO3_RESPONSE_TEMPLATE
    )

    response = app.lambda_handler(event, lambda_context)
    assert response['statusCode'] == HTTPStatus.NOT_FOUND


def test_generate_attachment_upload_url_unauthorized(lambda_context, build_api_request, dynamodb_stub):
    event = build_api_request(
        'POST',
        '/dev/tasks/145fe967-e83a-4f66-821c-b883c9afebca/generateAttachmentUploadUrl',
        body={
            'FieldName': 'VideoFile',
            'ArrayLength': 1,
            'Extension': 'mp4'
        }
    )

    dynamodb_stub.add_response(
        'get_item',
        expected_params={
            'TableName': 'infra-mock',
            'Key': {'Pk': 'TASK#145fe967-e83a-4f66-821c-b883c9afebca'}
        },
        service_response={
            **mocks.BOTO3_RESPONSE_TEMPLATE,
            'Item': serialize_to_ddb_record(mocks.NOT_OWNED_DRAFT_TASK)
        }
    )
    response = app.lambda_handler(event, lambda_context)
    assert response['statusCode'] == HTTPStatus.UNAUTHORIZED


def test_update_draft_task(lambda_context, build_api_request, dynamodb_stub):
    event = build_api_request(
        'PUT',
        '/dev/tasks/04bcdf96-db09-46cd-909a-781a3f6dcab9',
        body={
            'Name': 'Cambio nombre',
            'Description': 'Larga descripcion'
        }
    )

    dynamodb_stub.add_response(
        'get_item',
        expected_params={
            'TableName': 'infra-mock',
            'Key': {'Pk': 'TASK#04bcdf96-db09-46cd-909a-781a3f6dcab9'}
        },
        service_response={
            **mocks.BOTO3_RESPONSE_TEMPLATE,
            'Item': serialize_to_ddb_record(mocks.DRAFT_TASK)
        }
    )

    response = app.lambda_handler(event, lambda_context)
    assert response['statusCode'] == HTTPStatus.OK


# def test_generate_attachment_upload_url(lambda_context, build_api_request, dynamodb_stub):
#     event = build_api_request(
#         'POST',
#         '/dev/tasks/04bcdf96-db09-46cd-909a-781a3f6dcab9/generateAttachmentUploadUrl',
#         body={
#             'FieldName': 'VideoFile',
#             'ArrayLength': 1,
#             'Extension': 'mp4'
#         }
#     )

#     dynamodb_stub.add_response(
#         'get_item',
#         expected_params={
#             'TableName': 'infra-mock',
#             'Key': {'Pk': 'TASK#04bcdf96-db09-46cd-909a-781a3f6dcab9'}
#         },
#         service_response={
#             **mocks.BOTO3_RESPONSE_TEMPLATE,
#             'Item': serialize_to_ddb_record(mocks.DRAFT_TASK)
#         }
#     )

#     dynamodb_stub.add_response(
#         'update_item',
#         expected_params={
#             'TableName': 'infra-mock',
#             'Key': {'Pk': 'TASK#04bcdf96-db09-46cd-909a-781a3f6dcab9'},
#             'UpdateExpression': f'SET Inputs.#key00 = :value00',
#             'ExpressionAttributeNames': {'#key00': 'VideoFile'},
#             'ExpressionAttributeValues': {':value00': ANY}
#         },
#         service_response=mocks.BOTO3_RESPONSE_TEMPLATE
#     )

#     response = app.lambda_handler(event, lambda_context)
#     assert response['statusCode'] == HTTPStatus.OK


def test_task_submit(lambda_context, build_api_request, dynamodb_stub: Stubber, sqs_stub: Stubber):
    event = build_api_request('POST', '/dev/tasks/04bcdf96-db09-46cd-909a-781a3f6dcab9/submit')

    dynamodb_stub.add_response(
        'get_item',
        expected_params={
            'TableName': 'infra-mock',
            'Key': {'Pk': 'TASK#04bcdf96-db09-46cd-909a-781a3f6dcab9'}
        },
        service_response={
            **mocks.BOTO3_RESPONSE_TEMPLATE,
            'Item': serialize_to_ddb_record(mocks.DRAFT_TASK)
        }
    )

    sqs_stub.add_response(
        'send_message',
        expected_params={
            'QueueUrl': 'pavimentados-queue-mock',
            'MessageBody': ANY
            # 'MessageBody': Task.parse_obj(mocks.DRAFT_TASK).build_sqs_message()
        },
        service_response={
            **mocks.BOTO3_RESPONSE_TEMPLATE,
            'MD5OfMessageBody': 'caf62113c6147e8cbce6c193d0214d07',
            'MessageId': '79c109cc-1812-4986-c4cf-046ba4f781e2'
        }
    )

    response = app.lambda_handler(event, lambda_context)

    # TODO: Assert code status changed
    assert response['statusCode'] == HTTPStatus.ACCEPTED
