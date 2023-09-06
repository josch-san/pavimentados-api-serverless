from http import HTTPStatus
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# from infra_commons.services.storage_service import StorageService
from services.dataset_service import DatasetService

tracer = Tracer()
router = APIGatewayRouter()


def get_user_sub(event: APIGatewayProxyEvent):
    return event.request_context.authorizer.claims['sub']


@router.get('/')
@tracer.capture_method
def list_datasets():
    dataset_service = DatasetService(router.context.get('dynamodb_resource'))

    datasets = dataset_service.list()
    return {
        'items': datasets
    }


@router.post('/')
@tracer.capture_method
def create_dataset():
    dataset_service = DatasetService(router.context.get('dynamodb_resource'))

    dataset = dataset_service.create(
        router.current_event.json_body,
        get_user_sub(router.current_event)
    )

    return dataset, HTTPStatus.CREATED


@router.get('/<datasetId>')
@tracer.capture_method
def retrieve_dataset(datasetId: str):
    dataset_service = DatasetService(router.context.get('dynamodb_resource'))

    return dataset_service.retrieve(datasetId)
