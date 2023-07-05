import boto3


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    available_files = {}

    for output in event['OutputConfig']:
        *_, bucket, key = output['S3Output']['S3Uri'].split('/', 3)
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=key)

        available_files.update({
            to_camel_case(item['Key'].split('/')[-1].split('.')[0]): {
                'Content': {
                    'Key': item['Key'],
                    'Bucket': bucket
                }
            }
            for item in response['Contents']
        })

    return available_files


def to_camel_case(snake_str):
    return ''.join(x.capitalize() for x in snake_str.lower().split('_'))
