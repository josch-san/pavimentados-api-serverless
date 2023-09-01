from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter

# from infra_commons.services.storage_service import StorageService 

tracer = Tracer()
router = APIGatewayRouter()

@router.post('/')
@tracer.capture_method
def create_dataset():
    return {
        'sample': 'data'
    }
