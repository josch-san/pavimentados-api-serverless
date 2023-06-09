TABLE_NAME = 'infra-mock'
BUCKET_NAME = 'infra-attachments-mock'
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789012/pavimentados-queue-mock'
USER_ID = '6b456b08-fa1d-4e24-9fbd-be990e023299'

DRAFT_TASK = {
    'Pk': 'TASK#04bcdf96-db09-46cd-909a-781a3f6dcab9',
    'Id': '04bcdf96-db09-46cd-909a-781a3f6dcab9',
    'UserId': '6b456b08-fa1d-4e24-9fbd-be990e023299',
    'Name': 'Analizando video',
    'Description': 'larga descripcion...',
    'CreatedAt': '2023-05-19T20:04:17.282Z',
    'ModifiedAt': '2023-05-19T20:04:17.282Z',
    'Inputs': {
        'Geography': 'Pichincha',
        'VideoFile': {
            'Extension': 'mp4',
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/04bcdf96-db09-46cd-909a-781a3f6dcab9/inputs/VideoFile_20230519200417.mp4',
                'Uploaded': False
            }
        },
        'GpsFile': {
            'Extension': 'log',
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/04bcdf96-db09-46cd-909a-781a3f6dcab9/inputs/GpsFile_20230519200417.log',
                'Uploaded': False
            }
        },
        'Type': 'video_gps'
    },
    'AppServiceSlug': 'pavimenta2#road_sections_inference',
    'TaskStatus': 'draft',
    'Outputs': None,
    'OutputMessage': None,
    'AccessLevel': 'app',
    '__typename': 'TASK'
}

NOT_OWNED_DRAFT_TASK = {
    'Pk': 'TASK#145fe967-e83a-4f66-821c-b883c9afebca',
    'Id': '145fe967-e83a-4f66-821c-b883c9afebca',
    'UserId': 'cb3923d5-7fb9-4363-8eb9-43dbf0a1185c',
    'Name': 'Analizando video',
    'Description': 'larga descripcion...',
    'CreatedAt': '2023-05-19T20:04:17.282Z',
    'ModifiedAt': '2023-05-19T20:04:17.282Z',
    'Inputs': {
        'Geography': 'Pichincha',
        'VideoFile': {
            'Extension': 'mp4',
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:cb3923d5-7fb9-4363-8eb9-43dbf0a1185c/road_sections_inference/145fe967-e83a-4f66-821c-b883c9afebca/inputs/VideoFile_20230519200417.mp4',
                'Uploaded': False
            }
        },
        'GpsFile': {
            'Extension': 'log',
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:cb3923d5-7fb9-4363-8eb9-43dbf0a1185c/road_sections_inference/145fe967-e83a-4f66-821c-b883c9afebca/inputs/GpsFile_20230519200417.log',
                'Uploaded': False
            }
        },
        'Type': 'video_gps'
    },
    'AppServiceSlug': 'pavimenta2#road_sections_inference',
    'TaskStatus': 'draft',
    'Outputs': None,
    'OutputMessage': None,
    'AccessLevel': 'app',
    '__typename': 'TASK'
}

DRAFT_TASK_TO_SUBMIT = {
    'Pk': 'TASK#523dfef7-878d-4fca-bbe8-1b3a237e47a4',
    'Id': '523dfef7-878d-4fca-bbe8-1b3a237e47a4',
    'UserId': '6b456b08-fa1d-4e24-9fbd-be990e023299',
    'Name': 'Road Section images and gps',
    'Description': 'corta descripcion',
    'CreatedAt': '2023-03-21T19:56:33.303Z',
    'ModifiedAt': '2023-05-01T19:00:16.357Z',
    'Inputs': {
        'Geography': 'Curitiva',
        'GpsFile': {
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/523dfef7-878d-4fca-bbe8-1b3a237e47a4/inputs/GpsFile_20230327174623.txt',
                'Uploaded': True
            },
            'Extension': 'txt'
        },
        'ImageBundle': {
            'Content': [
                {
                    'Bucket': 'infra-attachments-mock',
                    'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/523dfef7-878d-4fca-bbe8-1b3a237e47a4/inputs/ImageBundle_20230529184933_00.zip',
                    'Uploaded': True
                },
                {
                    'Bucket': 'infra-attachments-mock',
                    'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/523dfef7-878d-4fca-bbe8-1b3a237e47a4/inputs/ImageBundle_20230529184933_01.zip',
                    'Uploaded': True
                },
                {
                    'Bucket': 'infra-attachments-mock',
                    'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/523dfef7-878d-4fca-bbe8-1b3a237e47a4/inputs/ImageBundle_20230529184933_02.zip',
                    'Uploaded': True
                }
            ],
            'Extension': 'zip'
        },
        'Type': 'image_bundle_gps'
    },
    'AppServiceSlug': 'pavimenta2#road_sections_inference',
    'TaskStatus': 'draft',
    'Outputs': None,
    'OutputMessage': None,
    'AccessLevel': 'app',
    '__typename': 'TASK'
}

