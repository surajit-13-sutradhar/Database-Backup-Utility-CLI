import subprocess
from pathlib import Path

import mysql.connector
from mysql.connector import Error as MySQLError

from dbbackup.connectors.base import BaseConnector, ConnectorError


class MySQLConnector(BaseConnector):

    def test_connection(self) -> bool:
        try:
            conn = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                connection_timeout=5,
            )
            conn.close()
            return True
        except MySQLError as e:
            raise ConnectorError(f"Failed to connect to MySQL database: {e}")

    def backup(self, output_path: str) -> str:
        self.test_connection()  # fail fast with a clear error before shelling out

        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "mysqldump",
            f"--host={self.config.host}",
            f"--port={self.config.port}",
            f"--user={self.config.username}",
            f"--password={self.config.password}",
            "--single-transaction",   # safe, consistent snapshot without locking tables
            "--routines",             # include stored procedures/functions
            "--triggers",
            self.config.database,
        ]

        try:
            with open(dest, "wb") as f_out:
                result = subprocess.run(
                    cmd, stdout=f_out, stderr=subprocess.PIPE, check=True
                )
        except FileNotFoundError:
            raise ConnectorError(
                "mysqldump not found. Ensure MySQL's bin directory is in your PATH."
            )
        except subprocess.CalledProcessError as e:
            dest.unlink(missing_ok=True)  # don't leave a partial/corrupt dump file
            raise ConnectorError(f"mysqldump failed: {e.stderr.decode(errors='replace')}")

        return str(dest)

    def restore(self, backup_file_path: str) -> None:
        source = Path(backup_file_path)
        if not source.exists():
            raise ConnectorError(f"Backup file not found: {source}")

        self.test_connection()  # fail fast if target DB is unreachable

        cmd = [
            "mysql",
            f"--host={self.config.host}",
            f"--port={self.config.port}",
            f"--user={self.config.username}",
            f"--password={self.config.password}",
            self.config.database,
        ]

        try:
            with open(source, "rb") as f_in:
                result = subprocess.run(
                    cmd, stdin=f_in, stderr=subprocess.PIPE, check=True
                )
        except FileNotFoundError:
            raise ConnectorError(
                "mysql client not found. Ensure MySQL's bin directory is in your PATH."
            )
        except subprocess.CalledProcessError as e:
            raise ConnectorError(f"mysql restore failed: {e.stderr.decode(errors='replace')}")