import sys
from unittest.mock import Mock

import pytest
from aws_lambda_powertools.event_handler.exceptions import BadRequestError

sys.path.append('src/lambda/task-microservice')

from services.task_service import TaskService
from models.task import Task

from tests import mocks

TABLE_NAME = 'infra-mock'
BUCKET_NAME = 'infra-attachments-mock'
USER_ID = '6b456b08-fa1d-4e24-9fbd-be990e023299'

@pytest.fixture
def table_mock():
    return Mock(name='dynamodb_table')


@pytest.fixture
def task_service(table_mock):
    return TaskService(Mock(table=table_mock))


class TestTaskService:
    def test_create_task(self, task_service, table_mock):
        form = {
            'Name': 'Analizando imagenes',
            'Description': 'larga descripcion...',
            'Inputs': {
                'Geography': 'Pichincha',
                'Type': 'video_gps'
            }
        }

        task_service.create(form, USER_ID, BUCKET_NAME)
        table_mock.put_item.assert_called_once()

    def test_create_incomplete_form(self, task_service, table_mock):
        form = {
            'Name': 'Analizando imagenes',
            'Description': 'larga descripcion...',
            'Inputs': {
                'Geography': 'Pichincha',
                # 'Type': 'video_gps'
            }
        }

        with pytest.raises(BadRequestError):
            task_service.create(form, USER_ID, BUCKET_NAME)
        table_mock.put_item.assert_not_called()

    @pytest.mark.parametrize('task, payload', [
        (mocks.DRAFT_VIDEO_GPS_TASK, {
            'FieldName': 'VideoFile',
            'Extension': 'mp4'
        }),
        (mocks.DRAFT_IMAGE_BUNDLE_GPS_TASK, {
            'FieldName': 'ImageBundle',
            'ArrayLength': 5,
            'Extension': 'zip'
        })
    ])
    def test_update_attachment_item(self, task_service, table_mock, task: dict, payload: dict):
        dynamodb_key = Task.build_dynamodb_key(task['Id'])
        table_mock.get_item.return_value = {'Item': task}

        task_service.update_attachment_input(task['Id'], payload, USER_ID, BUCKET_NAME)
        update_kwargs = table_mock.update_item.call_args.kwargs

        table_mock.get_item.assert_called_once_with(Key=dynamodb_key)
        assert update_kwargs['Key'] == dynamodb_key
        assert payload['FieldName'] in update_kwargs['ExpressionAttributeNames'].values()
