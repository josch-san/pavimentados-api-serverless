from pydantic import ValidationError
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
            raise BadRequestError('Task could not be created.')

        return task

    def retrieve(self, task_id: str) -> Task:
        try:
            task = self.repository.get_task(task_id)
        except KeyError:
            raise NotFoundError

        return task

    def retrieve_owned_task(self, task_id: str, user_id: str) -> Task:
        task = self.retrieve(task_id)

        if str(task.UserId) != user_id:
            raise UnauthorizedError("You are not authorized to modify task '{}'".format(task_id))

        return task

    def update(self, task_id: str, body: dict, user_id: str) -> Task:
        task = self.retrieve_owned_task(task_id, user_id)

        if task.TaskStatus != TaskStatusEnum.DRAFT:
            raise BadRequestError("Task '{}' cannot be updated because is in status '{}'.".format(task_id, task.TaskStatus))

        try:
            updated_task = task.copy(update=body)
            # TODO: pending implementation.
        except ValidationError as e:
            logger.error(e.errors())
            raise BadRequestError("Task '{}' could not be updated.".format(task_id))

        self.repository.update_task(updated_task)
        return updated_task

    def update_attachment_input(self, task_id: str, body: dict, user_id: str, bucket_name: str) -> InputS3Content:
        task = self.retrieve_owned_task(task_id, user_id)

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

    def update_to_submit(self, task_id: str, user_id: str) -> Task:
        task = self.retrieve_owned_task(task_id, user_id)

        if task.TaskStatus != TaskStatusEnum.DRAFT:
            raise BadRequestError("Task '{}' cannot be submitted because is in status '{}'.".format(task_id, task.TaskStatus))

        return task
