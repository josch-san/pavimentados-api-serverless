
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
    '__typename': 'TASK',
    'AccessLevel': 'app'
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
    '__typename': 'TASK',
    'AccessLevel': 'app'
}

TASK_LIST = [
    DRAFT_TASK,
    NOT_OWNED_DRAFT_TASK
]

BOTO3_RESPONSE_TEMPLATE = {
    'ResponseMetadata': {
        'RequestId': 'O599AH19SQJ6H8E1P3FLPHTUPRVV4KQNSO5AEMVJF66Q9ASUAAJG',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'server': 'Server',
            'date': 'Mon, 29 May 2023 13:43:28 GMT',
            'content-type': 'application/x-amz-json-1.0',
            'content-length': '1211',
            'connection': 'keep-alive',
            'x-amzn-requestid': 'O599AH19SQJ6H8E1P3FLPHTUPRVV4KQNSO5AEMVJF66Q9ASUAAJG',
            'x-amz-crc32': '362874364'
        },
        'RetryAttempts': 0
    }
}

# Example of API Gateway REST API request event:
# https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html#apigateway-example-event
API_GATEWAY_EVENT_TEMPLATE = {
    'path': '/dev/tasks',
    'httpMethod': 'GET',
    'requestContext': {
        'authorizer': {
            'claims': {
                'sub': '6b456b08-fa1d-4e24-9fbd-be990e023299',
                'cognito:username': '6b456b08-fa1d-4e24-9fbd-be990e023299',
                'given_name': 'Jose',
                'family_name': 'Hernandez',
                'email': 'jhernandez@sample.co'
            }
        },
        'requestId': '227b78aa-779d-47d4-a48e-ce62120393b8'  # correlation ID
    }
}
