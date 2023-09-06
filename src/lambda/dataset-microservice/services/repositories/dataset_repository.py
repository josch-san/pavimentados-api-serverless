from boto3.dynamodb.conditions import Attr
from pydantic import parse_obj_as

from models.dataset import Dataset
from infra_commons.aws_resources import LambdaDynamoDB
from infra_commons.utils import to_dynamodb_format


class DatasetRepository:
    def __init__(self, resource: LambdaDynamoDB):
        self.resource = resource

    def list_datasets(self) -> list[Dataset]:
        response = self.resource.table.scan(
            FilterExpression=Attr('__typename').eq('Dataset')
        )

        return parse_obj_as(list[Dataset], response['Items'])

    # https://aws.amazon.com/blogs/database/simulating-amazon-dynamodb-unique-constraints-using-transactions/
    def create_dataset(self, form: dict) -> Dataset:
        dataset = Dataset.parse_obj(form)

        self.resource.client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': self.resource.table_name,
                        'Item': to_dynamodb_format(dataset.dynamodb_record),
                        'ConditionExpression': 'attribute_not_exists(Pk)'
                    }
                },
                {
                    'Put': {
                        'TableName': self.resource.table_name,
                        'Item': to_dynamodb_format({
                            'Pk': f'DATASET#{dataset.Slug}',
                            'Id': str(dataset.Id)
                        }),
                        'ConditionExpression': 'attribute_not_exists(Pk)'
                    }
                }
            ]
        )

        return dataset

    def get_dataset(self, dataset_id: str) -> Dataset:
        response = self.resource.table.get_item(
            Key=Dataset.build_dynamodb_key(dataset_id)
        )

        return Dataset.parse_obj(response['Item'])

    def get_dataset_by_slug(self, dataset_slug: str) -> Dataset:
        response = self.resource.table.scan(
            FilterExpression=(
                Attr('__typename').eq('Dataset') &
                Attr('Slug').eq(dataset_slug)
            )
        )

        return Dataset.parse_obj(response['Items'][0])
