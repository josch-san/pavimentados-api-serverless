from models.task import Task


MOCK_TASK = {
    'Id': 'efd28533-8bb3-4d1e-8e2b-c063a61c006a',
    'Name': 'Analizando imagenes',
    'Description': 'larga descripcion...',
    'UserId': '2ecf2bb8-c700-4073-9d48-2745815dcd0d',
    'CreatedAt': '2023-05-23T17:42:30.766Z',
    'ModifiedAt': '2023-05-23T17:42:30.766Z',
    'TaskStatus': 'draft',
    'AccessLevel': 'app',
    'AppServiceSlug': 'pavimenta2#road_sections_inference',
    'Inputs': {
        'Geography': 'Pichincha',
        'VideoFile': {
            'Extension': 'mp4',
            'Content': {
                'Key': 'pavimenta2/user:2ecf2bb8-c700-4073-9d48-2745815dcd0d/road_sections_inference/efd28533-8bb3-4d1e-8e2b-c063a61c006a/inputs/VideoFile_20230523174230.mp4',
                'Bucket': 'infra-attachments-mock',
                'Uploaded': False
            }
        },
        'GpsFile': {
            'Extension': 'log',
            'Content': {
                'Key': 'pavimenta2/user:2ecf2bb8-c700-4073-9d48-2745815dcd0d/road_sections_inference/efd28533-8bb3-4d1e-8e2b-c063a61c006a/inputs/GpsFile_20230523174230.log',
                'Bucket': 'infra-attachments-mock',
                'Uploaded': False
            }
        },
        'Type': 'video_gps'
    },
    'Outputs': None,
    'OutputMessage': None
 }

def test_instance_video_input_task():
    form = {
        'Name': 'Analizando video',
        'Description': 'larga descripcion...',
        'Inputs': {
            'Geography': 'Pichincha',
            'Type': 'video_gps'
        }
    }

    user_id = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'
    bucket = 'infra-attachments-mock'

    inputs = form.pop('Inputs')
    task = Task.parse_obj({**form, 'UserId': user_id})
    task.initialize_inputs(inputs, bucket)
    
    assert task.Inputs.VideoFile.Content.Key.startswith(f'pavimenta2/user:{user_id}/road_sections_inference/{task.Id}/inputs/VideoFile_')
    assert task.Inputs.GpsFile.Content.Key.startswith(f'pavimenta2/user:{user_id}/road_sections_inference/{task.Id}/inputs/GpsFile_')


def test_instance_image_input_task():
    form = {
        'Name': 'Analizando imagenes',
        'Description': 'larga descripcion...',
        'Inputs': {
            'Geography': 'Pichincha',
            'Type': 'image_bundle_gps'
        }
    }

    user_id = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'
    bucket = 'infra-attachments-mock'

    inputs = form.pop('Inputs')
    task = Task.parse_obj({**form, 'UserId': user_id})
    task.initialize_inputs(inputs, bucket)
    
    assert task.Inputs.ImageBundle.Content[0].Key.startswith(f'pavimenta2/user:{user_id}/road_sections_inference/{task.Id}/inputs/ImageBundle_')
    assert task.Inputs.GpsFile.Content.Key.startswith(f'pavimenta2/user:{user_id}/road_sections_inference/{task.Id}/inputs/GpsFile_')


def test_update_attachment_input():
    bucket_name = 'infra-attachments-mock'
    payload = {
        'FieldName': 'GpsFile',
        'Extension': 'txt'
    }

    task = Task.parse_obj(MOCK_TASK)
    task.update_attachment_input(payload, bucket_name)

    path, file_name = task.Inputs.GpsFile.Content.Key.rsplit('/', 1)
    assert path == f'pavimenta2/user:{task.UserId}/road_sections_inference/{task.Id}/inputs'
    assert file_name.startswith('GpsFile_')
    assert file_name.endswith('.txt')
