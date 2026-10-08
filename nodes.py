# 定义 LangGraph 工作流节点，负责读取和更新共享 State。

from state import InsightFlowState
from ingestion.loader import load_data_sources
from context.context_builder import build_all_contexts
from agents.planner import create_analysis_plan
from agents.router import route_analysis_task
from agents.executor import generate_execution_code
from tools.python_tool import create_python_tool
from tools.sql_tool import create_sql_tool
from agents.repair import repair_execution_code
from agents.critic import review_execution_result
from agents.refine import refine_execution_code
from agents.reporter import generate_analysis_report
from utils.artifacts import save_markdown_report,save_html_report,save_pdf_report
from agents.visualizer import create_visualization_plan
from agents.plotter import generate_plot_code
from tools.plot_tool import create_plot_tool
from agents.plot_repair import repair_plot_code
from pathlib import Path
from utils.run_logger import log_event
from time import perf_counter
from rag.knowledge_service import build_and_retrieve_knowledge

def loader_node(
    state: InsightFlowState
) -> dict:

    tables = load_data_sources(
        state["data_sources"]
    )

    return {
        "tables": tables
    }


def context_node(
    state: InsightFlowState
) -> dict:

    contexts = build_all_contexts(
        state["tables"]
    )

    return {
        "data_context": contexts
    }


def knowledge_retrieval_node(
    state: InsightFlowState
) -> dict:

    knowledge_sources = state.get(
        "knowledge_sources",
        []
    )

    if not knowledge_sources:
        return {
            "retrieved_knowledge": [],
            "retrieved_knowledge_details": []
        }

    analysis_focus = state.get(
        "analysis_focus"
    )

    query = (
        analysis_focus
        or "与当前数据分析相关的业务规则、指标定义和术语"
    )

    retrieved_knowledge_details = (
        build_and_retrieve_knowledge(
            knowledge_sources=knowledge_sources,
            query=query
        )
    )

    retrieved_knowledge = [
        item["content"]
        for item in retrieved_knowledge_details
        if item.get("content")
    ]

    return {
        "retrieved_knowledge": retrieved_knowledge,
        "retrieved_knowledge_details": (retrieved_knowledge_details)
    }


def planner_node(
    state: InsightFlowState
) -> dict:

    retrieved_knowledge = state.get(
        "retrieved_knowledge",
        []
    )

    plan = create_analysis_plan(
        contexts=state["data_context"],
        analysis_focus=state.get(
            "analysis_focus"
        ),
        retrieved_knowledge=retrieved_knowledge
    )

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="planner",
            event="plan_created",
            status="success",
            details={
                "task_count": len(plan),
                "task_ids": [
                    task["task_id"]
                    for task in plan
                ],
                "retrieved_knowledge_count": len(
                    retrieved_knowledge
                )
            }
        )

    return {
        "analysis_plan": plan,
        "current_task_index": 0
    }



def router_node(
    state: InsightFlowState
) -> dict:

    index = state["current_task_index"]

    task = state["analysis_plan"][index]

    tool = route_analysis_task(
        task,
        state["tables"]
    )
    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="router",
            event="route_selected",
            status="success",
            details={
                "task_id": task["task_id"],
                "route": tool,
                "target_tables": task[
                    "target_tables"
                ]
            }
        )

    return {
        "current_tool": tool
    }


def execution_node(
    state: InsightFlowState
) -> dict:
    started_at = perf_counter()
    index = state["current_task_index"]

    task = state["analysis_plan"][index]

    data_context = {
        table_name: state["data_context"][table_name]
        for table_name in task["target_tables"]
    }

    tool = state["current_tool"]

    if tool is None:
        raise ValueError(
            "Current tool is missing."
        )

    retrieved_knowledge = state.get(
    "retrieved_knowledge",
    []
    )

    code = generate_execution_code(
        task=task,
        data_context=data_context,
        route=tool,
        retrieved_knowledge=retrieved_knowledge
    )

    duration_ms = (
    perf_counter() - started_at
    ) * 1000

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="execution_generation",
            event="analysis_code_generated",
            status="success",
            details={
                "task_id": task["task_id"],
                "tool": tool,
                "target_tables": task[
                    "target_tables"
                ]
            },
            duration_ms=duration_ms
        )

    return {
        "current_code": code
    }



