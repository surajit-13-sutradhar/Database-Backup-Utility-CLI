import sqlite3
from pathlib import Path

from dbbackup.connectors.factory import get_connector
from dbbackup.utils.compression import decompress_file


def test_sqlite_backup_and_restore(app_config, tmp_path):
    db_config = app_config.get_target("local_sqlite")
    connector = get_connector(db_config)

    live_db_path = Path(db_config.file_path)

    # 1. Ensure a known starting row exists
    conn = sqlite3.connect(live_db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
    conn.execute("DELETE FROM test")
    conn.execute("INSERT INTO test VALUES (1)")
    conn.commit()
    conn.close()

    # 2. Take a backup of this known state
    backup_path = tmp_path / "backup_test.db"
    connector.backup(str(backup_path))

    # 3. "Damage" the live database
    conn = sqlite3.connect(live_db_path)
    conn.execute("INSERT INTO test VALUES (999)")
    conn.commit()
    conn.close()

    damaged_rows = sqlite3.connect(live_db_path).execute("SELECT * FROM test").fetchall()
    assert damaged_rows == [(1,), (999,)]

    # 4. Restore from the backup taken in step 2
    connector.restore(str(backup_path))

    # 5. Verify it matches the pre-damage state
    restored_rows = sqlite3.connect(live_db_path).execute("SELECT * FROM test").fetchall()
    assert restored_rows == [(1,)]