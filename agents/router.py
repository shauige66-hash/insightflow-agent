# 根据分析任务涉及的数据源，选择合适的执行工具。
from typing import Literal
from ingestion.models import TableResource
from state import AnalysisTask


def route_analysis_task(task: AnalysisTask,tables: dict[str, TableResource]) -> Literal["python", "sql"]:

    target_tables = task["target_tables"]

    resources = [
        tables[table_name]
        for table_name in target_tables
    ]

    if all(
        resource.dataframe is not None
        for resource in resources
    ):
        return "python"

    if all(
        resource.source_type == "sqlite"
        for resource in resources
    ):
        return "sql"

    raise ValueError(
        f"Cannot route mixed data sources for task: {task['task_id']}"
    )