from http import HTTPStatus
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler.router import APIGatewayRouter

from services.task_service import TaskService
from services.queue_service import QueueService
from services.storage_service import StorageService

tracer = Tracer()
router = APIGatewayRouter()


@router.get('/')
@tracer.capture_method
def list_tasks():
    task_service = TaskService(router.context.get('table_name'))

    tasks = task_service.list()
    return {
        'items': tasks
    }


@router.post('/')
@tracer.capture_method
def create_task():
    task_service = TaskService(router.context.get('table_name'))
    queue_service = QueueService(router.context.get('queue_url'))

    task = task_service.create(
        router.current_event.json_body,
        router.current_event.request_context.authorizer.claims['sub'],
        router.context.get('attachments_bucket_name')
    )

    queue_service.send_message(task.build_sqs_message())
    return task, HTTPStatus.ACCEPTED


@router.get('/<taskId>')
@tracer.capture_method
def retrieve_task(taskId: str):
    task_service = TaskService(router.context.get('table_name'))

    return task_service.retrieve(taskId)

@router.post('/<taskId>/generateAttachmentUploadUrl')
@tracer.capture_method
def generate_attachment_upload_url(taskId: str):
    task_service = TaskService(router.context.get('table_name'))
    storage_service = StorageService()

    input_s3_content = task_service.update_attachment_input(
        taskId,
        router.current_event.json_body,
        router.current_event.request_context.authorizer.claims['sub'],
        router.context.get('attachments_bucket_name')
    )

    signed_content = storage_service.generate_presign_upload_url(input_s3_content)
    return signed_content, HTTPStatus.ACCEPTED
