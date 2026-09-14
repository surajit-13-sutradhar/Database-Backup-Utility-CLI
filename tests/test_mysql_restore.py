from pathlib import Path

import mysql.connector

from dbbackup.connectors.factory import get_connector


def _get_rows(db_config):
    conn = mysql.connector.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.username,
        password=db_config.password,
        database=db_config.database,
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM test_table ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def _reset_table(db_config, rows):
    conn = mysql.connector.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.username,
        password=db_config.password,
        database=db_config.database,
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM test_table")
    cur.executemany("INSERT INTO test_table VALUES (%s, %s)", rows)
    conn.commit()
    conn.close()


def test_mysql_backup_and_restore(app_config, tmp_path):
    db_config = app_config.get_target("local_mysql")
    connector = get_connector(db_config)

    # 1. Ensure a known starting state
    known_rows = [(1, "Alice"), (2, "Bob")]
    _reset_table(db_config, known_rows)
    assert _get_rows(db_config) == known_rows

    # 2. Take a backup of this known state
    backup_path = tmp_path / "backup_test.sql"
    connector.backup(str(backup_path))

    # 3. "Damage" the live database
    conn = mysql.connector.connect(
        host=db_config.host, port=db_config.port,
        user=db_config.username, password=db_config.password,
        database=db_config.database,
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO test_table VALUES (99, 'Intruder')")
    conn.commit()
    conn.close()

    damaged_rows = _get_rows(db_config)
    assert (99, "Intruder") in damaged_rows

    # 4. Restore from the backup taken in step 2
    connector.restore(str(backup_path))

    # 5. Verify it matches the pre-damage state
    restored_rows = _get_rows(db_config)
    assert restored_rows == known_rows