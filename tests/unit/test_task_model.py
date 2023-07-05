import sys
sys.path.append('src/lambda/task-microservice')

from models.task import Task
from tests import mocks


class TestTaskModelFeatures:
    def test_instance_video_input_task(self):
        form = mocks.VIDEO_GPS_CREATE_FORM.copy()

        inputs = form.pop('Inputs')
        task = Task.parse_obj({**form, 'UserSub': mocks.USER_SUB})
        task.initialize_inputs(inputs, mocks.BUCKET_NAME)

        assert task.Inputs.VideoFile.Content.Key.startswith(f'pavimenta2/user:{mocks.USER_SUB}/road_sections_inference/{task.Id}/inputs/VideoFile_')
        assert task.Inputs.GpsFile.Content.Key.startswith(f'pavimenta2/user:{mocks.USER_SUB}/road_sections_inference/{task.Id}/inputs/GpsFile_')


    def test_instance_image_input_task(self):
        form = mocks.IMAGE_BUNDLE_GPS_CREATE_FORM.copy()

        inputs = form.pop('Inputs')
        task = Task.parse_obj({**form, 'UserSub': mocks.USER_SUB})
        task.initialize_inputs(inputs, mocks.BUCKET_NAME)

        assert task.Inputs.ImageBundle.Content[0].Key.startswith(f'pavimenta2/user:{mocks.USER_SUB}/road_sections_inference/{task.Id}/inputs/ImageBundle_')
        assert task.Inputs.GpsFile.Content.Key.startswith(f'pavimenta2/user:{mocks.USER_SUB}/road_sections_inference/{task.Id}/inputs/GpsFile_')


    def test_update_attachment_input(self):
        task = Task.parse_obj(mocks.DRAFT_TASK)
        task.update_attachment_input(mocks.ATTACHMENT_URL_GPS_FILE_FORM, mocks.BUCKET_NAME)

        path, file_name = task.Inputs.GpsFile.Content.Key.rsplit('/', 1)
        assert path == f'pavimenta2/user:{task.UserSub}/road_sections_inference/{task.Id}/inputs'
        assert file_name.startswith('GpsFile_')
        assert file_name.endswith('.txt')
