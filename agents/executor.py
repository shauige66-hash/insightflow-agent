# 根据分析任务和执行路线，让大模型生成具体的 Python 或 SQL 分析代码。

import json
from typing import Any, Literal
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from core.llm import create_llm
from state import AnalysisTask


EXECUTION_PROMPT = """
你是一个数据分析执行 Agent。

分析任务：

{task}

相关数据上下文：

{data_context}

执行方式：

{route}

请为这个分析任务生成可执行代码。

要求：

1. 如果 route 是 python：

   - 使用 Pandas。
   - Pandas 已经通过 pd 变量提供，不要执行 import。
   - 所有目标数据表都已经通过 dfs 字典提供。
   - dfs 的 key 就是真实表名，例如：
     orders = dfs["orders"]
     customers = dfs["customers"]

   - 如果分析任务只有一张目标表，
     系统还会额外提供 df 变量作为该表的快捷引用。

   - 单表任务可以直接使用 df。
   - 多表任务必须通过 dfs["表名"] 访问对应 DataFrame。

   - 多表分析可以根据需要使用：
     merge、join、groupby、pivot_table、
     aggregation、filter、sort 等 Pandas 操作。

   - 只能使用数据上下文中真实存在的表名和字段名。
   - 只有在上下文能够支持表关系时才允许进行 merge 或 join。
   - 不要虚构不存在的关联字段或表关系。

   - 如果需要修改、排序、增加临时字段，
     优先对 DataFrame 使用 copy() 后再操作。

   - 最终分析结果必须保存到 result 变量。

   - 不要读取文件。
   - 不要使用网络。
   - 不要执行 import。
   - 不要修改原始数据。

2. 如果 route 是 sql：

   - 只生成只读 SQL。

   - 只能使用 SELECT 或 WITH。

   - analysis task 中的 target_tables 使用的是 InsightFlow 资源名，
     例如：
     sales.orders
     sales.customers

   - 生成 SQL 时，不要直接把 InsightFlow 资源名写进 FROM 或 JOIN。

   - 对于 SQLite 表，必须使用 data_context 中对应的
     database_table 作为真正的 SQL 表名。

   - 例如，如果：
     target_tables 中是 sales.orders
     而对应 data_context 中：
     "database_table": "orders"

     那么 SQL 中应使用：

     FROM orders

     而不是：

     FROM sales.orders

   - target_tables 中列出的 SQLite 表，
     如果来自同一个 SQLite 数据库，
     可以直接在同一条 SQL 中访问。

   - 如果分析任务涉及多张 SQLite 表，
     可以根据真实存在的关联字段使用 JOIN。

   - 只能使用 data_context 中真实存在的字段名。

   - 只有在上下文能够支持表关系时，
     才允许进行 JOIN。

   - 不要编造不存在的表、字段、关联键或表关系。

   - 不要尝试跨不同 SQLite 数据库文件进行 JOIN。

   - 最终 SQL 必须能够直接在当前 SQLite 数据库连接中执行。

返回格式：

{{
    "code": "生成的 Python 代码或 SQL 查询"
}}
"""


def generate_execution_code(
    task: AnalysisTask,
    data_context: dict[str, Any],
    route: Literal["python", "sql"]
) -> str:

    llm = create_llm()

    prompt = PromptTemplate.from_template(
        EXECUTION_PROMPT
    )

    parser = JsonOutputParser()

    chain = prompt | llm | parser

    result = chain.invoke({
        "task": json.dumps(
            task,
            ensure_ascii=False,
            indent=2
        ),
        "data_context": json.dumps(
            data_context,
            ensure_ascii=False,
            indent=2,
            default=str
        ),
        "route": route
    })

    return result["code"]