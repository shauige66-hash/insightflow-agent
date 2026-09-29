# 根据数据上下文和用户关注点，让大模型生成结构化的分析计划。
import json
from typing import Any
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from core.llm import create_llm
from state import AnalysisTask


PLANNER_PROMPT = """
你是一个数据分析规划 Agent。

下面是当前可用的数据上下文：

{data_context}

用户的分析关注点：

{analysis_focus}

请根据这些数据设计 3 到 5 个有价值的分析任务。

要求：
1. 只能使用上下文中真实存在的表和字段。

2. target_tables 中必须填写 data_context 最外层的真实资源名，
   不要使用 SQLite 的 database_table 代替资源名。

3. 例如，如果 data_context 的资源名是 sales.orders，
   即使其中 database_table 是 orders，
   target_tables 也必须填写 sales.orders。

4. 不要编造字段、表名或数据事实。

5. 可以设计单表分析，也可以在有合理关联字段时设计多表分析。

6. 只有在上下文中的字段能够支持表关系时，
   才设计多表关联任务。

7. 这里只决定“分析什么”，不要决定使用 Python 还是 SQL。

8. 如果用户没有指定分析关注点，请自主发现值得分析的问题。

9. 每个任务必须包含
   task_id、description、target_tables、expected_output。
   
只返回合法 JSON，不要输出其他文字。

返回格式：

{{
    "tasks": [
        {{
            "task_id": "task_1",
            "description": "分析内容",
            "target_tables": ["table_name"],
            "expected_output": "预期得到的分析结果"
        }}
    ]
}}
"""


def create_analysis_plan( contexts: dict[str, dict[str, Any]],analysis_focus: str | None = None) -> list[AnalysisTask]:

    llm = create_llm()

    prompt = PromptTemplate.from_template(
        PLANNER_PROMPT
    )

    parser = JsonOutputParser()

    chain = prompt | llm | parser

    result = chain.invoke({
        "data_context": json.dumps(
            contexts,
            ensure_ascii=False,
            indent=2,
            default=str
        ),
        "analysis_focus": analysis_focus or "未指定"
    })

    return result["tasks"]