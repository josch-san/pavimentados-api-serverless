import os

import requests
from requests import Response
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

import task_controller

tracer = Tracer()
logger = Logger()

TABLE_NAME = os.environ.get('TABLE_NAME', 'pavimentados-test')
app = APIGatewayRestResolver(strip_prefixes=['/dev'])
app.include_router(task_controller.router, prefix='/tasks')


@app.post('/todo')
@tracer.capture_method
def create_todo():
    data: dict = app.current_event.json_body
    todo: Response = requests.post('https://jsonplaceholder.typicode.com/todos', data=data)

    # Returns the created todo object, with a HTTP 201 Created status
    return {'todo': todo.json()}, 201


@app.get('/todos')
@tracer.capture_method
def get_todos():
    todos: Response = requests.get('https://jsonplaceholder.typicode.com/todos')
    todos.raise_for_status()

    return {'todos': todos.json()[:10]}


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    app.append_context(table_name=TABLE_NAME)

    return app.resolve(event, context)
