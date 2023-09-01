from http import HTTPStatus
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from infra_commons.services.storage_service import StorageService
from services.task_service import TaskService
from services.queue_service import QueueService

tracer = Tracer()
router = APIGatewayRouter()


def get_user_sub(event: APIGatewayProxyEvent):
    return event.request_context.authorizer.claims['sub']


@router.get('/')
@tracer.capture_method
def list_tasks():
    task_service = TaskService(router.context.get('dynamodb_resource'))

    tasks = task_service.list()
    return {
        'items': tasks
    }


@router.post('/')
@tracer.capture_method
def create_task():
    task_service = TaskService(router.context.get('dynamodb_resource'))

    task = task_service.create(
        router.current_event.json_body,
        get_user_sub(router.current_event),
        router.context.get('s3_resource').bucket_name
    )

    return task, HTTPStatus.CREATED


@router.get('/<taskId>')
@tracer.capture_method
def retrieve_task(taskId: str):
    task_service = TaskService(router.context.get('dynamodb_resource'))

    return task_service.retrieve(taskId)


@router.put('/<taskId>')
@tracer.capture_method
def update_task(taskId: str):
    task_service = TaskService(router.context.get('dynamodb_resource'))

    return task_service.update(
        taskId,
        router.current_event.json_body,
        get_user_sub(router.current_event)
    )


@router.post('/<taskId>/generateAttachmentUploadUrl')
@tracer.capture_method
def generate_attachment_upload_url(taskId: str):
    task_service = TaskService(router.context.get('dynamodb_resource'))
    storage_service = StorageService(router.context.get('s3_resource'))

    input_s3_content = task_service.update_attachment_input(
        taskId,
        router.current_event.json_body,
        get_user_sub(router.current_event),
        router.context.get('s3_resource').bucket_name
    )

    signed_content = storage_service.generate_presign_upload_url(input_s3_content)
    return signed_content, HTTPStatus.OK


@router.post('/<taskId>/submit')
@tracer.capture_method
def submit(taskId: str):
    task_service = TaskService(router.context.get('dynamodb_resource'))
    queue_service = QueueService(router.context.get('sqs_resource'))

    task = task_service.update_to_submit(
        taskId,
        get_user_sub(router.current_event)
    )

    queue_service.send_message(
        task.build_event_payload()
    )
    return task, HTTPStatus.ACCEPTED
