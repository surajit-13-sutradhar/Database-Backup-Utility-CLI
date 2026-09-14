import pytest
from dbbackup.utils.config import load_config


@pytest.fixture
def app_config():
    return load_config("dbbackup.yaml")