# 统一封装 InsightFlow 工作流运行逻辑，供命令行和 API 入口复用。

from typing import Any

from utils.run_logger import create_run_id, log_event
from workflow import create_workflow


def run_analysis(
    data_sources: list[str],
    analysis_focus: str | None = None,
    knowledge_sources: list[str] | None = None,
    run_id: str | None = None
) -> dict[str, Any]:

    if run_id is None:
        run_id = create_run_id()

    log_event(
        run_id=run_id,
        node="workflow",
        event="run_started",
        status="started"
    )

    workflow = create_workflow()

    try:
        result = workflow.invoke(
            {
                "run_id": run_id,
                "data_sources": data_sources,
                "analysis_focus": analysis_focus,
                "knowledge_sources": knowledge_sources or [],
                "retrieved_knowledge": [],
                "retrieved_knowledge_details": [],
                "execution_results": [],
                "failed_tasks": [],
                "visualization_results": [],
                "artifacts": [],
            },
            config={
                "recursion_limit": 100
            }
        )

    except Exception as error:

        log_event(
            run_id=run_id,
            node="workflow",
            event="run_failed",
            status="failed",
            details={
                "error_type": type(error).__name__,
                "error": str(error)
            }
        )

        raise

    log_event(
        run_id=run_id,
        node="workflow",
        event="run_completed",
        status="success",
        details={
            "analysis_tasks": len(
                result.get(
                    "analysis_plan",
                    []
                )
            ),
            "failed_tasks": len(
                result.get(
                    "failed_tasks",
                    []
                )
            ),
            "visualizations": len(
                result.get(
                    "visualization_plan",
                    []
                )
            ),
            "artifacts": result.get(
                "artifacts",
                []
            )
        }
    )

    return result