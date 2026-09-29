# 测试同一个 SQLite 数据库中的多表 JOIN 能否通过 SQL Tool 正常执行。

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )

from ingestion.loader import load_data_sources
from tools.sql_tool import create_sql_tool


def main():

    tables = load_data_sources([
        "data/sales.sqlite"
    ])

    sql_tool = create_sql_tool(
        tables
    )

    execution = sql_tool.invoke({
        "table_names": [
        "sales.orders",
        "sales.customers"
    ],
        "query": """
            SELECT
                c.customer_id,
                c.name,
                COUNT(o.order_id) AS order_count,
                COALESCE(SUM(o.amount), 0) AS total_amount
            FROM customers AS c
            LEFT JOIN orders AS o
                ON o.customer_id = c.customer_id
            GROUP BY
                c.customer_id,
                c.name
            ORDER BY
                total_amount DESC
        """
    })

    print(execution)

    assert execution["success"] is True
    assert execution["error"] is None

    rows = execution["result"]

    assert len(rows) > 0

    assert all(
        {
            "customer_id",
            "name",
            "order_count",
            "total_amount"
        }.issubset(row.keys())
        for row in rows
    )

    print(
        "SQLite multi-table JOIN test passed."
    )


if __name__ == "__main__":
    main()