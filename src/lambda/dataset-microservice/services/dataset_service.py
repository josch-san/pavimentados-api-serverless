from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError,
    BadRequestError
)

from infra_commons.aws_resources import LambdaDynamoDB
from services.repositories.dataset_repository import DatasetRepository
from models.dataset import Dataset

logger = Logger(child=True)


class DatasetService:
    def __init__(self, dynamodb_resource: LambdaDynamoDB):
        self.repository = DatasetRepository(dynamodb_resource)

    def list(self) -> list[Dataset]:
        return self.repository.list_datasets()

    def create(self, form: dict, user_sub: str) -> Dataset:
        form['UserSub'] = user_sub

        try:
            dataset = self.repository.create_dataset(form)

        except ClientError as e:
            if e.response['Error']['Code'] == 'TransactionCanceledException':
                if any(
                    reason['Code'] == 'ConditionalCheckFailed'
                    for reason in e.response['CancellationReasons']
                ):
                    raise BadRequestError(f"Dataset with '{form['Slug']}' Slug already exists.")

            raise e

        except Exception as e:
            logger.error(e.errors())
            raise BadRequestError('Dataset could not be created.')

        logger.info('Dataset successful created.')
        return dataset

    def retrieve(self, dataset_id: str) -> Dataset:
        try:
            dataset = self.repository.get_dataset(dataset_id)
        except KeyError:
            raise NotFoundError

        return dataset

    def destroy(self, dataset_id: str) -> None:
        dataset = self.retrieve(dataset_id)

        try:
            self.repository.delete_dataset(dataset)

        except ClientError as e:
            if e.response['Error']['Code'] == 'TransactionCanceledException':
                if any(
                    reason['Code'] == 'ConditionalCheckFailed'
                    for reason in e.response['CancellationReasons']
                ):
                    raise BadRequestError(f"Dataset with '{dataset_id}' Id could not be deleted.")

            raise e

    def retrieve_by_slug(self, dataset_slug: str) -> Dataset:
        try:
            dataset = self.repository.get_dataset_by_slug(dataset_slug)
        except IndexError:
            raise NotFoundError

        return dataset
