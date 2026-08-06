"""Build external-knowledge reference documents for LiveSQLBench tasks."""

from __future__ import annotations

import json
from pathlib import Path

from livesql_agent_infini.config import DATA_ROOT


def load_kb_entries(db_id: str, data_root: Path | None = None) -> dict[int, dict]:
    root = data_root or DATA_ROOT
    kb_path = root / db_id / f"{db_id}_kb.jsonl"
    if not kb_path.is_file():
        raise FileNotFoundError(f"KB file not found: {kb_path}")

    by_id: dict[int, dict] = {}
    with open(kb_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            by_id[int(entry["id"])] = entry
    return by_id


def _collect_kb_ids(required_ids: list[int], kb_by_id: dict[int, dict]) -> list[int]:
    ordered: list[int] = []
    seen: set[int] = set()

    def visit(kb_id: int) -> None:
        if kb_id in seen or kb_id not in kb_by_id:
            return
        seen.add(kb_id)
        entry = kb_by_id[kb_id]
        children = entry.get("children_knowledge")
        if isinstance(children, list):
            for child_id in children:
                if isinstance(child_id, int):
                    visit(child_id)
        ordered.append(kb_id)

    for kb_id in required_ids:
        visit(int(kb_id))
    return ordered


def render_kb_markdown(
    instance_id: str,
    db_id: str,
    external_knowledge: list[int],
    data_root: Path | None = None,
) -> str:
    kb_by_id = load_kb_entries(db_id, data_root=data_root)
    kb_ids = _collect_kb_ids(external_knowledge, kb_by_id)

    lines = [
        f"# External Knowledge for {instance_id}",
        "",
        "Use these domain definitions when writing the final SQLite query.",
        "",
    ]
    for kb_id in kb_ids:
        entry = kb_by_id[kb_id]
        lines.extend(
            [
                f"## [{kb_id}] {entry.get('knowledge', '')}",
                "",
                f"Description: {entry.get('description', '')}",
                "",
                f"Definition: {entry.get('definition', '')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_kb_reference(
    instance_id: str,
    db_id: str,
    external_knowledge: list[int],
    dest_dir: Path,
    data_root: Path | None = None,
) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{instance_id}_kb.md"
    dest_path.write_text(
        render_kb_markdown(
            instance_id,
            db_id,
            external_knowledge,
            data_root=data_root,
        ),
        encoding="utf-8",
    )
    return dest_path
