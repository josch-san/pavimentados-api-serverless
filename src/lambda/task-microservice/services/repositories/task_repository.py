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

    def create_task(self, form: dict, user_id:str) -> Task:
        task = Task.parse_obj({**form, 'UserId': user_id})

        self.table.put_item(Item=task.dynamodb_record)
