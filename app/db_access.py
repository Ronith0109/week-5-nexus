import sqlite3
from pathlib import Path

from app.logging_config import get_logger, trace

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MERIDIAN_DB = DATA_DIR / "meridian.db"

SAFE_FUNCTIONS = {
    "lower", "upper", "length", "substr", "coalesce",
    "abs", "round", "min", "max", "count"
}

DENIED_ACTIONS = {
    sqlite3.SQLITE_ATTACH,
    sqlite3.SQLITE_DETACH,
    sqlite3.SQLITE_ALTER_TABLE,
    sqlite3.SQLITE_ANALYZE,
    sqlite3.SQLITE_CREATE_INDEX,
    sqlite3.SQLITE_CREATE_TABLE,
    sqlite3.SQLITE_CREATE_TEMP_INDEX,
    sqlite3.SQLITE_CREATE_TEMP_TABLE,
    sqlite3.SQLITE_CREATE_TEMP_TRIGGER,
    sqlite3.SQLITE_CREATE_TEMP_VIEW,
    sqlite3.SQLITE_CREATE_TRIGGER,
    sqlite3.SQLITE_CREATE_VIEW,
    sqlite3.SQLITE_DROP_INDEX,
    sqlite3.SQLITE_DROP_TABLE,
    sqlite3.SQLITE_DROP_TEMP_INDEX,
    sqlite3.SQLITE_DROP_TEMP_TABLE,
    sqlite3.SQLITE_DROP_TEMP_TRIGGER,
    sqlite3.SQLITE_DROP_TEMP_VIEW,
    sqlite3.SQLITE_DROP_TRIGGER,
    sqlite3.SQLITE_DROP_VIEW,
    sqlite3.SQLITE_REINDEX,
    sqlite3.SQLITE_PRAGMA,
}

DOMAIN_SCOPES = {
    "banking": {
        "db_path": MERIDIAN_DB,
        "allowed_tables": {"customers", "accounts", "transactions"},
        "writable": False,
    },
    "insurance": {
        "db_path": MERIDIAN_DB,
        "allowed_tables": {"customers", "policies", "claims"},
        "writable": False,
    },
    "wealth": {
        "db_path": MERIDIAN_DB,
        "allowed_tables": {"customers", "portfolios", "investment_products"},
        "writable": False,
    },
    "concierge_ops": {
        "db_path": MERIDIAN_DB,
        "allowed_tables": {"customers", "interaction_log", "escalation_flags", "audit_log"},
        "writable": True,
    },
}


def _redact_initialize_arguments(arguments):
    return {
        "db_path": arguments.get("db_path"),
        "schema_sql": "<schema omitted>",
        "seed_rows": "<seed data omitted>",
    }


@trace(logger)
def _authorizer_factory(allowed_tables, writable):
    allowed_tables = set(allowed_tables)

    def authorizer(action, arg1, arg2, db_name, source):
        if action in DENIED_ACTIONS:
            return sqlite3.SQLITE_DENY

        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK

        if action == sqlite3.SQLITE_READ:
            return sqlite3.SQLITE_OK if arg1 in allowed_tables else sqlite3.SQLITE_DENY

        if action == sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if (arg2 or "").lower() in SAFE_FUNCTIONS else sqlite3.SQLITE_DENY

        if action in (sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE):
            if writable and arg1 in allowed_tables:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        if action == sqlite3.SQLITE_TRANSACTION:
            return sqlite3.SQLITE_OK

        if hasattr(sqlite3, "SQLITE_SAVEPOINT") and action == sqlite3.SQLITE_SAVEPOINT:
            return sqlite3.SQLITE_OK

        return sqlite3.SQLITE_DENY

    return authorizer


@trace(logger)
def get_scoped_connection(allowed_tables, read_only=True, writable=False, db_path=None):
    if not allowed_tables:
        raise ValueError("allowed_tables cannot be empty")
    if writable and read_only:
        raise ValueError("read_only and writable cannot both be True")
    path = Path(db_path) if db_path else MERIDIAN_DB
    if not path.exists():
        raise FileNotFoundError(f"Database does not exist: {path}")

    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA query_only = ON" if read_only else "PRAGMA query_only = OFF")
    conn.set_authorizer(_authorizer_factory(allowed_tables, writable))
    return conn


@trace(logger)
def get_domain_scope(domain):
    if domain not in DOMAIN_SCOPES:
        raise ValueError(f"Unknown domain: {domain}")
    return DOMAIN_SCOPES[domain]


@trace(logger)
def get_domain_connection(domain):
    scope = get_domain_scope(domain)
    return get_scoped_connection(
        allowed_tables=scope["allowed_tables"],
        read_only=not scope["writable"],
        writable=scope["writable"],
        db_path=scope["db_path"],
    )


@trace(logger, redact=_redact_initialize_arguments)
def initialize_database(db_path, schema_sql, seed_rows):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(db_path) + suffix)
        if sidecar.exists():
            sidecar.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(schema_sql)

        for table, columns, rows in seed_rows:
            placeholders = ",".join("?" for _ in columns)
            conn.executemany(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                rows,
            )
        conn.commit()
    finally:
        conn.close()
