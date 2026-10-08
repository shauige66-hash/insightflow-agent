# 定义各个 Agent 在工作流中共享的数据状态结构。
from typing import Any, Literal,TypedDict
from ingestion.models import TableResource


class AnalysisTask(TypedDict):
    task_id: str
    description: str
    target_tables: list[str]
    expected_output: str


class VisualizationTask(TypedDict):
    chart_id: str
    description: str
    source_task_id: str
    target_tables: list[str]
    chart_type: Literal[
        "line",
        "bar",
        "scatter"
    ]
    expected_output: str

class VisualizationResult(TypedDict):
    chart_id: str
    code: str
    success: bool
    path: str | None
    error: str | None

class ExecutionResult(TypedDict):
    task_id: str
    tool_used: Literal["python", "sql"]
    code: str
    success: bool
    result: Any
    error: str | None


class TaskFailure(TypedDict):
    task_id: str
    stage: Literal["execution", "validation"]
    reason: str
    code: str | None
    retry_count: int
    refine_count: int




# 工作流传递信息
class InsightFlowState(TypedDict, total=False):
    run_id: str  # 每次workflow唯一编号

    analysis_focus: str | None  # 提供分析重点（可选）

    data_sources: list[str]  # 文件数据

    tables: dict[str, TableResource]  # 数据表

    knowledge_sources: list[str]    #用户提供业务知识文件

    retrieved_knowledge: list[str]    # 针对当前分析问题实际检索出来的相关片段

    retrieved_knowledge_details: list[ dict[str, Any]]  # RAG 检索结果及其来源信息

    data_context: dict[str, dict[str, Any]]  # Adaptive Context 生成的数据上下文

    analysis_plan: list[AnalysisTask]  # Planner Agent 生成的分析计划

    current_task_index: int  # 当前正在执行的分析任务位置

    current_tool: Literal["python", "sql"] | None  # 选择的工具

    current_code: str | None  # 当前生成并准备执行的 Python 或 SQL 代码

    execution_results: list[ExecutionResult]  # 执行分析结果

    execution_error: str | None  # 执行错误

    retry_count: int  # 重试次数

    refine_count: int  # Critic 不通过后的代码改进次数

    critic_feedback: str | None  # Critic Agent 反馈

    failed_tasks: list[TaskFailure]  # 最终失败的分析任务记录

    validation_passed: bool  # 验证是否通过

    artifacts: list[str]  # 生成的文件

    report_path: str | None  # 报告路径

    report_content: str | None  # 最终生成的 Markdown 分析报告

    visualization_plan: list[VisualizationTask]  # Visualization Agent 生成的图表计划
    current_chart_index: int  # 当前正在处理的图表位置
    current_plot_code: str | None  # 当前生成并准备执行的绘图代码
    visualization_results: list[VisualizationResult]  # 图表生成结果
    plot_error: str | None  # 当前图表执行错误
    plot_retry_count: int  # 绘图失败后的修复次数c