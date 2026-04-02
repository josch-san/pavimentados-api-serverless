"""Utility functions for data transformation."""
from datetime import datetime
from decimal import Decimal


def to_dynamodb_format(data: dict) -> dict:
    """Convert a Python dict to DynamoDB format."""
    if not data:
        return {}
    
    result = {}
    for key, value in data.items():
        result[key] = _to_dynamodb_value(value)
    return result


def _to_dynamodb_value(value):
    """Convert a Python value to DynamoDB format."""
    if value is None:
        return {'NULL': True}
    elif isinstance(value, bool):
        return {'BOOL': value}
    elif isinstance(value, (int, float)):
        return {'N': str(value)}
    elif isinstance(value, Decimal):
        return {'N': str(value)}
    elif isinstance(value, str):
        return {'S': value}
    elif isinstance(value, bytes):
        return {'B': value}
    elif isinstance(value, list):
        return {'L': [_to_dynamodb_value(item) for item in value]}
    elif isinstance(value, dict):
        return {'M': to_dynamodb_format(value)}
    elif isinstance(value, datetime):
        return {'S': value.isoformat()}
    else:
        return {'S': str(value)}


def from_dynamodb_format(data: dict) -> dict:
    """Convert DynamoDB format to Python dict."""
    if not data:
        return {}
    
    result = {}
    for key, value in data.items():
        result[key] = _from_dynamodb_value(value)
    return result


def _from_dynamodb_value(value):
    """Convert DynamoDB value to Python format."""
    if 'S' in value:
        return value['S']
    elif 'N' in value:
        num = value['N']
        if '.' in num:
            return float(num)
        return int(num)
    elif 'BOOL' in value:
        return value['BOOL']
    elif 'L' in value:
        return [_from_dynamodb_value(item) for item in value['L']]
    elif 'M' in value:
        return from_dynamodb_format(value['M'])
    elif 'NULL' in value:
        return None
    elif 'B' in value:
        return value['B']
    else:
        return value
