# 根据绘图执行错误、分析结果和原始绘图代码，让大模型生成修复后的 Matplotlib 代码。

import json

from typing import Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from core.llm import create_llm
from state import ExecutionResult, VisualizationTask


PLOT_REPAIR_PROMPT = """
你是一个数据可视化代码修复 Agent。

可视化任务：

{visualization_task}

该图表对应的分析执行结果：

{execution_result}

相关原始数据上下文：

{data_context}

原始绘图代码：

{code}

执行错误：

{error}

请根据错误信息修复 Matplotlib 绘图代码。

执行环境将提供：

- analysis_result：
  source_task_id 对应分析任务的原始执行结果。

- result_df：
  如果 analysis_result 可以转换成二维表格，
  系统会提供对应的 Pandas DataFrame。

  - result_df 变量始终存在，但它的值可能为 None。

- 如果需要判断 result_df 是否可用，
  请使用：
  result_df is not None

- 不要使用 globals()、locals() 或 try/except NameError
  来检测 result_df 是否存在。

- dfs：
  一个字典，包含当前图表涉及的原始 Pandas DataFrame。
  只有 DataFrame 类型的数据源才会出现在这里。

- 如果当前图表只涉及一张 DataFrame 数据表，
  系统可能额外提供 df 作为快捷引用。

- plt：
  matplotlib.pyplot

- output_path：
  图片保存路径

要求：

1. 修复后的代码必须继续完成原始可视化任务。

2. 优先使用 source_task_id 对应的分析执行结果绘图。

3. 如果 result_df 可用，
   应优先使用 result_df.copy()，
   不要重新从原始数据重复计算已经完成的分析。

4. analysis_result 用于访问无法直接表示为单个 DataFrame 的分析结果。

5. 只有当分析执行结果不足以完成原始可视化任务时，
   才使用 dfs 中的原始 DataFrame 进行必要的补充处理。

6. 如果使用 dfs：

   - 必须使用真实的数据表名。
   - 多表任务通过 dfs["真实表名"] 分别访问 DataFrame。
   - 只有在数据上下文明确支持表关系时才能 merge 或 join。
   - 不要编造字段、关联键、分类映射或表关系。

7. 不要为了消除执行错误，
   就删除原可视化任务要求的关键指标或数据关系。

8. 不要把 execution_result、expected_output
   或 data_context 中的具体结果数值
   硬编码成 Python 列表、字典或映射。

9. 绘图数据必须来自 analysis_result、result_df
   或真实 DataFrame 的动态计算。

10. 不要执行 import。

11. 不要读取文件，不要访问网络。

12. 如果需要修改、排序或增加临时字段，
    应先使用 copy()，
    不要修改系统提供的原始对象。

13. 根据 chart_type 使用合适的 line、bar 或 scatter 图。

14. 图表必须包含清晰的标题、横轴标签和纵轴标签。

15. 必要时添加 legend。

16. 最终必须执行：

    plt.tight_layout()

    plt.savefig(
        output_path,
        bbox_inches="tight"
    )

    plt.close()

17. 最终必须将 result 设置为 output_path。

18. 只修复代码，不要解释错误原因。

只返回合法 JSON，不要输出其他文字。

返回格式：

{{
    "code": "修复后的 Matplotlib 绘图代码"
}}
"""


def repair_plot_code(
    visualization_task: VisualizationTask,
    data_context: dict[str, Any],
    execution_result: ExecutionResult,
    code: str,
    error: str
) -> str:

    llm = create_llm()

    prompt = PromptTemplate.from_template(
        PLOT_REPAIR_PROMPT
    )

    parser = JsonOutputParser()

    chain = prompt | llm | parser

    result = chain.invoke({
        "visualization_task": json.dumps(
            visualization_task,
            ensure_ascii=False,
            indent=2,
            default=str
        ),
        "execution_result": json.dumps(
            execution_result,
            ensure_ascii=False,
            indent=2,
            default=str
        ),
        "data_context": json.dumps(
            data_context,
            ensure_ascii=False,
            indent=2,
            default=str
        ),
        "code": code,
        "error": error
    })

    return result["code"]