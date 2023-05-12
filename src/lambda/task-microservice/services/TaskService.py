from services.repositories.TaskRepository import TaskRepository

from models.Task import Task


class TaskService:
    def __init__(self, table_name: str):
        self.repository = TaskRepository(table_name)

    def list_tasks(self) -> list[Task]:
        return self.repository.list_tasks()
