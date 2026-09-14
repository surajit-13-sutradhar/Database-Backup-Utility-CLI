import shutil
from pathlib import Path

from dbbackup.storage.base import BaseStorage


class LocalStorage(BaseStorage):
    def __init__(self, base_dir: str = "./backups"):
        self.base_dir = Path(base_dir)

    def save(self, local_temp_path: str, destination_name: str) -> str:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        dest = self.base_dir / destination_name

        src = Path(local_temp_path)
        if src.resolve() != dest.resolve():
            shutil.move(str(src), str(dest))

        return str(dest)