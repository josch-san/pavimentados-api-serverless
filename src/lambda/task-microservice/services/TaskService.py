from services.repositories.TaskRepository import TaskRepository


class TaskService:
    def __init__(self, table_name: str):
        self.repository = TaskRepository(table_name)

    def list_tasks(self) -> list:
        tasks = self.repository.list_tasks()

        return tasks
