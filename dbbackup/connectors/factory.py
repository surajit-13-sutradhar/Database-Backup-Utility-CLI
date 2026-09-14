from dbbackup.utils.config import DBConnectionConfig, DBType
from dbbackup.connectors.base import BaseConnector, ConnectorError
from dbbackup.connectors.sqlite_connector import SQLiteConnector
from dbbackup.connectors.mysql_connector import MySQLConnector


def get_connector(config: DBConnectionConfig) -> BaseConnector:
    if config.db_type == DBType.sqlite:
        return SQLiteConnector(config)
    if config.db_type == DBType.mysql:
        return MySQLConnector(config)
    raise ConnectorError(f"Unsupported or not-yet-implemented db_type: {config.db_type}")