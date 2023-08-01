import parameter_mappers as mappers
from input_file import InputFile


class InferenceBuilder(object):
    VIDEO_FORMATS = r'\.mp4$'
    GPS_FORMATS = r'\.log$|\.txt$'
    COMPRESSED_FORMATS = r'\.zip$'
    SUPPORTED_INPUT_TYPES = ['video_gps', 'image_bundle_gps', 'image_bundle']

    def __init__(self, task_id, base_code_s3uri):
        self.task_id = task_id
        self.base_code_s3uri = base_code_s3uri

    def build_inference_parameters(self, payload):
        return {
            'JobName': mappers.get_unique_job_name(self.task_id, 'road-sections'),
            'ContainerArguments': payload['container_args'],
            'InputConfig': [
                mappers.get_processing_input('code',
                    self.base_code_s3uri + '/code', '/opt/ml/processing/code'),
                mappers.get_processing_input('inputs',
                    payload['inference_inputs_uri'], '/opt/ml/processing/inputs'),

                mappers.get_processing_input('models',
                    self.base_code_s3uri + '/models.tar.gz', '/opt/ml/processing/models')
            ],
            'OutputConfig': [
                mappers.get_processing_output('outputs',
                    '/opt/ml/processing/outputs', payload['inference_outputs_uri'])
            ]
        }

    def run(self, inputs: dict, user_sub: str):
        if inputs.get('Type') not in self.SUPPORTED_INPUT_TYPES:
            raise Exception(f'Input type {inputs.get("Type")} is not supported.')

        inference_container_args = [
            '--user', user_sub,
            '--task', self.task_id,
            '--type', inputs['Type'],
            '--geography', inputs['Geography']
        ]
        payload = {}

        if inputs['Type'].startswith('video'):
            video_file = InputFile(inputs['VideoFile'], self.VIDEO_FORMATS)

            payload.update({
                'inference_inputs_uri': video_file.inputs_s3_uri,
                'inference_outputs_uri': video_file.build_s3_uri_for_ancestor('outputs')
            })

            inference_container_args.extend([
                '--video_file_name',
                video_file.file_name
            ])

        elif inputs['Type'].startswith('image_bundle'):
            file_names = []

            for s3_file in inputs['ImageBundle']:
                bundle_file = InputFile(s3_file, self.COMPRESSED_FORMATS)
                file_names.append(bundle_file.file_name)

            payload.update({
                'inference_inputs_uri': bundle_file.inputs_s3_uri,
                'inference_outputs_uri': bundle_file.build_s3_uri_for_ancestor('outputs')
            })

            inference_container_args.extend([
                '--image_bundle_file_names',
                *file_names
            ])

        if inputs['Type'].endswith('gps'):
            gps_file = InputFile(inputs['GpsFile'], self.GPS_FORMATS)

            inference_container_args.extend([
                '--gps_file_name',
                gps_file.file_name
            ])

        payload.update({
            'container_args': inference_container_args,
        })

        return self.build_inference_parameters(payload)
