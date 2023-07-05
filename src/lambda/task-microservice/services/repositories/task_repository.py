from boto3.dynamodb.conditions import Attr
from pydantic import parse_obj_as

from models.task import Task
from aws_resources import LambdaDynamoDB


class TaskRepository:
    def __init__(self, resource: LambdaDynamoDB):
        self.resource = resource

    def list_tasks(self) -> list[Task]:
        response = self.resource.table.scan(
            FilterExpression=Attr('__typename').eq('TASK')
        )

        return parse_obj_as(list[Task], response['Items'])

    def create_task(self, form: dict, bucket_name: str) -> Task:
        inputs = form.pop('Inputs')
        task = Task.parse_obj(form)

        task.initialize_inputs(inputs, bucket_name)
        self.resource.table.put_item(Item=task.dynamodb_record)

        return task

    def get_task(self, task_id: str) -> Task:
        response = self.resource.table.get_item(
            Key=Task.build_dynamodb_key(task_id)
        )

        return Task.parse_obj(response['Item'])

    def partial_update(self, task: Task, fields: list[str]) -> Task:
        update_expression = []
        attribute_names = {}
        attribute_values = {}

        raw_task = task.raw_dict()
        for index, field_key in enumerate(fields):
            key_expression = f'#key{index:02}'
            value_expression = f':value{index:02}'

            if field_key.startswith('Inputs.'):
                attribute_names['#inputs'] = 'Inputs'

                nested_field_key = field_key.replace('Inputs.', '')
                attribute_names[key_expression] = nested_field_key
                attribute_values[value_expression] = raw_task['Inputs'][nested_field_key]

                key_expression = f'#inputs.{key_expression}'

            else:
                attribute_names[key_expression] = field_key
                attribute_values[value_expression] = raw_task[field_key]


            update_expression.append(f'{key_expression} = {value_expression}')

        self.resource.table.update_item(
            Key=task.dynamodb_key,
            UpdateExpression=f'SET {", ".join(update_expression)}',
            ExpressionAttributeNames=attribute_names,
            ExpressionAttributeValues=attribute_values
        )

        return task
