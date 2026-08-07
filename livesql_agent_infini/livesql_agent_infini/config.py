from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MINI_DEV_ROOT = PROJECT_ROOT.parent

DATA_ROOT = MINI_DEV_ROOT / "livesqlbench-base-lite-sqlite"
ASSISTANT_JSONL = DATA_ROOT / "assistant_sqlite.jsonl"

INFINI_CREDENTIAL_PATH = PROJECT_ROOT / "infini_credential.json"
FAILURE_LOG_PATH = PROJECT_ROOT / "setup_failures.log"

# InfiniSynapse data source name prefix to avoid colliding with Spider2 registrations.
DATABASE_NAME_PREFIX = "livesql_"

# Remote InfiniSynapse hosts often need a longer timeout than localhost.
DEFAULT_API_TIMEOUT = 60.0
DEFAULT_API_RETRIES = 3
TASK_MAX_WAIT = 1800.0

OUTPUT_DIR = PROJECT_ROOT / "output"
REFERENCES_DIR = PROJECT_ROOT / "references"
SUBMISSION_DIR_SQL = PROJECT_ROOT / "submission_sql"
SUBMISSION_DIR_REASONING = PROJECT_ROOT / "submission_reasoning"
SUBMISSION_DIR_OUTPUT = PROJECT_ROOT / "submission_output"
