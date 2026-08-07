"""Run LiveSQLBench Query tasks through InfiniSynapse."""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import queue
import re
import shutil
import sys
import threading
import uuid
import zipfile
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

import requests

from livesql_agent_infini.api.client import ping_api, resolve_timeout
from livesql_agent_infini.api.database import select_databases_by_livesql_db_id
from livesql_agent_infini.api.tasks import (
    download_task_zip,
    get_ai_state,
    list_available_engines,
    new_task,
    wait_for_task,
)
from livesql_agent_infini.config import (
    ASSISTANT_JSONL,
    DATA_ROOT,
    INFINI_CREDENTIAL_PATH,
    OUTPUT_DIR,
    REFERENCES_DIR,
    SUBMISSION_DIR_OUTPUT,
    SUBMISSION_DIR_REASONING,
    SUBMISSION_DIR_SQL,
    TASK_MAX_WAIT,
)
from livesql_agent_infini.kb_reference import write_kb_reference

logger = logging.getLogger("livesql_agent_infini")

_CONTEXT_HUB_SAY_TO_DROP = frozenset({
    "context_hub_search",
    "context_hub_search_result",
})

_ANSWER_SHAPE_SECTION = """<answer_shape>
The output shape MUST literally match what the question asks for. Read the
question carefully and follow these mappings:

- "How many ...", "What is the count/number of ..." → return **a single scalar
  count** (one row, one column). Do NOT return the underlying detail rows.
- "Which / List / What are the ... (top N / all ...)" → return the requested
  detail rows, only the columns the question asks about.
- "What is the average / total / max / min ..." → return that single aggregate
  value, not the per-row breakdown.
- "For each X, ..." / "... by X" / "... per X" → return one row per X, grouped
  accordingly.

Other strict rules on shape:
- Do NOT add extra columns "for context" that the question did not ask for.
- Do NOT include intermediate detail rows alongside the aggregate when only the
  aggregate was requested.
- Column names should reflect what the question is asking. Use snake_case.
- If the question implies an ordering (e.g. "top N", "earliest", "largest"),
  apply the corresponding `ORDER BY` (and `LIMIT` where applicable).
</answer_shape>"""


