import boto3
from boto3.dynamodb.conditions import Attr
from pydantic import parse_obj_as

from models.task import Task


class TaskRepository:
    def __init__(self, table_name: str):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(table_name)

    def list_tasks(self) -> list[Task]:
        response = self.table.scan(
            FilterExpression=Attr('__typename').eq('TASK')
        )

        return parse_obj_as(list[Task], response['Items'])

    def create_task(self, form: dict, bucket_name: str) -> Task:
        inputs = form.pop('Inputs')
        task = Task.parse_obj(form)

        task.initialize_inputs(inputs, bucket_name)
        self.table.put_item(Item=task.dynamodb_record)

        return task

    def get_task(self, task_id: str) -> Task:
        response = self.table.get_item(
            Key=Task.build_dynamodb_key(task_id)
        )

        return Task.parse_obj(response['Item'])
