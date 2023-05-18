from models.task import Task


def test_instance_task():
    form = {
        'Name': 'Analizando video',
        'Description': 'larga descripcion...',
        'Inputs': {
            'Geography': 'Pichincha',
            'GpsFile': {
            'Content': {
                'Bucket': 'infra-attachments-dev-195419001736',
                'Key': 'pavimenta2/user:2ecf2bb8-c700-4073-9d48-2745815dcd0d/road_sections_inference/db4e6a6c-d768-4b43-ad8c-99b579c8c23b/inputs/GpsFile_20230510141406.log',
                'Uploaded': True
            },
            'Extension': 'log'
            },
            'Type': 'video_gps',
            'VideoFile': {
            'Content': {
                'Bucket': 'infra-attachments-dev-195419001736',
                'Key': 'pavimenta2/user:2ecf2bb8-c700-4073-9d48-2745815dcd0d/road_sections_inference/db4e6a6c-d768-4b43-ad8c-99b579c8c23b/inputs/VideoFile_20230510141341.mp4',
                'Uploaded': True
            },
            'Extension': 'mp4'
            }
        }
    }

    user_id = '2ecf2bb8-c700-4073-9d48-2745815dcd0d'

    try:
        task = Task.parse_obj({**form, 'UserId': user_id})
    except Exception as e:
        print(e)

    print(task)
