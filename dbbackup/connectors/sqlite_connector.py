import shutil
import sqlite3
from pathlib import Path

from dbbackup.connectors.base import BaseConnector, ConnectorError


class SQLiteConnector(BaseConnector):

    def _get_file_path(self) -> Path:
        if not self.config.file_path:
            raise ConnectorError("SQLite config is missing 'file_path'.")
        return Path(self.config.file_path)

    def test_connection(self) -> bool:
        path = self._get_file_path()
        if not path.exists():
            raise ConnectorError(f"SQLite database file not found: {path}")
        try:
            conn = sqlite3.connect(str(path))
            conn.execute("SELECT 1;")
            conn.close()
            return True
        except sqlite3.Error as e:
            raise ConnectorError(f"Failed to connect to SQLite database: {e}")

    def backup(self, output_path: str) -> str:
        source_path = self._get_file_path()
        self.test_connection()  # fail fast with a clear error before copying

        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Use SQLite's own backup API rather than a raw file copy —
        # this is safe even if the DB is being written to concurrently.
        source_conn = sqlite3.connect(str(source_path))
        dest_conn = sqlite3.connect(str(dest))
        with dest_conn:
            source_conn.backup(dest_conn)
        source_conn.close()
        dest_conn.close()

        return str(dest)

    def restore(self, backup_file_path: str) -> None:
        target_path = self._get_file_path()
        source = Path(backup_file_path)

        if not source.exists():
            raise ConnectorError(f"Backup file not found: {source}")

        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Use SQLite's backup API in reverse: copy FROM the backup file INTO the live target.
        source_conn = sqlite3.connect(str(source))
        dest_conn = sqlite3.connect(str(target_path))
        with dest_conn:
            source_conn.backup(dest_conn)
        source_conn.close()
        dest_conn.close()