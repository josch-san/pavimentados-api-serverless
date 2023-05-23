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
    bucket = 'infra-attachments-dev-195419001736'

    task = task_service.create(form, user_id, bucket)
    print(task)
