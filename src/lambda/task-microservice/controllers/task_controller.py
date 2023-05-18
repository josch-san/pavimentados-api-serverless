from http import HTTPStatus
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter

from services.task_service import TaskService
from services.queue_service import QueueService

tracer = Tracer()
router = APIGatewayRouter()


@router.get('/')
@tracer.capture_method
def list_tasks():
    task_service = TaskService(router.context.get('table_name'))

    tasks = task_service.list_tasks()
    return {
        'items': tasks
    }


@router.post('/')
@tracer.capture_method
def create_task():
    task_service = TaskService(router.context.get('table_name'))
    queue_service = QueueService(router.context.get('queue_url'))

    task = task_service.create_task(
        router.current_event.json_body,
        router.current_event.request_context.authorizer.claims['sub']
    )

    queue_service.send_message(task.build_sqs_message())
    return task, HTTPStatus.ACCEPTED
