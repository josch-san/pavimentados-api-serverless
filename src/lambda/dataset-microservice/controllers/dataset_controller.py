import urllib.parse
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    UnauthorizedError
)

from infra_commons.services.storage_service import StorageService
from services.dataset_service import DatasetService
from models.dataset import AccessLevelEnum, RepositoryTypeEnum

tracer = Tracer()
router = APIGatewayRouter()


@router.get('/<datasetSlug>/signedUrl')
@tracer.capture_method
def get_public_dataset_signed_url(datasetSlug: str):
    dataset_service = DatasetService(router.context.get('dynamodb_resource'))
    storage_service = StorageService(router.context.get('s3_resource'))

    decoded_dataset_slug = urllib.parse.unquote_plus(datasetSlug)
    dataset = dataset_service.retrieve_by_slug(
        decoded_dataset_slug.lower()
    )

    if dataset.AccessLevel != AccessLevelEnum.PUBLIC:
        raise UnauthorizedError('This dataset is not publicly accessible')

    if dataset.RepositoryType != RepositoryTypeEnum.AMAZON_S3:
        raise BadRequestError('Dataset RepositoryType must be "amazon-s3" to return signed url')

    return {
        'url': storage_service.generate_signed_download_url(dataset.DatasetConfig)
    }
