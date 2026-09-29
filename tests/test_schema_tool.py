# 测试 Schema Tool 能否根据表名查询对应的数据表结构。

from ingestion.loader import load_data_sources
from tools.schema_tool import create_schema_tool


tables = load_data_sources([
    "data/financials.csv",
    "data/sales.sqlite"
])

schema_tool = create_schema_tool(tables)

result = schema_tool.invoke({
    "table_name": "financials"
})

print(result)