import sys
from unittest.mock import Mock

import pytest
from aws_lambda_powertools.event_handler.exceptions import BadRequestError

sys.path.append('src/lambda/task-microservice')

from services.task_service import TaskService
from models.task import Task, TaskStatusEnum

from tests import mocks


@pytest.fixture
def table_mock():
    return Mock(name='dynamodb_table')


@pytest.fixture
def task_service(table_mock):
    return TaskService(Mock(table=table_mock))


class TestTaskService:
    def test_create_task(self, task_service, table_mock):
        task_service.create(mocks.VIDEO_GPS_CREATE_FORM.copy(), mocks.USER_ID, mocks.BUCKET_NAME)
        table_mock.put_item.assert_called_once()

    def test_create_incomplete_form(self, task_service, table_mock):
        form = mocks.VIDEO_GPS_CREATE_FORM.copy()
        form['Inputs'].pop('Type')

        with pytest.raises(BadRequestError):
            task_service.create(form, mocks.USER_ID, mocks.BUCKET_NAME)
        table_mock.put_item.assert_not_called()

    @pytest.mark.parametrize('task, payload', [
        (mocks.DRAFT_VIDEO_GPS_TASK, mocks.ATTACHMENT_URL_VIDEO_FILE_FORM),
        (mocks.DRAFT_IMAGE_BUNDLE_GPS_TASK, mocks.ATTACHMENT_URL_IMAGE_BUNDLE_FORM)
    ])
    def test_update_attachment_input(self, task_service, table_mock, task: dict, payload: dict):
        dynamodb_key = Task.build_dynamodb_key(task['Id'])
        table_mock.get_item.return_value = {'Item': task}

        task_service.update_attachment_input(task['Id'], payload, mocks.USER_ID, mocks.BUCKET_NAME)
        update_kwargs = table_mock.update_item.call_args.kwargs

        table_mock.get_item.assert_called_once_with(Key=dynamodb_key)
        assert update_kwargs['Key'] == dynamodb_key
        assert {'Inputs.' + payload['FieldName'], 'ModifiedAt'} == set(update_kwargs['ExpressionAttributeNames'].values())

    def test_update_task(self, task_service, table_mock):
        dynamodb_key = Task.build_dynamodb_key(mocks.DRAFT_TASK['Id'])
        table_mock.get_item.return_value = {'Item': mocks.DRAFT_TASK}

        task_service.update(mocks.DRAFT_TASK['Id'], mocks.UPDATE_FORM, mocks.USER_ID)
        update_kwargs = table_mock.update_item.call_args.kwargs

        table_mock.get_item.assert_called_once_with(Key=dynamodb_key)
        assert update_kwargs['Key'] == dynamodb_key
        assert {'Name', 'Description', 'Inputs.Geography', 'ModifiedAt'} == set(update_kwargs['ExpressionAttributeNames'].values())

    def test_update_to_submit(self, task_service, table_mock):
        dynamodb_key = Task.build_dynamodb_key(mocks.DRAFT_TASK['Id'])
        table_mock.get_item.return_value = {'Item': mocks.DRAFT_TASK}

        task = task_service.update_to_submit(mocks.DRAFT_TASK['Id'], mocks.USER_ID)
        assert task.TaskStatus == TaskStatusEnum.QUEUED
        update_kwargs = table_mock.update_item.call_args.kwargs

        table_mock.get_item.assert_called_once_with(Key=dynamodb_key)
        assert update_kwargs['Key'] == dynamodb_key
        assert {'TaskStatus', 'ModifiedAt'} == set(update_kwargs['ExpressionAttributeNames'].values())
