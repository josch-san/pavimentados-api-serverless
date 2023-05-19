from models.task import Task


def test_instance_task():
    form = {
        'Name': 'Analizando video',
        'Description': 'larga descripcion...',
        'Inputs': {
            'Geography': 'Pichincha',
            'Type': 'video_gps'
        }
    }

    user_id = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'
    bucket = 'infra-attachments-dev-195419001736'

    inputs = form.pop('Inputs')
    task = Task.parse_obj({**form, 'UserId': user_id})
    task.initialize_inputs(inputs, bucket)
    
    assert task.Inputs.VideoFile.Content.Key.startswith(f'pavimenta2/user:{user_id}/road_sections_inference/{task.Id}/inputs/VideoFile_')
    assert task.Inputs.GpsFile.Content.Key.startswith(f'pavimenta2/user:{user_id}/road_sections_inference/{task.Id}/inputs/GpsFile_')
