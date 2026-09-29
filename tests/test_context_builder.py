# 测试 Adaptive Context Manager 能否为所有数据表构建上下文。

from ingestion.loader import load_data_sources
from context.context_builder import build_all_contexts


tables = load_data_sources([
    "data/financials.csv",
    "data/sales.sqlite"
])

contexts = build_all_contexts(tables)

for table_name, context in contexts.items():
    print(f"\nTABLE: {table_name}")
    print(context)