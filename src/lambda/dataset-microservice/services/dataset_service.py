from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError
)

from infra_commons.aws_resources import LambdaDynamoDB
from services.repositories.dataset_repository import DatasetRepository
from models.dataset import Dataset

logger = Logger(child=True)


class DatasetService:
    def __init__(self, dynamodb_resource: LambdaDynamoDB):
        self.repository = DatasetRepository(dynamodb_resource)

    def create(self, form: dict, user_sub: str) -> Dataset:
        form['UserSub'] = user_sub

        try:
            dataset = self.repository.create_dataset(form)

        except Exception as e:
            logger.error(e.errors())
            raise BadRequestError('Dataset could not be created.')

        logger.info('Dataset successful created.')
        return dataset
