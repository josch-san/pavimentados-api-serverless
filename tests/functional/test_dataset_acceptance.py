import os
import sys
import json
from http import HTTPStatus
from dataclasses import dataclass

import pytest

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
sys.path.append('src/layers/endpoints-dependencies')
sys.path.append('src/lambda/dataset-microservice')

# from models.dataset import Dataset
import app

from tests.mocks import dataset_microservice as mocks

def parse_body(response):
    return json.loads(response['body'])


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = 'dataset-microservice-mock'
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = 'arn:aws:lambda:us-east-1:123456789012:function:dataset-microservice-mock'
        aws_request_id: str = 'da658bd3-2d6f-4e7b-8ec2-937234644fdc'

    return LambdaContext()


@pytest.fixture
def api_client(lambda_context, build_api_request):
    def _resolve_request(*args, **kwargs):
        event = build_api_request(*args, **kwargs)
        return app.lambda_handler(event, lambda_context)

    return _resolve_request


@pytest.fixture(autouse=True)
def set_aws_resources(monkeypatch, dynamodb, s3):
    dynamodb_resource, dynamodb_client = dynamodb

    monkeypatch.setattr(app, '_DYNAMODB_RESOURCE', {
        'client': dynamodb_client,
        'resource': dynamodb_resource,
        'table_name': mocks.TABLE_NAME
    })
    monkeypatch.setattr(app, '_S3_RESOURCE', {
        'client': s3,
        'bucket_name': mocks.BUCKET_NAME
    })

class TestDatasetEndpoints:
    def test_create_dataset(self, api_client):
        create_form = {
            'Name': 'Geography resource to pavimentados request form - CO',
            'Slug': 'pavimenta2#geography_road_co',
            'Description': 'larga descripcion...',
            'AccessLevel': 'public',
            'RepositoryType': 'amazon-s3',
            'Config': {
                'Bucket': 'ineiadb-infradigital-datalake-dev',
                'Key': 'pavimenta2/geography/geography_road_co.json'
            }
        }

        response = api_client('POST', '/admin/datasets', body=create_form)
        assert response['statusCode'] == HTTPStatus.CREATED