def tool_execution_node(
    state: InsightFlowState
) -> dict:



    index = state["current_task_index"]
    task = state["analysis_plan"][index]

    tool = state["current_tool"]
    code = state["current_code"]

    if tool is None:
        raise ValueError("Current tool is missing.")

    if code is None:
        raise ValueError("Current code is missing.")

    if tool == "python":
        python_tool = create_python_tool(
            state["tables"]
        )


        execution = python_tool.invoke({
            "table_names": task["target_tables"],
            "code": code
        })

    elif tool == "sql":

        sql_tool = create_sql_tool(
            state["tables"]
        )

        execution = sql_tool.invoke({
            "table_names": task["target_tables"],
            "query": code
        })

    else:
        raise ValueError(
            f"Unsupported tool: {tool}"
        )

    execution_result = {
        "task_id": task["task_id"],
        "tool_used": tool,
        "code": code,
        "success": execution["success"],
        "result": execution["result"],
        "error": execution["error"]
    }

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="tool_execution",
            event="execution_completed",
            status=(
                "success"
                if execution["success"]
                else "failed"
            ),
            details={
                "task_id": task["task_id"],
                "tool": tool,
                "target_tables": task[
                    "target_tables"
                ],
                "retry_count": state.get(
                    "retry_count",
                    0
                ),
                "refine_count": state.get(
                    "refine_count",
                    0
                ),
                "error": execution["error"]
            }
        )

    previous_results = state.get(
        "execution_results",
        []
    )

    return {
        "execution_results": previous_results + [
            execution_result
        ],
        "execution_error": execution["error"]
    }


def repair_node(
    state: InsightFlowState
) -> dict:

    retrieved_knowledge = state.get(
    "retrieved_knowledge",
    []
)

    index = state["current_task_index"]
    task = state["analysis_plan"][index]

    data_context = {
        table_name: state["data_context"][table_name]
        for table_name in task["target_tables"]
    }

    tool = state["current_tool"]
    code = state["current_code"]
    error = state["execution_error"]

    if tool is None:
        raise ValueError("Current tool is missing.")

    if code is None:
        raise ValueError("Current code is missing.")

    if error is None:
        raise ValueError("Execution error is missing.")

    repaired_code = repair_execution_code(
        task=task,
        data_context=data_context,
        route=tool,
        code=code,
        error=error,
        retrieved_knowledge=retrieved_knowledge
    )

    retry_count = state.get(
        "retry_count",
        0
    ) + 1

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="repair",
            event="repair_generated",
            status="success",
            details={
                "task_id": task["task_id"],
                "tool": tool,
                "retry_count": retry_count,
                "previous_error": error
            }
        )

    return {
        "current_code": repaired_code,
        "retry_count": retry_count
    }




def get_final_execution_results(
    execution_results: list[dict]
) -> list[dict]:

    final_results = {}

    for item in execution_results:
        final_results[item["task_id"]] = item

    return list(final_results.values())

    

def get_final_visualization_results(
    visualization_results: list[dict]
) -> list[dict]:

    final_results = {}

    for item in visualization_results:
        final_results[item["chart_id"]] = item

    return list(final_results.values())

    

def advance_task_node(
    state: InsightFlowState
) -> dict:

    current_index = state[
        "current_task_index"
    ]

    current_task = state[
        "analysis_plan"
    ][current_index]

    if state.get(
        "validation_passed",
        False
    ):
        run_id = state.get("run_id")

        if run_id is not None:
            log_event(
                run_id=run_id,
                node="task",
                event="task_completed",
                status="success",
                details={
                    "task_id": current_task[
                        "task_id"
                    ],
                    "retry_count": state.get(
                        "retry_count",
                        0
                    ),
                    "refine_count": state.get(
                        "refine_count",
                        0
                    )
                }
            )

    next_index = current_index + 1

    return {
        "current_task_index": next_index,
        "current_tool": None,
        "current_code": None,
        "execution_error": None,
        "retry_count": 0,
        "refine_count": 0,
        "critic_feedback": None,
        "validation_passed": False
    }



def critic_node(
    state: InsightFlowState
) -> dict:
    retrieved_knowledge = state.get(
    "retrieved_knowledge",
    []
)
    index = state["current_task_index"]
    task = state["analysis_plan"][index]

    data_context = {
        table_name: state["data_context"][table_name]
        for table_name in task["target_tables"]
    }

    execution_result = state["execution_results"][-1]

    review = review_execution_result(
        task=task,
        data_context=data_context,
        execution_result=execution_result,
        retrieved_knowledge=retrieved_knowledge
    )

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="critic",
            event="validation_completed",
            status=(
                "passed"
                if review["validation_passed"]
                else "failed"
            ),
            details={
                "task_id": task["task_id"],
                "validation_passed": review[
                    "validation_passed"
                ],
                "refine_count": state.get(
                    "refine_count",
                    0
                ),
                "feedback": review[
                    "feedback"
                ]
            }
        )

    return {
        "validation_passed": review["validation_passed"],
        "critic_feedback": review["feedback"]
    }



