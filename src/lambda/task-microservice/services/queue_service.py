from aws_resources import LambdaSQS


class QueueService:
    def __init__(self, resource: LambdaSQS):
        self.resource = resource

    def send_message(self, body: str) -> dict:
        return self.resource.queue.send_message(
            MessageBody=body
        )
