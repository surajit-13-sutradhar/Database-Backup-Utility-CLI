from abc import ABC, abstractmethod
from dbbackup.utils.config import DBConnectionConfig


class ConnectorError(Exception):
    """Raised when a connector fails to connect or perform an operation."""
    pass


class BaseConnector(ABC):
    """Abstract interface that every database connector must implement."""

    def __init__(self, config: DBConnectionConfig):
        self.config = config

    @abstractmethod
    def test_connection(self) -> bool:
        """Attempt to connect; return True if successful, raise ConnectorError otherwise."""
        raise NotImplementedError

    @abstractmethod
    def backup(self, output_path: str) -> str:
        """Perform a full backup, writing to output_path. Return the final file path."""
        raise NotImplementedError

    @abstractmethod
    def restore(self, backup_file_path: str) -> None:
        """Restore the database from an uncompressed backup file at backup_file_path."""
        raise NotImplementedError