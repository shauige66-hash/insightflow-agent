# 大模型能否调用 Schema Tool，并根据工具结果生成最终回答

from langchain_core.messages import HumanMessage, ToolMessage

from core.llm import create_llm
from ingestion.loader import load_data_sources
from tools.schema_tool import create_schema_tool


tables = load_data_sources([
    "data/financials.csv",
    "data/sales.sqlite"
])

schema_tool = create_schema_tool(tables)

llm = create_llm()

llm_with_tools = llm.bind_tools([
    schema_tool
])

user_message = HumanMessage(
    content="请查看 financials 表有哪些字段以及字段类型。"
)

response = llm_with_tools.invoke([
    user_message
])

tool_call = response.tool_calls[0]

tool_result = schema_tool.invoke(
    tool_call["args"]
)

tool_message = ToolMessage(
    content=str(tool_result),
    tool_call_id=tool_call["id"]
)

final_response = llm_with_tools.invoke([
    user_message,
    response,
    tool_message
])

print(final_response.content)