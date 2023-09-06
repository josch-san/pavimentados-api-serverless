import urllib.parse
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter

# from infra_commons.services.storage_service import StorageService
from services.dataset_service import DatasetService

tracer = Tracer()
router = APIGatewayRouter()


@router.get('/<datasetSlug>/signedUrl')
@tracer.capture_method
def retrieve_dataset(datasetSlug: str):
    dataset_service = DatasetService(router.context.get('dynamodb_resource'))

    return dataset_service.retrieve_by_slug(
        urllib.parse.unquote_plus(datasetSlug)
    )
