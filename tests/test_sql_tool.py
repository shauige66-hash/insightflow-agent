# 测试 SQL Tool 能否对 SQLite 数据库执行只读查询。

from ingestion.loader import load_data_sources
from tools.sql_tool import create_sql_tool


tables = load_data_sources([
    "data/sales.sqlite"
])

sql_tool = create_sql_tool(tables)

result = sql_tool.invoke({
    "table_name": "sales.orders",
    "query": """
        SELECT AVG(amount) AS average_amount
        FROM orders
    """
})

print(result)