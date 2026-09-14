from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from pathlib import Path
from typing import List

import yaml
from dotenv import load_dotenv
import os




def _resolve_env_placeholders(obj):
    """Recursively replace ${VAR_NAME} strings with values from environment variables."""
    if isinstance(obj, dict):
        return {k: _resolve_env_placeholders(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_env_placeholders(v) for v in obj]
    if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        env_var = obj[2:-1]
        return os.environ.get(env_var, "")
    return obj

class DBType(str, Enum):
    sqlite = "sqlite"
    mysql = "mysql"
    postgresql = "postgresql"
    mongodb = "mongodb"


class DBConnectionConfig(BaseModel):
    """Connection parameters for a single database target."""

    name: str = Field(..., description="A friendly name for this target, e.g. 'prod_mysql'.")
    db_type: DBType
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    # For SQLite, we just need a file path instead of host/port/etc.
    file_path: Optional[str] = None

    class Config:
        use_enum_values = True

class AppConfig(BaseModel):
    targets: List[DBConnectionConfig] = Field(default_factory=list)

    def get_target(self, name: str) -> DBConnectionConfig:
        for t in self.targets:
            if t.name == name:
                return t
        raise ValueError(f"No target named '{name}' found in config.")

def load_config(config_path: str = "dbbackup.yaml") -> AppConfig:
    """Load targets from a YAML file, resolving ${ENV_VAR} placeholders using .env / environment."""
    load_dotenv()  # loads .env into os.environ if present

    path = Path(config_path)
    if not path.exists():
        return AppConfig()  # empty config is valid; user may use pure CLI flags instead

    with open(path, "r") as f:
        raw = yaml.safe_load(f) or {}

    raw = _resolve_env_placeholders(raw)
    return AppConfig(**raw)