def _configure_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    datetime_str = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(levelname)s %(module)s] %(message)s",
        handlers=[
            logging.FileHandler(
                os.path.join("logs", f"run-{datetime_str}.log"),
                encoding="utf-8",
            ),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_tasks(jsonl_path: Path) -> list[dict]:
    tasks: list[dict] = []
    with open(jsonl_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            if raw.get("category") != "Query":
                continue
            tasks.append(
                {
                    "instance_id": raw["instance_id"],
                    "instruction": raw["query"],
                    "db_id": raw["selected_database"],
                    "external_knowledge": raw.get("external_knowledge") or [],
                    "_raw": raw,
                }
            )
    return tasks


def _parse_range(spec: str, total: int) -> tuple[int, int]:
    parts = [part.strip() for part in spec.split(",")]
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"--range must look like 'start,end' (got {spec!r})")
    start, end = int(parts[0]), int(parts[1])
    if start < 1 or end < start:
        raise ValueError(f"invalid range: {spec!r}")
    end = min(end, total)
    return start, end


def _resolve_engine_ids(
    engines: list[dict],
    engine_spec: str | None,
) -> list[str]:
    available = [
        item for item in engines
        if isinstance(item, dict) and item.get("id")
    ]
    if not available:
        return []
    if not engine_spec:
        return [str(item["id"]) for item in available]

    by_name = {
        str(item.get("name") or ""): str(item["id"])
        for item in available
        if item.get("name")
    }
    engine_ids: list[str] = []
    missing: list[str] = []
    for name in [token.strip() for token in engine_spec.split(",") if token.strip()]:
        engine_id = by_name.get(name)
        if engine_id is None:
            missing.append(name)
            continue
        if engine_id not in engine_ids:
            engine_ids.append(engine_id)
    if missing:
        raise ValueError(f"engine name(s) not found: {missing}")
    return engine_ids


def _build_prompt(instance_id: str, instruction: str) -> str:
    intro = (
        "You are a Data Analysis Agent working on LiveSQLBench Base-Lite-SQLite. "
        "Solve the following business question end-to-end: first explore and analyze "
        "the data with **Infinity SQL**, then deliver the final answer as a "
        "**SQLite SQL** script."
    )
    objective = (
        "<objective>\n"
        "Produce one deliverable that **strictly** answers the user's question:\n"
        f"1. `{instance_id}.sql` — a single SQLite SQL script whose final `SELECT`, "
        "when executed against the scoped LiveSQLBench SQLite database, returns "
        "**exactly** the result that answers the question (same columns, same rows, "
        "same order when requested).\n"
        "</objective>"
    )
    rules_section = (
        "<rules>\n"
        "- You MUST use Infinity SQL (via `execute_infinity_sql`) to derive and "
        "validate the answer. Do NOT fabricate results.\n"
        "- Read the uploaded external-knowledge document in `upload_documents/` "
        "when the question uses domain-specific metrics or definitions.\n"
        "- You MUST produce the SQLite SQL only AFTER the Infinity-SQL analysis has "
        "confirmed the correct answer.\n"
        "- The SQLite script must contain exactly ONE final answer `SELECT` — the one "
        "that returns the answer.\n"
        "- Use plain SQLite-dialect SQL (no database/schema prefixes; use bare table "
        "names as they appear in the SQLite database).\n"
        "- Do NOT use machine-learning methods/functions in Infinity SQL.\n"
        f"- Never stop early: keep iterating until `{instance_id}.sql` exists and its "
        "final `SELECT` literally answers the question.\n"
        "</rules>"
    )
    return f"""
{intro}

{objective}

{_ANSWER_SHAPE_SECTION}

{rules_section}

<question>
{instruction}
</question>
"""


def _is_done(instance_id: str) -> bool:
    return (SUBMISSION_DIR_SQL / f"{instance_id}.sql").exists()


def _clear_submissions(instance_id: str) -> None:
    for path in (
        SUBMISSION_DIR_SQL / f"{instance_id}.sql",
        SUBMISSION_DIR_REASONING / f"{instance_id}.json",
        SUBMISSION_DIR_OUTPUT / f"{instance_id}.json",
    ):
        if path.exists():
            path.unlink()


def _filter_reasoning_messages(messages: list) -> list:
    return [
        message for message in messages
        if not (
            isinstance(message, dict)
            and message.get("say") in _CONTEXT_HUB_SAY_TO_DROP
        )
    ]


def _save_reasoning_trace(
    instance_id: str,
    task_id: str,
    *,
    credential_path: Path,
    timeout: float | None,
) -> None:
    try:
        state = get_ai_state(
            task_id,
            credential_path=credential_path,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        logger.warning("[trace] %s: get_ai_state failed: %s", instance_id, exc)
        return

    messages = state.get("infiniMessages") if isinstance(state, dict) else []
    if not isinstance(messages, list):
        messages = []
    messages = _filter_reasoning_messages(messages)

    SUBMISSION_DIR_REASONING.mkdir(parents=True, exist_ok=True)
    dest = SUBMISSION_DIR_REASONING / f"{instance_id}.json"
    with open(dest, "w", encoding="utf-8") as handle:
        json.dump(messages, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logger.info("[trace] %s: reasoning saved -> %s", instance_id, dest)


def _extract_zip(zip_path: str | os.PathLike, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)


def _find_first(root: Path, name: str) -> Path | None:
    for cur, _dirs, files in os.walk(root):
        if name in files:
            return Path(cur) / name
    return None


def _split_sql_statements(sql_string: str) -> list[str]:
    statements = [stmt.strip() for stmt in sql_string.split(";") if stmt.strip()]
    result: list[str] = []
    for stmt in statements:
        if not stmt.endswith(";"):
            stmt += ";"
        result.append(stmt)
    return result


def _extract_sql_from_file(sql_path: Path) -> list[str]:
    content = sql_path.read_text(encoding="utf-8")
    fenced = re.search(r"```(?:sqlite|sql)?\n(.*?)\n```", content, re.DOTALL | re.IGNORECASE)
    if fenced:
        content = fenced.group(1).strip()
    return _split_sql_statements(content)


def _write_submission_output(task: dict, pred_sqls: list[str]) -> Path:
    """Write one evaluation record to submission_output/{instance_id}.json."""
    raw = dict(task["_raw"])
    raw["pred_sqls"] = pred_sqls
    instance_id = raw["instance_id"]

    SUBMISSION_DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
    dest = SUBMISSION_DIR_OUTPUT / f"{instance_id}.json"
    with open(dest, "w", encoding="utf-8") as handle:
        json.dump(raw, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return dest


def run_one(
    task: dict,
    *,
    rerun: bool = False,
    engine_id: str | None = None,
    credential_path: Path,
    data_root: Path,
    timeout: float | None = None,
) -> bool:
    instance_id = task["instance_id"]
    instruction = task["instruction"]
    db_id = task["db_id"]
    external_knowledge = task.get("external_knowledge") or []

    if _is_done(instance_id):
        if rerun:
            _clear_submissions(instance_id)
        else:
            logger.info("[skip ] %s already has submission", instance_id)
            return True

    logger.info(
        "=== Running %s (db_id=%s, engine=%s) ===",
        instance_id,
        db_id,
        engine_id or "(default)",
    )

    prompt = _build_prompt(instance_id, instruction)
    task_id = str(uuid.uuid4())

    try:
        matching = select_databases_by_livesql_db_id(
            db_id,
            credential_path=credential_path,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        logger.error("[fail ] %s: failed to resolve sqlite source: %s", instance_id, exc)
        return False

    if not matching:
        logger.error(
            "[fail ] %s: no InfiniSynapse sqlite source for db_id=%s; "
            "run setup_livesql.py --db %s first",
            instance_id,
            db_id,
            db_id,
        )
        return False

    database_ids = [item["id"] for item in matching if isinstance(item, dict) and item.get("id")]
    source_names = [item.get("name") for item in matching if isinstance(item, dict)]
    logger.info("[src  ] %s: using sqlite source %s (ids=%s)", instance_id, source_names, database_ids)

    reference_paths: list[str] = []
    if external_knowledge:
        try:
            kb_path = write_kb_reference(
                instance_id,
                db_id,
                external_knowledge,
                REFERENCES_DIR,
                data_root=data_root,
            )
            reference_paths.append(str(kb_path))
            logger.info("[kb   ] %s: uploaded reference %s", instance_id, kb_path)
        except Exception as exc:
            logger.warning("[warn ] %s: failed to build KB reference: %s", instance_id, exc)

    try:
        new_task(
            text=prompt,
            task_id=task_id,
            reference_paths=reference_paths or None,
            database_ids=database_ids,
            engine_id=engine_id,
            credential_path=credential_path,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        logger.error("[fail ] %s: newTask failed: %s", instance_id, exc)
        return False

    logger.info("[task ] %s -> taskId=%s (submitted)", instance_id, task_id)

    try:
        wait_for_task(
            task_id,
            poll_interval=3.0,
            max_wait=TASK_MAX_WAIT,
            terminal_on_any_ask=True,
            credential_path=credential_path,
            timeout=timeout,
        )
    except TimeoutError as exc:
        logger.error("[fail ] %s: task wait timed out: %s", instance_id, exc)
        return False
    except requests.RequestException as exc:
        logger.error("[fail ] %s: wait_for_task error: %s", instance_id, exc)
        return False

    _save_reasoning_trace(
        instance_id,
        task_id,
        credential_path=credential_path,
        timeout=timeout,
    )

    task_output_dir = OUTPUT_DIR / instance_id
    task_output_dir.mkdir(parents=True, exist_ok=True)
    try:
        zip_path = download_task_zip(
            task_id,
            task_output_dir,
            credential_path=credential_path,
            timeout=timeout,
        )
        logger.info("[zip  ] %s: downloaded %s", instance_id, zip_path)
    except requests.RequestException as exc:
        logger.error("[fail ] %s: download zip failed: %s", instance_id, exc)
        return False

    extract_dir = task_output_dir / "workspace"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    _extract_zip(zip_path, extract_dir)

    src = _find_first(extract_dir, f"{instance_id}.sql")
    if src is None:
        logger.warning("[miss ] %s: required deliverable %s.sql not found", instance_id, instance_id)
        return False

    SUBMISSION_DIR_SQL.mkdir(parents=True, exist_ok=True)
    dst = SUBMISSION_DIR_SQL / f"{instance_id}.sql"
    shutil.copyfile(src, dst)
    logger.info("[sql  ] %s: saved -> %s", instance_id, dst)

    pred_sqls = _extract_sql_from_file(dst)
    if pred_sqls:
        out_path = _write_submission_output(task, pred_sqls)
        logger.info("[output] %s: saved -> %s", instance_id, out_path)
    return True


def _run_task_batch(
    tasks: list[dict],
    *,
    rerun: bool,
    engine_ids: list[str],
    credential_path: Path,
    data_root: Path,
    timeout: float | None,
) -> tuple[int, int]:
    total = len(tasks)
    if not engine_ids:
        return 0, total

    def _worker(engine_id: str) -> None:
        while True:
            try:
                item = work_q.get_nowait()
            except queue.Empty:
                return
            if item is None:
                return
            idx, task = item
            instance_id = task["instance_id"]
            logger.info(
                "---- [%d/%d] %s start (engine=%s) ----",
                idx,
                total,
                instance_id,
                engine_id,
            )
            try:
                ok = run_one(
                    task,
                    rerun=rerun,
                    engine_id=engine_id,
                    credential_path=credential_path,
                    data_root=data_root,
                    timeout=timeout,
                )
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                logger.exception("[fail ] %s: unhandled exception: %s", instance_id, exc)
                ok = False
            results.append((idx, instance_id, ok))
            logger.info(
                "---- [%d/%d] %s done (ok=%s, engine=%s) ----",
                idx,
                total,
                instance_id,
                ok,
                engine_id,
            )

    work_q: queue.Queue[tuple[int, dict] | None] = queue.Queue()
    results: list[tuple[int, str, bool]] = []
    for idx, task in enumerate(tasks, 1):
        work_q.put((idx, task))
    for _ in engine_ids:
        work_q.put(None)

    with ThreadPoolExecutor(max_workers=len(engine_ids)) as executor:
        futures = [executor.submit(_worker, engine_id) for engine_id in engine_ids]
        for future in futures:
            future.result()

    n_ok = sum(int(ok) for _, _, ok in results)
    return n_ok, total


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run LiveSQLBench Query tasks via InfiniSynapse",
    )
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=ASSISTANT_JSONL,
        help=f"task jsonl path (default: {ASSISTANT_JSONL})",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DATA_ROOT,
        help=f"LiveSQLBench dataset root (default: {DATA_ROOT})",
    )
    parser.add_argument(
        "--credential",
        type=Path,
        default=INFINI_CREDENTIAL_PATH,
        help=f"InfiniSynapse credential JSON (default: {INFINI_CREDENTIAL_PATH})",
    )
    parser.add_argument(
        "--instance_id",
        type=str,
        default=None,
        help="only run given instance_id(s), comma-separated (e.g. alien_1)",
    )
    parser.add_argument(
        "--range",
        dest="index_range",
        type=str,
        default=None,
        help="1-indexed inclusive range over filtered Query tasks, e.g. 1,10",
    )
    parser.add_argument(
        "--db_id",
        type=str,
        default=None,
        help="only run tasks for given selected_database values, comma-separated",
    )
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        help="only use given InfiniSQL engine name(s), comma-separated",
    )
    parser.add_argument(
        "--rerun",
        "--force",
        dest="rerun",
        action="store_true",
        help="force rerun even if submission already exists",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="API timeout in seconds (default: 60, or INFINI_API_TIMEOUT env)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    args = _parse_args(argv)

    if not args.credential.is_file():
        logger.error("credential file not found: %s", args.credential)
        return 1
    if not args.jsonl.is_file():
        logger.error("jsonl file not found: %s", args.jsonl)
        return 1

    try:
        api_url = ping_api(credential_path=args.credential, timeout=args.timeout)
        logger.info("InfiniSynapse API reachable at %s", api_url)
    except requests.RequestException as exc:
        logger.error("Cannot reach InfiniSynapse API: %s", exc)
        return 1

    tasks = load_tasks(args.jsonl)
    if not tasks:
        logger.error("no Query tasks found in %s", args.jsonl)
        return 1

    if args.instance_id:
        requested = [token.strip() for token in args.instance_id.split(",") if token.strip()]
        by_id = {task["instance_id"]: task for task in tasks}
        missing = [item for item in requested if item not in by_id]
        if missing:
            logger.error("instance_id(s) not found: %s", missing)
            return 1
        tasks = [by_id[item] for item in requested]
    elif args.index_range:
        start, end = _parse_range(args.index_range, len(tasks))
        tasks = tasks[start - 1:end]

    if args.db_id:
        db_set = set(token.strip() for token in args.db_id.split(",") if token.strip())
        tasks = [task for task in tasks if task["db_id"] in db_set]

    if not tasks:
        logger.error("no tasks left after filtering")
        return 1

    try:
        engines = list_available_engines(
            credential_path=args.credential,
            timeout=args.timeout,
        )
        engine_ids = _resolve_engine_ids(engines, args.engine)
    except (requests.RequestException, ValueError) as exc:
        logger.error("Failed to resolve engines: %s", exc)
        return 1

    if not engine_ids:
        logger.error("No available InfiniSQL engines found")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUBMISSION_DIR_SQL.mkdir(parents=True, exist_ok=True)
    SUBMISSION_DIR_REASONING.mkdir(parents=True, exist_ok=True)
    SUBMISSION_DIR_OUTPUT.mkdir(parents=True, exist_ok=True)

    logger.info("Running %d Query task(s)", len(tasks))
    if len(engine_ids) == 1:
        n_ok = 0
        for task in tasks:
            if run_one(
                task,
                rerun=args.rerun,
                engine_id=engine_ids[0],
                credential_path=args.credential,
                data_root=args.data_root,
                timeout=args.timeout,
            ):
                n_ok += 1
    else:
        n_ok, _ = _run_task_batch(
            tasks,
            rerun=args.rerun,
            engine_ids=engine_ids,
            credential_path=args.credential,
            data_root=args.data_root,
            timeout=args.timeout,
        )

    logger.info("All tasks finished: %d/%d succeeded", n_ok, len(tasks))
    logger.info("Submission output dir: %s", SUBMISSION_DIR_OUTPUT)
    return 0 if n_ok == len(tasks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