def refine_node(
    state: InsightFlowState
) -> dict:
    
    retrieved_knowledge = state.get(
    "retrieved_knowledge",
    []
)
    index = state["current_task_index"]

    task = state["analysis_plan"][index]

    data_context = {
        table_name: state["data_context"][table_name]
        for table_name in task["target_tables"]
    }

    tool = state["current_tool"]

    code = state["current_code"]

    execution_result = state[
        "execution_results"
    ][-1]

    critic_feedback = state[
        "critic_feedback"
    ]

    if tool is None:
        raise ValueError(
            "Current tool is missing."
        )

    if code is None:
        raise ValueError(
            "Current code is missing."
        )

    if critic_feedback is None:
        raise ValueError(
            "Critic feedback is missing."
        )

    refined_code = refine_execution_code(
        task=task,
        data_context=data_context,
        route=tool,
        code=code,
        execution_result=execution_result,
        critic_feedback=critic_feedback,
        retrieved_knowledge=retrieved_knowledge
    )

    refine_count = state.get(
        "refine_count",
        0
    ) + 1

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="refine",
            event="refinement_generated",
            status="success",
            details={
                "task_id": task["task_id"],
                "tool": tool,
                "refine_count": refine_count,
                "critic_feedback": critic_feedback
            }
        )

    return {
        "current_code": refined_code,
        "refine_count": refine_count
    }



def failed_task_node(
    state: InsightFlowState
) -> dict:

    index = state["current_task_index"]
    task = state["analysis_plan"][index]

    execution_error = state.get("execution_error")
    critic_feedback = state.get("critic_feedback")

    if execution_error is not None:
        stage = "execution"
        reason = execution_error

    elif critic_feedback is not None:
        stage = "validation"
        reason = critic_feedback

    else:
        raise ValueError(
            "Task failure reason is missing."
        )

    failure = {
        "task_id": task["task_id"],
        "stage": stage,
        "reason": reason,
        "code": state.get("current_code"),
        "retry_count": state.get(
            "retry_count",
            0
        ),
        "refine_count": state.get(
            "refine_count",
            0
        )
    }

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="task",
            event="task_failed",
            status="failed",
            details={
                "task_id": task["task_id"],
                "stage": stage,
                "reason": reason,
                "retry_count": state.get(
                    "retry_count",
                    0
                ),
                "refine_count": state.get(
                    "refine_count",
                    0
                )
            }
        )


    previous_failures = state.get(
        "failed_tasks",
        []
    )

    return {
        "failed_tasks": previous_failures + [
            failure
        ]
    }

def report_node(
    state: InsightFlowState
) -> dict:

    final_execution_results = (
        get_final_execution_results(
            state.get(
                "execution_results",
                []
            )
        )
    )

    final_visualization_results = (
        get_final_visualization_results(
            state.get(
                "visualization_results",
                []
            )
        )
    )

    visualization_plan_by_id = {
        item["chart_id"]: item
        for item in state.get(
            "visualization_plan",
            []
        )
    }

    report_visualizations = []

    for item in final_visualization_results:

        result_item = dict(item)

        visualization_task = (
            visualization_plan_by_id.get(
                item["chart_id"]
            )
        )

        if visualization_task is not None:
            result_item["description"] = (
                visualization_task["description"]
            )

            result_item["chart_type"] = (
                visualization_task["chart_type"]
            )

            result_item["target_tables"] = (
                visualization_task["target_tables"]
            )

            result_item["expected_output"] = (
                visualization_task["expected_output"]
            )

        if result_item.get("path"):
            result_item["markdown_path"] = Path(
                result_item["path"]
            ).name

        report_visualizations.append(
            result_item
        )

    report = generate_analysis_report(
        analysis_plan=state["analysis_plan"],
        execution_results=final_execution_results,
        failed_tasks=state.get(
            "failed_tasks",
            []
        ),
        visualization_plan=state.get(
            "visualization_plan",
            []
        ),
        visualization_results=report_visualizations
    )

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="report",
            event="report_generated",
            status="success",
            details={
                "analysis_task_count": len(
                    state["analysis_plan"]
                ),
                "execution_result_count": len(
                    final_execution_results
                ),
                "failed_task_count": len(
                    state.get(
                        "failed_tasks",
                        []
                    )
                ),
                "visualization_count": len(
                    report_visualizations
                )
            }
        )

    return {
        "report_content": report
    }


