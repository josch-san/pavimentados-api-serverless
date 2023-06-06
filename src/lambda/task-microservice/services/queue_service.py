import boto3

sqs_client = boto3.client('sqs')


class QueueService:
    def __init__(self, queue_url: str):
        self.queue_url = queue_url

    def send_message(self, body: str) -> dict:
        return sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=body
        )
