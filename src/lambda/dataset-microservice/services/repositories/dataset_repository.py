# from boto3.dynamodb.conditions import Attr
# from pydantic import parse_obj_as

from models.dataset import Dataset
from infra_commons.aws_resources import LambdaDynamoDB


class DatasetRepository:
    def __init__(self, resource: LambdaDynamoDB):
        self.resource = resource

    def create_dataset(self, form: dict) -> Dataset:
        dataset = Dataset.parse_obj(form)
        self.resource.table.put_item(
            Item=dataset.dynamodb_record
        )

        return dataset
