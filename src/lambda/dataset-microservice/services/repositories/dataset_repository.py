# from pydantic import parse_obj_as

from models.dataset import Dataset
from infra_commons.aws_resources import LambdaDynamoDB
from infra_commons.utils import to_dynamodb_format


class DatasetRepository:
    def __init__(self, resource: LambdaDynamoDB):
        self.resource = resource

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