COMPLETED_TASK = {
    'Pk': 'TASK#3bd2c23f-efba-40ec-b969-d490d5fe33bd',
    'Id': '3bd2c23f-efba-40ec-b969-d490d5fe33bd',
    'UserId': '6b456b08-fa1d-4e24-9fbd-be990e023299',
    'Name': 'Analizando video',
    'Description': 'larga descripcion...',
    'CreatedAt': '2023-05-10T14:12:27.123Z',
    'ModifiedAt': '2023-05-10T14:32:37.147Z',
    'Inputs': {
        'Geography': 'Pichincha',
        'GpsFile': {
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/3bd2c23f-efba-40ec-b969-d490d5fe33bd/inputs/GpsFile_20230510141406.log',
                'Uploaded': True
            },
            'Extension': 'log'
        },
        'Type': 'video_gps',
        'VideoFile': {
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/3bd2c23f-efba-40ec-b969-d490d5fe33bd/inputs/VideoFile_20230510141341.mp4',
                'Uploaded': True
            },
            'Extension': 'mp4'
        }
    },
    'Outputs': {
        'DetectionsOverPhotogram': {
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/3bd2c23f-efba-40ec-b969-d490d5fe33bd/outputs/detections_over_photogram.csv'
            }
        },
        'FailuresDetected': {
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/3bd2c23f-efba-40ec-b969-d490d5fe33bd/outputs/failures_detected.csv'
            }
        },
        'Sections': {
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/3bd2c23f-efba-40ec-b969-d490d5fe33bd/outputs/sections.csv'
            }
        },
        'SignalsDetected': {
            'Content': {
                'Bucket': 'infra-attachments-mock',
                'Key': 'pavimenta2/user:6b456b08-fa1d-4e24-9fbd-be990e023299/road_sections_inference/3bd2c23f-efba-40ec-b969-d490d5fe33bd/outputs/signals_detected.csv'
            }
        }
    },
    'OutputMessage': 'Successful processing',
    'AppServiceSlug': 'pavimenta2#road_sections_inference',
    'TaskStatus': 'completed',
    'AccessLevel': 'app',
    '__typename': 'TASK'
}

TASK_LIST = [
    DRAFT_TASK,
    NOT_OWNED_DRAFT_TASK,
    DRAFT_TASK_TO_SUBMIT,
    COMPLETED_TASK
]

DRAFT_VIDEO_GPS_TASK = DRAFT_TASK
DRAFT_IMAGE_BUNDLE_GPS_TASK = DRAFT_TASK_TO_SUBMIT


ATTACHMENT_URL_VIDEO_FILE_FORM = {
    'FieldName': 'VideoFile',
    'ArrayLength': 1,
    'Extension': 'mp4'
}

ATTACHMENT_URL_IMAGE_BUNDLE_FORM = {
    'FieldName': 'ImageBundle',
    'ArrayLength': 5,
    'Extension': 'zip'
}

ATTACHMENT_URL_GPS_FILE_FORM = {
    'FieldName': 'GpsFile',
    'Extension': 'txt'
}

ATTACHMENT_URL_WRONG_EXTENSION_FORM = {
    'FieldName': 'GpsFile',
    'ArrayLength': 1,
    'Extension': 'csv'
}

ATTACHMENT_URL_WRONG_ARRAY_LENGTH_FORM = {
    'FieldName': 'VideoFile',
    'ArrayLength': 3,
    'Extension': 'mp4'
}

ATTACHMENT_URL_WRONG_FILE_NAME_FORM = {
    'FieldName': 'CompressedFile',
    'Extension': 'zip'
}

VIDEO_GPS_CREATE_FORM = {
    'Name': 'Analizando video',
    'Description': 'larga descripcion...',
    'Inputs': {
        'Geography': 'Pichincha',
        'Type': 'video_gps'
    }
}

IMAGE_BUNDLE_GPS_CREATE_FORM = {
    'Name': 'Analizando imagenes con GPS',
    'Description': 'larga descripcion...',
    'Inputs': {
        'Geography': 'Pichincha',
        'Type': 'image_bundle_gps'
    }
}

IMAGE_BUNDLE_CREATE_FORM = {
    'Name': 'Analizando imagenes',
    'Description': 'larga descripcion...',
    'Inputs': {
        'Geography': 'Pichincha',
        'Type': 'image_bundle'
    }
}

UPDATE_FORM = {
    'Name': 'Autopista Nacional TC-153',
    'Description': 'Un analisis muy importante',
    'Inputs': {
        'Geography': 'Monserrat'
    }
}