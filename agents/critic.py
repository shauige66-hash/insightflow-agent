# 检查分析执行结果是否真正完成了原始分析任务。

import json
from typing import Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from core.llm import create_llm
from state import AnalysisTask, ExecutionResult
from utils.llm_retry import invoke_json_with_retry



CRITIC_PROMPT = """
你是一个数据分析结果审查 Agent。

原始分析任务：

{task}

相关数据上下文：

{data_context}

执行结果：

{execution_result}

请判断这次执行结果是否真正完成了原始分析任务。

重点检查：

1. 执行的代码是否与原始分析任务一致。
2. 是否使用了正确的表和字段。
3. 返回的结果是否能够支持 expected_output。
4. 不要因为代码成功运行就自动判定分析正确。
5. 只能根据提供的数据上下文和执行结果进行判断。
6. 如果分析不充分、答非所问或使用错误字段，应判定为不通过。

只返回合法 JSON，不要输出其他文字。

返回格式：

{{
    "validation_passed": true,
    "feedback": "审查意见"
}}
"""


def review_execution_result(
    task: AnalysisTask,
    data_context: dict[str, Any],
    execution_result: ExecutionResult
) -> dict[str, Any]:

    llm = create_llm()

    prompt = PromptTemplate.from_template(
        CRITIC_PROMPT
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
    "execution_result": json.dumps(
        execution_result,
        ensure_ascii=False,
        indent=2,
        default=str
    )
}

    result = invoke_json_with_retry(
        chain,
        inputs
    )

    return result