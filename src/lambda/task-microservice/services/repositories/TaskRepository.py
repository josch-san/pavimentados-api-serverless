import boto3


class TaskRepository:
    def __init__(self, table_name: str):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(table_name)

    def list_tasks(self):
        tasks = [
            {
                'id': 1,
                'name': 'tarea n1',
                'status': 'draft'
            },
            {
                'id': 2,
                'name': 'tarea n2',
                'status': 'queued'
            }
        ]

        return tasks
