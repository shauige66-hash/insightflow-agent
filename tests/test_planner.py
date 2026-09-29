# 测试 Planner 生成分析任务后，Router 能否为每个任务选择执行工具。

from ingestion.loader import load_data_sources
from context.context_builder import build_all_contexts
from agents.planner import create_analysis_plan
from agents.router import route_analysis_task


tables = load_data_sources([
    "data/financials.csv",
    "data/sales.sqlite"
])

contexts = build_all_contexts(tables)

plan = create_analysis_plan(
    contexts=contexts,
    analysis_focus=None
)

for task in plan:
    route = route_analysis_task(
        task,
        tables
    )

    print("\nTASK:", task["task_id"])
    print("DESCRIPTION:", task["description"])
    print("TABLES:", task["target_tables"])
    print("ROUTE:", route)
    print("EXPECTED:", task["expected_output"])