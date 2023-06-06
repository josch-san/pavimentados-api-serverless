import pytest


@pytest.fixture(autouse=True)
def clean_aws_credentials(monkeypatch):
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-east-1')
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'AKIAIOSFODNN7EXAMPLE')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'superSecret')
