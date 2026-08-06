"""Register LiveSQLBench Base-Lite-SQLite databases in InfiniSynapse."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import requests

from livesql_agent_infini.api.client import ping_api
from livesql_agent_infini.api.database import (
    add_sqlite_database,
    check_database_exists,
    create_upload_directory,
    delete_database,
    get_database_by_name,
    normalize_database_name,
    select_databases_by_livesql_db_id,
    upload_file_to_directory,
)
from livesql_agent_infini.config import (
    DATA_ROOT,
    DATABASE_NAME_PREFIX,
    FAILURE_LOG_PATH,
    INFINI_CREDENTIAL_PATH,
)

logger = logging.getLogger("livesql_agent_infini")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(levelname)s %(module)s] %(message)s",
    )


def _log_failure(message: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    logger.error(message)
    with open(FAILURE_LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def discover_databases(data_root: Path) -> list[str]:
    """Return sorted LiveSQLBench database names under ``data_root``."""
    if not data_root.is_dir():
        raise FileNotFoundError(f"dataset root not found: {data_root}")

    db_names: list[str] = []
    for child in sorted(data_root.iterdir()):
        if not child.is_dir():
            continue
        sqlite_path = child / f"{child.name}_template.sqlite"
        if sqlite_path.is_file():
            db_names.append(child.name)

    if not db_names:
        raise RuntimeError(
            f"no LiveSQLBench sqlite databases found under {data_root}"
        )
    return db_names


def build_database_name(db_id: str) -> str:
    return normalize_database_name(f"{DATABASE_NAME_PREFIX}{db_id}")


def sqlite_template_path(data_root: Path, db_id: str) -> Path:
    return data_root / db_id / f"{db_id}_template.sqlite"


def register_one_database(
    db_id: str,
    *,
    data_root: Path,
    credential_path: Path,
    force: bool = False,
    dry_run: bool = False,
    timeout: float | None = None,
) -> bool:
    sqlite_file = sqlite_template_path(data_root, db_id)
    database_name = build_database_name(db_id)
    description = f"LiveSQLBench Base-Lite-SQLite database: {db_id}"

    logger.info("=== Processing db_id=%s (source name=%s) ===", db_id, database_name)

    if not sqlite_file.is_file():
        _log_failure(f"sqlite file missing for db_id={db_id!r}: {sqlite_file}")
        return False

    if dry_run:
        logger.info("[dry-run] would register %s from %s", database_name, sqlite_file)
        return True

    try:
        if check_database_exists(
            database_name,
            credential_path=credential_path,
            timeout=timeout,
        ):
            if force:
                logger.info("[delete] %s already exists, deleting", database_name)
                delete_database(
                    database_name,
                    credential_path=credential_path,
                    timeout=timeout,
                )
            else:
                logger.info("[skip ] %s already exists (use --force to recreate)", database_name)
                return True

        tmp_dir = f"sqlite_tmp_{database_name}"
        logger.info("[mkdir ] %s", tmp_dir)
        create_upload_directory(
            tmp_dir,
            credential_path=credential_path,
            timeout=timeout,
        )

        logger.info("[upload] %s -> %s", sqlite_file, tmp_dir)
        absolute_path = upload_file_to_directory(
            tmp_dir,
            sqlite_file,
            credential_path=credential_path,
        )

        logger.info("[create] %s (sqlite_path=%s)", database_name, absolute_path)
        add_sqlite_database(
            database_name=database_name,
            sqlite_path=absolute_path,
            description=description,
            credential_path=credential_path,
            timeout=timeout,
        )
        logger.info("[ok    ] %s", database_name)
        return True
    except Exception as exc:
        _log_failure(
            f"Failed to set up sqlite database {database_name!r} "
            f"(db_id={db_id}, file={sqlite_file}): {exc}"
        )
        return False


def verify_registrations(
    db_ids: list[str],
    *,
    credential_path: Path,
    timeout: float | None = None,
) -> tuple[int, int, int]:
    ok = 0
    failed = 0
    for db_id in db_ids:
        try:
            matches = select_databases_by_livesql_db_id(
                db_id,
                credential_path=credential_path,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            failed += 1
            logger.error("[verify] %s -> API ERROR: %s", db_id, exc)
            continue

        if matches:
            logger.info("[verify] %s -> %s", db_id, matches[0].get("name"))
            ok += 1
        else:
            logger.error("[verify] %s -> NOT FOUND", db_id)
    return ok, len(db_ids), failed


def _ensure_api_reachable(credential_path: Path, timeout: float | None) -> bool:
    try:
        api_url = ping_api(credential_path=credential_path, timeout=timeout)
    except requests.RequestException as exc:
        logger.error(
            "Cannot reach InfiniSynapse API (%s): %s\n"
            "Tips: check VPN/network, confirm infini_credential.json api_url, "
            "or increase timeout via --timeout / INFINI_API_TIMEOUT.",
            credential_path,
            exc,
        )
        return False

    logger.info("InfiniSynapse API reachable at %s", api_url)
    return True


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Register LiveSQLBench Base-Lite-SQLite databases in InfiniSynapse."
        ),
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DATA_ROOT,
        help=f"path to livesqlbench-base-lite-sqlite (default: {DATA_ROOT})",
    )
    parser.add_argument(
        "--credential",
        type=Path,
        default=INFINI_CREDENTIAL_PATH,
        help=f"InfiniSynapse credential JSON (default: {INFINI_CREDENTIAL_PATH})",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="only register the given database name(s), comma-separated (e.g. alien,credit)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="delete and recreate databases that already exist",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list databases that would be registered without calling InfiniSynapse",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="only verify existing registrations and exit",
    )
    parser.add_argument(
        "--list-remote",
        action="store_true",
        help="list registered LiveSQLBench sqlite data sources in InfiniSynapse",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="API request timeout in seconds (default: 60, or INFINI_API_TIMEOUT env)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    args = _parse_args(argv)

    if args.list_remote:
        if not args.credential.is_file():
            logger.error("credential file not found: %s", args.credential)
            return 1
        if not _ensure_api_reachable(args.credential, args.timeout):
            return 1

        db_ids = discover_databases(args.data_root)
        if args.db:
            db_ids = [token.strip() for token in args.db.split(",") if token.strip()]

        livesql_items = []
        api_errors = 0
        for db_id in db_ids:
            try:
                record = get_database_by_name(
                    build_database_name(db_id),
                    credential_path=args.credential,
                    timeout=args.timeout,
                )
            except requests.RequestException as exc:
                api_errors += 1
                logger.error("[list  ] %s -> API ERROR: %s", db_id, exc)
                continue
            if record:
                livesql_items.append(record)

        logger.info(
            "Found %d registered source(s) with prefix %r",
            len(livesql_items),
            DATABASE_NAME_PREFIX,
        )
        for item in livesql_items:
            logger.info(
                "  - %s (id=%s, enabled=%s, type=%s)",
                item.get("name"),
                item.get("id"),
                item.get("enabled"),
                item.get("type"),
            )
        if api_errors:
            logger.error("%d lookup(s) failed due to API/network errors", api_errors)
            return 1
        return 0

    db_ids = discover_databases(args.data_root)
    if args.db:
        requested = [token.strip() for token in args.db.split(",") if token.strip()]
        missing = sorted(set(requested) - set(db_ids))
        if missing:
            logger.error("unknown database name(s): %s", missing)
            return 1
        db_ids = requested

    logger.info(
        "Discovered %d LiveSQLBench database(s) under %s",
        len(db_ids),
        args.data_root,
    )

    if args.verify:
        if not args.credential.is_file():
            logger.error("credential file not found: %s", args.credential)
            return 1
        if not _ensure_api_reachable(args.credential, args.timeout):
            return 1
        ok, total, failed = verify_registrations(
            db_ids,
            credential_path=args.credential,
            timeout=args.timeout,
        )
        logger.info("Verification complete: %d/%d registered", ok, total)
        if failed:
            logger.error("%d lookup(s) failed due to API/network errors", failed)
            return 1
        return 0 if ok == total else 1

    if args.dry_run:
        for db_id in db_ids:
            register_one_database(
                db_id,
                data_root=args.data_root,
                credential_path=args.credential,
                force=args.force,
                dry_run=True,
            )
        logger.info("Dry run complete for %d database(s)", len(db_ids))
        return 0

    if not args.credential.is_file():
        logger.error(
            "credential file not found: %s\n"
            "Copy your InfiniSynapse credential to this path, for example:\n"
            "  cp /path/to/spider_agent_infini/infini_credential.json %s",
            args.credential,
            args.credential,
        )
        return 1
    if not _ensure_api_reachable(args.credential, args.timeout):
        return 1

    ok_count = 0
    for db_id in db_ids:
        if register_one_database(
            db_id,
            data_root=args.data_root,
            credential_path=args.credential,
            force=args.force,
            timeout=args.timeout,
        ):
            ok_count += 1

    logger.info("Setup finished: %d/%d succeeded", ok_count, len(db_ids))
    if ok_count != len(db_ids):
        logger.error("Some databases failed; see %s", FAILURE_LOG_PATH)
        return 1

    verify_ok, verify_total, verify_failed = verify_registrations(
        db_ids,
        credential_path=args.credential,
        timeout=args.timeout,
    )
    logger.info("Post-setup verification: %d/%d registered", verify_ok, verify_total)
    if verify_failed:
        logger.error("%d verification lookup(s) failed due to API/network errors", verify_failed)
        return 1
    return 0 if verify_ok == verify_total else 1


if __name__ == "__main__":
    sys.exit(main())
