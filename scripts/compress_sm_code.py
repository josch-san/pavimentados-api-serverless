from pathlib import Path

import boto3

s3_client = boto3.client('s3')

def upload_without_package(ntl_code_path, bucket, key):
    for file_path in ntl_code_path.iterdir():
        if file_path.is_dir():
            upload_without_package(file_path, bucket, '/'.join([key, file_path.name]))
            continue

        s3_client.upload_file(str(file_path), bucket, '/'.join([key, file_path.name]))


if __name__ == '__main__':
    bucket = 'infra-artifacts-dev'
    rsi_code_path = Path('src/sagemaker/road-section-inference/code')

    code_key = 'pavimenta2/sagemaker/road-section-inference/code'
    upload_without_package(rsi_code_path, bucket, code_key)

    print('uploaded files.')