def artifact_node(
    state: InsightFlowState
) -> dict:

    report_content = state[
        "report_content"
    ]

    if report_content is None:
        raise ValueError(
            "Report content is missing."
        )

    run_id = state.get(
        "run_id"
    )

    if run_id is None:
        raise ValueError(
            "Run ID is missing."
        )

    output_dir = (
        Path("outputs")
        / run_id
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    markdown_path = save_markdown_report(
        report_content,
        output_path=str(
            output_dir
            / "analysis_report.md"
        )
    )

    html_path = save_html_report(
        report_content,
        output_path=str(
            output_dir
            / "analysis_report.html"
        )
    )

    pdf_path = save_pdf_report(
        html_path,
        output_path=str(
            output_dir
            / "analysis_report.pdf"
        )
    )

    log_event(
        run_id=run_id,
        node="artifact",
        event="report_artifacts_saved",
        status="success",
        details={
            "markdown_path": markdown_path,
            "html_path": html_path,
            "pdf_path": pdf_path
        }
    )

    previous_artifacts = state.get(
        "artifacts",
        []
    )

    return {
        "report_path": markdown_path,
        "artifacts": (
            previous_artifacts
            + [
                markdown_path,
                html_path,
                pdf_path
            ]
        )
    }


def visualization_planner_node(
    state: InsightFlowState
) -> dict:

    final_execution_results = (
        get_final_execution_results(
            state.get(
                "execution_results",
                []
            )
        )
    )

    visualization_plan = create_visualization_plan(
        analysis_plan=state["analysis_plan"],
        execution_results=final_execution_results,
        failed_tasks=state.get(
            "failed_tasks",
            []
        )
    )

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="visualization_planner",
            event="visualization_plan_created",
            status="success",
            details={
                "chart_count": len(
                    visualization_plan
                ),
                "charts": [
                    {
                        "chart_id": item["chart_id"],
                        "source_task_id": item[
                            "source_task_id"
                        ],
                        "chart_type": item[
                            "chart_type"
                        ]
                    }
                    for item in visualization_plan
                ]
            }
        )

    return {
        "visualization_plan": visualization_plan,
        "current_chart_index": 0
    }


def plot_generation_node(
    state: InsightFlowState
) -> dict:

    index = state["current_chart_index"]

    visualization_task = state[
        "visualization_plan"
    ][index]

    target_tables = visualization_task[
        "target_tables"
    ]

    data_context = {
        table_name: state[
            "data_context"
        ][table_name]
        for table_name in target_tables
    }

    source_task_id = visualization_task[
        "source_task_id"
    ]

    source_execution_result = next(
        (
            result
            for result in reversed(
                state["execution_results"]
            )
            if (
                result["task_id"]
                == source_task_id
                and result["success"]
            )
        ),
        None
    )

    if source_execution_result is None:
        raise ValueError(
            f"No successful execution result found "
            f"for source task: {source_task_id}"
        )

    generation = generate_plot_code(
        visualization_task=visualization_task,
        data_context=data_context,
        execution_result=source_execution_result
    )

    code = generation["code"]

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="plot_generation",
            event="plot_code_generated",
            status="success",
            details={
                "chart_id": visualization_task[
                    "chart_id"
                ],
                "source_task_id": source_task_id,
                "chart_type": visualization_task[
                    "chart_type"
                ],
                "target_tables": target_tables,
                "generation_attempts": generation[
                    "attempts"
                ],
                "generation_retry_errors": generation[
                    "retry_errors"
                ]
            }
        )

    return {
        "current_plot_code": code,
        "plot_error": None
    }





