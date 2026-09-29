# 测试 Python Tool 能否对 DataFrame 数据执行 Pandas 分析代码。
from ingestion.loader import load_data_sources
from tools.python_tool import create_python_tool


tables = load_data_sources([
    "data/financials.csv"
])

python_tool = create_python_tool(tables)

result = python_tool.invoke({
    "table_name": "financials",
    "code": 'result = df["Revenue"].mean()'
})

print(result)