import typer
import time
import tempfile
from dbbackup.utils.config import load_config
from dbbackup.connectors.factory import get_connector
from dbbackup.connectors.base import ConnectorError
from datetime import datetime
from dbbackup.storage.local_storage import LocalStorage
from dbbackup.utils.compression import compress_file, decompress_file
from dbbackup.utils.logger import get_logger
from pathlib import Path

logger = get_logger()

app = typer.Typer(
    name="dbbackup",
    help="A CLI utility for backing up and restoring databases (MySQL, PostgreSQL, MongoDB, SQLite, and more).",
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def version():
    """Show the tool version."""
    typer.echo("dbbackup v0.1.0")


@app.command()
def hello():
    """Placeholder command (will be replaced by real backup commands soon)."""
    typer.echo("dbbackup CLI is working.")

@app.command()
def show_config(config_path: str = "dbbackup.yaml"):
    """Load and display the current config (for testing)."""
    cfg = load_config(config_path)
    if not cfg.targets:
        typer.echo("No targets found. Did you create dbbackup.yaml?")
        return
    for t in cfg.targets:
        typer.echo(f"- {t.name} ({t.db_type}) host={t.host} db={t.database}")

@app.command()
def test_connection(target: str, config_path: str = "dbbackup.yaml"):
    """Test the connection to a named target from the config file."""
    cfg = load_config(config_path)
    try:
        db_config = cfg.get_target(target)
        connector = get_connector(db_config)
        connector.test_connection()
        typer.echo(f" Connection to '{target}' succeeded.")
    except ConnectorError as e:
        typer.echo(f" Connection failed: {e}")
    except ValueError as e:
        typer.echo(f" {e}")

@app.command()
def backup(target: str, config_path: str = "dbbackup.yaml"):
    """Perform a full backup of the named target and store it locally."""
    cfg = load_config(config_path)
    try:
        db_config = cfg.get_target(target)
        connector = get_connector(db_config)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{target}_{timestamp}.db"
        temp_path = f"./backups/_tmp_{temp_filename}"

        typer.echo(f"Starting backup of '{target}'...")
        connector.backup(temp_path)

        storage = LocalStorage(base_dir="./backups")
        final_path = storage.save(temp_path, temp_filename)

        typer.echo(f" Backup complete: {final_path}")
    except ConnectorError as e:
        typer.echo(f" Backup failed: {e}")
    except ValueError as e:
        typer.echo(f" {e}")

@app.command()
def backup(target: str, config_path: str = "dbbackup.yaml", compress: bool = True):
    """Perform a full backup of the named target and store it locally."""
    cfg = load_config(config_path)
    try:
        db_config = cfg.get_target(target)
        extension = "db" if db_config.db_type == "sqlite" else "sql"
        connector = get_connector(db_config)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{target}_{timestamp}.{extension}"
        temp_path = f"./backups/_tmp_{temp_filename}"

        typer.echo(f"Starting backup of '{target}'...")
        connector.backup(temp_path)

        final_temp_path = temp_path
        final_filename = temp_filename

        if compress:
            typer.echo("Compressing backup...")
            final_temp_path = compress_file(temp_path)
            final_filename = temp_filename + ".gz"

        storage = LocalStorage(base_dir="./backups")
        final_path = storage.save(final_temp_path, final_filename)

        typer.echo(f" Backup complete: {final_path}")
    except ConnectorError as e:
        typer.echo(f" Backup failed: {e}")
    except ValueError as e:
        typer.echo(f" {e}")

@app.command()
def backup(target: str, config_path: str = "dbbackup.yaml", compress: bool = True):
    """Perform a full backup of the named target and store it locally."""
    cfg = load_config(config_path)
    start_time = time.time()
    start_dt = datetime.now()

    try:
        db_config = cfg.get_target(target)
        connector = get_connector(db_config)

        extension = "db" if db_config.db_type == "sqlite" else "sql"

        timestamp = start_dt.strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{target}_{timestamp}.{extension}"
        temp_path = f"./backups/_tmp_{temp_filename}"

        logger.info(f"Backup started | target={target}")
        typer.echo(f"Starting backup of '{target}'...")

        connector.backup(temp_path)

        final_temp_path = temp_path
        final_filename = temp_filename

        if compress:
            typer.echo("Compressing backup...")
            final_temp_path = compress_file(temp_path)
            final_filename = temp_filename + ".gz"

        storage = LocalStorage(base_dir="./backups")
        final_path = storage.save(final_temp_path, final_filename)

        duration = round(time.time() - start_time, 2)
        logger.info(
            f"Backup succeeded | target={target} | file={final_path} | duration={duration}s"
        )
        typer.echo(f" Backup complete: {final_path}")

    except ConnectorError as e:
        duration = round(time.time() - start_time, 2)
        logger.error(f"Backup failed | target={target} | duration={duration}s | error={e}")
        typer.echo(f" Backup failed: {e}")
    except ValueError as e:
        logger.error(f"Backup failed | target={target} | error={e}")
        typer.echo(f" {e}")

@app.command()
def restore(target: str, backup_file: str, config_path: str = "dbbackup.yaml"):
    """Restore a target database from a backup file (.gz or raw)."""
    cfg = load_config(config_path)
    try:
        db_config = cfg.get_target(target)
        connector = get_connector(db_config)

        actual_backup_path = backup_file
        temp_decompressed = None

        if backup_file.endswith(".gz"):
            typer.echo("Decompressing backup file...")
            temp_decompressed = tempfile.mktemp()
            actual_backup_path = decompress_file(backup_file, temp_decompressed)

        typer.confirm(
            f"This will overwrite the '{target}' database. Continue?", abort=True
        )

        logger.info(f"Restore started | target={target} | file={backup_file}")
        typer.echo(f"Restoring '{target}' from {backup_file}...")

        connector.restore(actual_backup_path)

        logger.info(f"Restore succeeded | target={target} | file={backup_file}")
        typer.echo(f"Restore complete.")

        if temp_decompressed:
            Path(temp_decompressed).unlink(missing_ok=True)

    except ConnectorError as e:
        logger.error(f"Restore failed | target={target} | error={e}")
        typer.echo(f"Restore failed: {e}")
    except ValueError as e:
        typer.echo(f"{e}")

if __name__ == "__main__":
    app()