def plot_execution_node(
    state: InsightFlowState
) -> dict:

    index = state["current_chart_index"]

    visualization_task = state[
        "visualization_plan"
    ][index]

    code = state["current_plot_code"]

    if code is None:
        raise ValueError(
            "Current plot code is missing."
        )

    target_tables = visualization_task[
        "target_tables"
    ]

    chart_id = visualization_task[
        "chart_id"
    ]

    source_task_id = visualization_task[
        "source_task_id"
    ]

    source_execution_result = next(
        (
            result
            for result in reversed(
                state["execution_results"]
            )
            if (
                result["task_id"]
                == source_task_id
                and result["success"]
            )
        ),
        None
    )

    if source_execution_result is None:
        raise ValueError(
            f"No successful execution result found "
            f"for source task: {source_task_id}"
        )

    run_id = state.get("run_id")

    if run_id is None:
        raise ValueError(
            "Run ID is missing."
        )

    output_dir = (
        Path("outputs")
        / run_id
    )

    plot_tool = create_plot_tool(
        state["tables"],
        output_dir=str(output_dir)
    )

    execution = plot_tool.invoke({
        "table_names": target_tables,
        "chart_id": chart_id,
        "code": code,
        "analysis_result": (
            source_execution_result["result"]
        )
    })

    visualization_result = {
        "chart_id": chart_id,
        "code": code,
        "success": execution["success"],
        "path": execution["result"],
        "error": execution["error"]
    }

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="plot_execution",
            event="plot_execution_completed",
            status=(
                "success"
                if execution["success"]
                else "failed"
            ),
            details={
                "chart_id": chart_id,
                "source_task_id": source_task_id,
                "chart_type": visualization_task[
                    "chart_type"
                ],
                "plot_retry_count": state.get(
                    "plot_retry_count",
                    0
                ),
                "path": execution["result"],
                "error": execution["error"]
            }
        )

    previous_results = state.get(
        "visualization_results",
        []
    )

    updates = {
        "visualization_results": (
            previous_results
            + [visualization_result]
        ),
        "plot_error": execution["error"]
    }

    if execution["success"]:

        previous_artifacts = state.get(
            "artifacts",
            []
        )

        updates["artifacts"] = (
            previous_artifacts
            + [execution["result"]]
        )

    return updates


def advance_chart_node(
    state: InsightFlowState
) -> dict:

    current_index = state[
        "current_chart_index"
    ]

    visualization_task = state[
        "visualization_plan"
    ][current_index]

    chart_id = visualization_task[
        "chart_id"
    ]

    latest_result = next(
        (
            result
            for result in reversed(
                state.get(
                    "visualization_results",
                    []
                )
            )
            if result["chart_id"] == chart_id
        ),
        None
    )

    run_id = state.get("run_id")

    if (
        run_id is not None
        and latest_result is not None
    ):
        if latest_result["success"]:
            log_event(
                run_id=run_id,
                node="chart",
                event="chart_completed",
                status="success",
                details={
                    "chart_id": chart_id,
                    "source_task_id": (
                        visualization_task[
                            "source_task_id"
                        ]
                    ),
                    "plot_retry_count": state.get(
                        "plot_retry_count",
                        0
                    ),
                    "path": latest_result[
                        "path"
                    ]
                }
            )

        else:
            log_event(
                run_id=run_id,
                node="chart",
                event="chart_failed",
                status="failed",
                details={
                    "chart_id": chart_id,
                    "source_task_id": (
                        visualization_task[
                            "source_task_id"
                        ]
                    ),
                    "plot_retry_count": state.get(
                        "plot_retry_count",
                        0
                    ),
                    "error": latest_result[
                        "error"
                    ]
                }
            )

    next_index = current_index + 1

    return {
        "current_chart_index": next_index,
        "current_plot_code": None,
        "plot_error": None,
        "plot_retry_count": 0
    }


def plot_repair_node(
    state: InsightFlowState
) -> dict:

    index = state["current_chart_index"]

    visualization_task = state[
        "visualization_plan"
    ][index]

    target_tables = visualization_task[
        "target_tables"
    ]

    data_context = {
        table_name: state[
            "data_context"
        ][table_name]
        for table_name in target_tables
    }

    source_task_id = visualization_task[
        "source_task_id"
    ]

    source_execution_result = next(
        (
            result
            for result in reversed(
                state["execution_results"]
            )
            if (
                result["task_id"]
                == source_task_id
                and result["success"]
            )
        ),
        None
    )

    if source_execution_result is None:
        raise ValueError(
            f"No successful execution result found "
            f"for source task: {source_task_id}"
        )

    code = state["current_plot_code"]

    error = state["plot_error"]

    if code is None:
        raise ValueError(
            "Current plot code is missing."
        )

    if error is None:
        raise ValueError(
            "Plot error is missing."
        )

    repaired_code = repair_plot_code(
        visualization_task=visualization_task,
        data_context=data_context,
        execution_result=source_execution_result,
        code=code,
        error=error
    )

    plot_retry_count = state.get(
        "plot_retry_count",
        0
    ) + 1

    run_id = state.get("run_id")

    if run_id is not None:
        log_event(
            run_id=run_id,
            node="plot_repair",
            event="plot_repair_generated",
            status="success",
            details={
                "chart_id": visualization_task[
                    "chart_id"
                ],
                "source_task_id": source_task_id,
                "plot_retry_count": plot_retry_count,
                "previous_error": error
            }
        )

    return {
        "current_plot_code": repaired_code,
        "plot_retry_count": plot_retry_count
    }