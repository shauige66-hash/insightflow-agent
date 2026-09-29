# 根据已完成的分析结果规划最有价值的数据可视化任务。

import json
from typing import Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from core.llm import create_llm
from state import AnalysisTask, ExecutionResult, VisualizationTask


VISUALIZATION_PROMPT = """
你是一个数据可视化规划 Agent。

原始分析计划：

{analysis_plan}

分析执行结果：

{execution_results}

最终失败的任务：

{failed_tasks}

请根据已经成功得到的分析结果，规划 1 到 3 个最有价值的图表。

要求：

1. 只为已经成功执行并得到可靠结果的分析任务设计图表。

2. 不要为失败任务设计图表。

3. 不要为了数量而生成无意义或重复的图表。

4. 图表类型只能使用 line、bar、scatter。

5. 时间趋势优先使用 line。

6. 分类或指标比较优先使用 bar。

7. 数值变量关系分析可以使用 scatter。

8. 每个图表必须通过 source_task_id 指定它所依赖的分析任务。

9. source_task_id 必须来自 analysis_plan 中真实存在且执行成功的 task_id。

10. 每个图表应优先基于 source_task_id 对应的 execution_result 进行可视化，
    不要重新发明一套与原分析任务无关的计算逻辑。

11. 每个图表必须通过 target_tables 指定该分析任务涉及的数据表。

12. target_tables 必须是字符串列表，即使只需要一张表也必须使用列表形式。

13. target_tables 中的表名必须来自 source_task_id 对应分析任务的 target_tables。

14. 不要编造不存在的数据表、字段、分析任务或关联关系。

15. expected_output 只描述图表应该表达的信息，
    不要把具体结果硬编码成新的数据来源。

16. 这里只决定“画什么”和“基于哪个分析结果画”，
    不要生成 Python 绘图代码。

每个图表必须包含：

- chart_id
- description
- source_task_id
- target_tables
- chart_type
- expected_output

只返回合法 JSON，不要输出其他文字。

返回格式：

{{
    "charts": [
        {{
            "chart_id": "chart_1",
            "description": "图表描述",
            "source_task_id": "task_id",
            "target_tables": [
                "实际分析任务使用的数据表名"
            ],
            "chart_type": "bar",
            "expected_output": "预期展示的信息"
        }}
    ]
}}
"""


def create_visualization_plan(
    analysis_plan: list[AnalysisTask],
    execution_results: list[ExecutionResult],
    failed_tasks: list[dict[str, Any]]
) -> list[VisualizationTask]:

    llm = create_llm()

    prompt = PromptTemplate.from_template(
        VISUALIZATION_PROMPT
    )

    parser = JsonOutputParser()

    chain = prompt | llm | parser

    result = chain.invoke({
        "analysis_plan": json.dumps(
            analysis_plan,
            ensure_ascii=False,
            indent=2,
            default=str
        ),
        "execution_results": json.dumps(
            execution_results,
            ensure_ascii=False,
            indent=2,
            default=str
        ),
        "failed_tasks": json.dumps(
            failed_tasks,
            ensure_ascii=False,
            indent=2,
            default=str
        )
    })

    return result["charts"]