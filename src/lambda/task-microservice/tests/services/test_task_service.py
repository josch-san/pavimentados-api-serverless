import os
import pytest

from models.base_task import TaskStatusEnum
from services.task_service import TaskService

# import sys
# sys.path.append('..')
from tests import mocks

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def task_service():
    table_name = 'infra-mock'
    return TaskService(table_name)


def test_create_task(task_service: TaskService):
    form = {
        'Name': 'Analizando imagenes',
        'Description': 'larga descripcion...',
        'Inputs': {
            'Geography': 'Pichincha',
            'Type': 'video_gps'
        }
    }

    user_id = '6b456b08-fa1d-4e24-9fbd-be990e023299'
    bucket_name = 'infra-attachments-dev-195419001736'

    task = task_service.create(form, user_id, bucket_name)
    print(task)


def test_update_attachment_input_item(task_service: TaskService):
    task_id = 'ffb0a7bb-4337-4af1-9af5-43362a038715'
    user_id = '6b456b08-fa1d-4e24-9fbd-be990e023299'
    bucket_name = 'infra-attachments-dev-195419001736'
    payload = {
        'FieldName': 'VideoFile',
        'ArrayLength': 1,
        'Extension': 'mp4'
    }

    content = task_service.update_attachment_input(task_id, payload, user_id, bucket_name)
    print(content)


def test_update_attachment_array_item(task_service: TaskService):
    task_id = '1d44ad6e-3073-4e3a-8fb0-df12cdcdd8bb'
    user_id = '6b456b08-fa1d-4e24-9fbd-be990e023299'
    bucket_name = 'infra-attachments-dev-195419001736'
    payload = {
        'FieldName': 'ImageBundle',
        'ArrayLength': 3,
        'Extension': 'zip'
    }

    content = task_service.update_attachment_input(task_id, payload, user_id, bucket_name)
    print(content)


def test_update_to_submit(task_service: TaskService):
    task_id = '3bd2c23f-efba-40ec-b969-d490d5fe33bd'
    user_id = '6b456b08-fa1d-4e24-9fbd-be990e023299'

    task = task_service.update_to_submit(task_id, user_id)
    assert task.TaskStatus == TaskStatusEnum.QUEUED
