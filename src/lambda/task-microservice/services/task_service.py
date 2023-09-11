from datetime import datetime
from pydantic import ValidationError
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError,
    BadRequestError,
    UnauthorizedError
)

from infra_commons.models.s3_object import InputS3Content
from infra_commons.aws_resources import LambdaDynamoDB
from services.repositories.task_repository import TaskRepository
from models.task import Task, TaskStatusEnum

logger = Logger(child=True)


class TaskService:
    def __init__(self, resource: LambdaDynamoDB):
        self.repository = TaskRepository(resource)

    def list(self) -> list[Task]:
        return self.repository.list_tasks()

    def create(self, form: dict, user_sub: str, bucket_name: str) -> Task:
        form['UserSub'] = user_sub

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

    def retrieve_owned_task(self, task_id: str, user_sub: str) -> Task:
        task = self.retrieve(task_id)

        if str(task.UserSub) != user_sub:
            raise UnauthorizedError("You are not authorized to modify task '{}'".format(task_id))

        return task

    def update(self, task_id: str, body: dict, user_sub: str) -> Task:
        task = self.retrieve_owned_task(task_id, user_sub)

        if task.TaskStatus != TaskStatusEnum.DRAFT:
            raise BadRequestError("Task '{}' cannot be updated because is in status '{}'.".format(task_id, task.TaskStatus))

        try:
            updated_fields = task.update(body)
        except ValidationError as e:
            logger.error(e.errors())
            raise BadRequestError("Task '{}' could not be updated.".format(task_id))

        self.repository.partial_update(task, updated_fields)
        return task

    def update_attachment_input(self, task_id: str, body: dict, user_sub: str, bucket_name: str) -> InputS3Content:
        task = self.retrieve_owned_task(task_id, user_sub)

        if task.TaskStatus != TaskStatusEnum.DRAFT:
            raise BadRequestError("Cannot generate signed urls for task '{}' because is not in status 'draft'.".format(task_id))

        try:
            updated_fields = task.update_attachment_input(body, bucket_name)

        except AttributeError:
            raise BadRequestError("Field '{}' is not available to upload attachments in task '{}'.".format(body['FieldName'], task_id))

        except Exception as e:
            raise BadRequestError(e)

        self.repository.partial_update(task, updated_fields)
        return getattr(task.Inputs, body['FieldName'])

    def update_to_submit(self, task_id: str, user_sub: str) -> Task:
        task = self.retrieve_owned_task(task_id, user_sub)

        if task.TaskStatus != TaskStatusEnum.DRAFT:
            raise BadRequestError("Task '{}' cannot be submitted because is in status '{}'.".format(task_id, task.TaskStatus))

        task.TaskStatus = TaskStatusEnum.QUEUED
        task.ModifiedAt = datetime.utcnow()

        self.repository.partial_update(task, ['TaskStatus', 'ModifiedAt'])

        return task
