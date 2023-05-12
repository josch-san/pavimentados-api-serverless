import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

import task_controller
from serializers import custom_serializer

tracer = Tracer()
logger = Logger()

TABLE_NAME = os.environ['TABLE_NAME']
STAGE_PREFIX = '/' + os.environ['API_STAGE']

app = APIGatewayRestResolver(strip_prefixes=[STAGE_PREFIX], serializer=custom_serializer)
app.include_router(task_controller.router, prefix='/tasks')


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    app.append_context(table_name=TABLE_NAME)

    return app.resolve(event, context)
