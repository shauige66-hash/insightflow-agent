# 测试 Router 能否根据任务涉及的数据源选择 Python 或 SQL 工具。

from ingestion.loader import load_data_sources
from agents.router import route_analysis_task


tables = load_data_sources([
    "data/financials.csv",
    "data/sales.sqlite"
])


python_task = {
    "task_id": "task_1",
    "description": "分析 Revenue 的年度变化趋势",
    "target_tables": ["financials"],
    "expected_output": "Revenue 的年度趋势"
}


sql_task = {
    "task_id": "task_2",
    "description": "分析不同客户的订单总金额",
    "target_tables": [
        "sales.orders",
        "sales.customers"
    ],
    "expected_output": "每个客户的订单总金额"
}


python_route = route_analysis_task(
    python_task,
    tables
)

sql_route = route_analysis_task(
    sql_task,
    tables
)


print("TASK 1 ROUTE:", python_route)
print("TASK 2 ROUTE:", sql_route)