# 测试 SQL Executor 能否根据 SQLite 上下文生成正确的多表 JOIN 查询。

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )

from agents.executor import generate_execution_code
from context.context_builder import build_all_contexts
from ingestion.loader import load_data_sources
from tools.sql_tool import create_sql_tool


def main():

    tables = load_data_sources([
        "data/sales.sqlite"
    ])

    all_contexts = build_all_contexts(
        tables
    )

    task = {
        "task_id": "task_1",
        "description": (
            "关联订单表和客户表，"
            "按客户名称统计订单数量和订单总金额，"
            "并按订单总金额降序排列。"
        ),
        "target_tables": [
            "sales.orders",
            "sales.customers"
        ],
        "expected_output": (
            "每个客户的名称、订单数量和订单总金额。"
        )
    }

    data_context = {
        table_name: all_contexts[table_name]
        for table_name in task["target_tables"]
    }

    code = generate_execution_code(
        task=task,
        data_context=data_context,
        route="sql"
    )

    print("\n=== Generated SQL ===")
    print(code)

    assert "sales.orders" not in code
    assert "sales.customers" not in code

    sql_tool = create_sql_tool(
        tables
    )

    execution = sql_tool.invoke({
        "table_names": task["target_tables"],
        "query": code
    })

    print("\n=== Execution Result ===")
    print(execution)

    assert execution["success"] is True
    assert execution["error"] is None
    assert len(execution["result"]) > 0

    print(
        "\nSQLite multi-table Agent execution test passed."
    )


if __name__ == "__main__":
    main()