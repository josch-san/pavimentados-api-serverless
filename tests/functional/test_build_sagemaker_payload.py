import os
import sys

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
sys.path.append('src/lambda/build-payload')
sys.path.append('src/lambda/task-microservice')
sys.path.append('src/layers/endpoints-dependencies')

from models.task import Task
from inference_builder import InferenceBuilder

from tests import mocks


class TestBuildSagemakerPayload:
    def test_build_payload_function(self):
        task = Task.parse_obj(mocks.QUEUED_TASK)
        event = task.build_event_payload()
        base_code_s3uri = 's3://infra-artifacts-mock/pavimenta2/sagemaker/road-section-inference'

        builder = InferenceBuilder(event['Id'], base_code_s3uri)

        payload = builder.run(
            event['Inputs'],
            user_sub=event['UserSub']
        )

        assert payload['ContainerArguments'] == [
            '--user', '6b456b08-fa1d-4e24-9fbd-be990e023299',
            '--task', '523dfef7-878d-4fca-bbe8-1b3a237e47a4',
            '--type', 'image_bundle_gps',
            '--geography', 'Curitiva',
            '--image_bundle_file_names', 'ImageBundle_20230529184933_00.zip',
                'ImageBundle_20230529184933_01.zip', 'ImageBundle_20230529184933_02.zip',
            '--gps_file_name', 'GpsFile_20230327174623.txt']
