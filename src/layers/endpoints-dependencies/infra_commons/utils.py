from boto3.dynamodb.types import TypeSerializer


def to_dynamodb_format(object):
    serializer = TypeSerializer()
    return {
        key: serializer.serialize(value)
        for key, value in object.items()
    }
