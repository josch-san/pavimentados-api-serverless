from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter

from services.task_service import TaskService

tracer = Tracer()
router = APIGatewayRouter()


@router.get('/')
@tracer.capture_method
def list_tasks():
    task_service = TaskService(router.context.get('table_name'))

    # print(router.current_event.request_context.authorizer.claims['sub'])
    tasks = task_service.list_tasks()
    return tasks
