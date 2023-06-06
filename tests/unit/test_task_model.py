import sys
sys.path.append('./src/lambda/task-microservice')

from models.task import Task
from tests import mocks

BUCKET_NAME = 'infra-attachments-mock'
USER_ID = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'


class TestTaskModelFeatures:
    def test_instance_video_input_task(self):
        form = {
            'Name': 'Analizando video',
            'Description': 'larga descripcion...',
            'Inputs': {
                'Geography': 'Pichincha',
                'Type': 'video_gps'
            }
        }

        inputs = form.pop('Inputs')
        task = Task.parse_obj({**form, 'UserId': USER_ID})
        task.initialize_inputs(inputs, BUCKET_NAME)

        assert task.Inputs.VideoFile.Content.Key.startswith(f'pavimenta2/user:{USER_ID}/road_sections_inference/{task.Id}/inputs/VideoFile_')
        assert task.Inputs.GpsFile.Content.Key.startswith(f'pavimenta2/user:{USER_ID}/road_sections_inference/{task.Id}/inputs/GpsFile_')


    def test_instance_image_input_task(self):
        form = {
            'Name': 'Analizando imagenes',
            'Description': 'larga descripcion...',
            'Inputs': {
                'Geography': 'Pichincha',
                'Type': 'image_bundle_gps'
            }
        }

        inputs = form.pop('Inputs')
        task = Task.parse_obj({**form, 'UserId': USER_ID})
        task.initialize_inputs(inputs, BUCKET_NAME)

        assert task.Inputs.ImageBundle.Content[0].Key.startswith(f'pavimenta2/user:{USER_ID}/road_sections_inference/{task.Id}/inputs/ImageBundle_')
        assert task.Inputs.GpsFile.Content.Key.startswith(f'pavimenta2/user:{USER_ID}/road_sections_inference/{task.Id}/inputs/GpsFile_')


    def test_update_attachment_input(self):
        payload = {
            'FieldName': 'GpsFile',
            'Extension': 'txt'
        }

        task = Task.parse_obj(mocks.DRAFT_TASK)
        task.update_attachment_input(payload, BUCKET_NAME)

        path, file_name = task.Inputs.GpsFile.Content.Key.rsplit('/', 1)
        assert path == f'pavimenta2/user:{task.UserId}/road_sections_inference/{task.Id}/inputs'
        assert file_name.startswith('GpsFile_')
        assert file_name.endswith('.txt')
