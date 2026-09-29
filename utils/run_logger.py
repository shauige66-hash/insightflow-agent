# 提供 InsightFlow 工作流的本地结构化运行日志能力。

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


LOG_DIR = Path("outputs") / "logs"


def create_run_id() -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    suffix = uuid4().hex[:8]

    return f"run_{timestamp}_{suffix}"


def log_event(
    run_id: str,
    node: str,
    event: str,
    status: str,
    details: dict[str, Any] | None = None,
    duration_ms: float | None = None
) -> None:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    log_path = LOG_DIR / f"{run_id}.jsonl"

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "run_id": run_id,
        "node": node,
        "event": event,
        "status": status,
        "details": details or {}
    }

    if duration_ms is not None:
        record["duration_ms"] = round(
            duration_ms,
            2
        )

    with log_path.open(
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
                default=str
            )
            + "\n"
        )