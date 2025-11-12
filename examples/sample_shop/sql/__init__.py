"""SQL database management with adapter pattern."""

import os
from pathlib import Path

from .sqldb import SqlDb
from .table import Table
from .adapters import DbAdapter, SqliteAdapter, PostgresAdapter

# Allow override via environment variable for testing
DB_PATH = Path(os.environ.get("SHOP_DB_PATH", Path(__file__).parent.parent / "shop.db"))

__all__ = [
    "SqlDb",
    "Table",
    "DB_PATH",
    "DbAdapter",
    "SqliteAdapter",
    "PostgresAdapter",
]
