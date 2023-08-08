import os
import logging

from inference_builder import InferenceBuilder

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

BASE_CODE_S3URI = os.environ['BASE_CODE_S3URI']

def lambda_handler(event, context):
    builder = InferenceBuilder(event['Id'], BASE_CODE_S3URI)

    payload = builder.run(
        event['Inputs'],
        user_sub=event['UserSub']
    )

    return payload
