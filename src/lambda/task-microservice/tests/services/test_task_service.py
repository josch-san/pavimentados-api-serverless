import os
from services.task_service import TaskService

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


def test_create_task():
    table_name = 'infra-dev'
    task_service = TaskService(table_name)

    form = {
        'Name': 'Analizando imagenes',
        'Description': 'larga descripcion...',
        'Inputs': {
            'Geography': 'Pichincha',
            'Type': 'video_gps'
        }
    }

    user_id = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'
    bucket_name = 'infra-attachments-dev-195419001736'

    task = task_service.create(form, user_id, bucket_name)
    print(task)

def test_update_attachment_input_item():
    table_name = 'infra-dev'
    task_service = TaskService(table_name)

    task_id = 'ffb0a7bb-4337-4af1-9af5-43362a038715'
    user_id = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'
    bucket_name = 'infra-attachments-dev-195419001736'
    payload = {
        'FieldName': 'VideoFile',
        'ArrayLength': 1,
        'Extension': 'mp4'
    }

    content = task_service.update_attachment_input(task_id, payload, user_id, bucket_name)
    print(content)

def test_update_attachment_array_item():
    table_name = 'infra-dev'
    task_service = TaskService(table_name)

    task_id = '1d44ad6e-3073-4e3a-8fb0-df12cdcdd8bb'
    user_id = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'
    bucket_name = 'infra-attachments-dev-195419001736'
    payload = {
        'FieldName': 'ImageBundle',
        'ArrayLength': 3,
        'Extension': 'zip'
    }

    content = task_service.update_attachment_input(task_id, payload, user_id, bucket_name)
    print(content)
