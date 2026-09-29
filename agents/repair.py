# 根据执行错误和原始代码，让大模型生成修复后的 Python 或 SQL 代码。

import json
from typing import Any, Literal

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from core.llm import create_llm
from state import AnalysisTask
from utils.llm_retry import invoke_json_with_retry

REPAIR_PROMPT = """
你是一个数据分析代码修复 Agent。

分析任务：

{task}

相关数据上下文：

{data_context}

执行方式：

{route}

原始代码：

{code}

执行错误：

{error}

请根据错误信息修复代码。

要求：

1. 修复后的代码仍然必须完成原始分析任务。

2. 只能使用上下文中真实存在的表和字段。

3. 不要编造字段、数据、表关系或关联键。

4. 如果 route 是 python：

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

   - 如果原始任务需要多表分析，
     修复后仍然必须保留正确的多表逻辑。

   - 可以根据需要使用 merge、join、groupby、
     pivot_table、aggregation、filter、sort 等 Pandas 操作。

   - 只有在数据上下文明确支持表关系时，
     才允许进行 merge 或 join。

   - 不要为了消除错误而删除原任务要求的关键分析步骤。

   - 如果需要修改、排序或增加临时字段，
     优先对 DataFrame 使用 copy() 后再操作。

   - 最终结果必须保存到 result 变量。

   - 不要读取文件。
   - 不要使用网络。
   - 不要执行 import。

5. 如果 route 是 sql：

   - 只能生成 SELECT 或 WITH 开头的只读 SQL。

   - 只能使用数据上下文和分析任务中真实存在的表名与字段名。

   - target_tables 中列出的 SQLite 表，
     如果来自同一个 SQLite 数据库，
     可以直接在同一条 SQL 中访问。

   - 如果原始任务涉及多张 SQLite 表，
     修复后的 SQL 必须保留必要的多表分析逻辑。

   - 可以根据真实存在的关联字段使用 JOIN。
   - analysis task 中的 target_tables 是 InsightFlow 资源名。

   - 修复 SQL 时，SQLite 的 FROM 和 JOIN 必须使用
    data_context 中对应的 database_table 作为真实表名。

   - 不要把类似 sales.orders 这样的资源名直接当作 SQLite 表名使用。

   - 不要为了消除执行错误，
     就删除原任务要求的 JOIN 或多表分析步骤。

   - 只有在上下文明确支持表关系时，
     才允许进行 JOIN。

   - 不要编造不存在的表、字段、关联键或表关系。

   - 不要尝试跨不同 SQLite 数据库文件进行 JOIN。

   - 修复后的 SQL 必须能够直接在当前 SQLite 数据库连接中执行。


6. 只修复代码，不要解释错误原因。

只返回合法 JSON，不要输出其他文字。

返回格式：

{{
    "code": "修复后的 Python 代码或 SQL 查询"
}}
"""


def repair_execution_code(
    task: AnalysisTask,
    data_context: dict[str, Any],
    route: Literal["python", "sql"],
    code: str,
    error: str
) -> str:

    llm = create_llm()

    prompt = PromptTemplate.from_template(
        REPAIR_PROMPT
    )

    parser = JsonOutputParser()

    chain = prompt | llm | parser

    inputs = {
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
    "route": route,
    "code": code,
    "error": error
}

    result = invoke_json_with_retry(
        chain,
        inputs
    )

    return result["code"]