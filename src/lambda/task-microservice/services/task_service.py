from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError
)

from services.repositories.task_repository import TaskRepository
from models.task import Task

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
