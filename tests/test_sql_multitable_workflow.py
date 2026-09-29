# 测试 Planner、Router、Executor 和 SQL Tool 的完整 SQLite 多表分析链路。

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


from agents.executor import generate_execution_code
from agents.planner import create_analysis_plan
from agents.router import route_analysis_task
from context.context_builder import build_all_contexts
from ingestion.loader import load_data_sources
from tools.sql_tool import create_sql_tool


def main():

    tables = load_data_sources([
        "data/sales.sqlite"
    ])

    contexts = build_all_contexts(
        tables
    )

    analysis_focus = (
        "重点分析订单和客户之间的关系。"
        "至少设计一个必须同时使用订单表和客户表的多表分析任务。"
        "根据真实 schema 自己选择关联字段，"
        "不要编造不存在的字段。"
    )

    plan = create_analysis_plan(
        contexts=contexts,
        analysis_focus=analysis_focus
    )

    print("\n=== Analysis Plan ===")

    for task in plan:
        print(task)

    multi_table_tasks = [
        task
        for task in plan
        if len(task["target_tables"]) >= 2
    ]

    assert len(multi_table_tasks) > 0, (
        "Planner did not create a multi-table task."
    )

    sql_tool = create_sql_tool(
        tables
    )

    for task in plan:

        print(
            f"\n=== Testing {task['task_id']} ==="
        )

        for table_name in task["target_tables"]:

            assert table_name in tables, (
                f"Planner returned unknown resource: "
                f"{table_name}"
            )

        route = route_analysis_task(
            task=task,
            tables=tables
        )

        print("\nRoute:")
        print(route)

        assert route == "sql", (
            f"{task['task_id']} was not routed to SQL."
        )

        data_context = {
            table_name: contexts[table_name]
            for table_name in task["target_tables"]
        }

        code = generate_execution_code(
            task=task,
            data_context=data_context,
            route=route
        )

        print("\nGenerated SQL:")
        print(code)

        for resource_name in task["target_tables"]:

            assert resource_name not in code, (
                "Generated SQL used an InsightFlow "
                "resource name instead of database_table."
            )

        execution = sql_tool.invoke({
            "table_names": task["target_tables"],
            "query": code
        })

        print("\nExecution Result:")
        print(execution)

        assert execution["success"] is True, (
            f"{task['task_id']} failed: "
            f"{execution['error']}"
        )

        assert execution["error"] is None

        assert execution["result"] is not None

    print(
        "\nAll SQLite workflow tasks passed."
    )


if __name__ == "__main__":
    main()