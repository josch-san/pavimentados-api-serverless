from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError,
    BadRequestError,
    UnauthorizedError
)

from models.task import Task
from models.s3_object import InputS3Content
from models.base_task import TaskStatusEnum
from services.repositories.task_repository import TaskRepository

logger = Logger(child=True)


class TaskService:
    def __init__(self, table_name: str):
        self.repository = TaskRepository(table_name)

    def list(self) -> list[Task]:
        return self.repository.list_tasks()

    def create(self, form: dict, user_id: str, bucket_name: str) -> Task:
        form['UserId'] = user_id

        try:
            task = self.repository.create_task(form, bucket_name)
        except Exception as e:
            logger.error(e.errors())

        return task

    def retrieve(self, task_id: str) -> Task:
        try:
            task = self.repository.get_task(task_id)
        except KeyError:
            raise NotFoundError

        return task

    def update_attachment_input(self, task_id: str, body: dict, user_id: str, bucket_name: str) -> InputS3Content:
        task = self.retrieve(task_id)

        if str(task.UserId) != user_id:
            raise UnauthorizedError("You are not authorized to modify task '{}'".format(task_id))

        if task.TaskStatus != TaskStatusEnum.DRAFT:
            raise BadRequestError("Cannot generate signed urls for task '{}' because is not in status 'draft'.".format(task_id))

        try:
            task.update_attachment_input(body, bucket_name)

        except AttributeError:
            raise BadRequestError("Field '{}' is not available to upload attachments in task '{}'.".format(body['FieldName'], task_id))

        except Exception as e:
            raise BadRequestError(e)

        self.repository.update_partial_inputs(task, [body['FieldName']])
        return getattr(task.Inputs, body['FieldName']).Content
