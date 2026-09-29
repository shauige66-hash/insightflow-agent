# 定义 LangGraph 工作流中的条件分支判断逻辑。

from typing import Literal

from state import InsightFlowState


MAX_RETRIES = 3
MAX_REFINES = 3
MAX_PLOT_RETRIES = 3

def route_after_execution(
    state: InsightFlowState
) -> Literal["repair", "critic", "failed"]:

    error = state.get("execution_error")
    retry_count = state.get("retry_count", 0)

    if error is None:
        return "critic"

    if retry_count < MAX_RETRIES:
        return "repair"

    return "failed"



def route_after_advance(
    state: InsightFlowState
) -> Literal["router", "complete"]:

    index = state["current_task_index"]

    total_tasks = len(
        state["analysis_plan"]
    )

    if index < total_tasks:
        return "router"

    return "complete"






def route_after_critic(
    state: InsightFlowState
) -> Literal["advance", "refine", "failed"]:

    passed = state.get("validation_passed")
    refine_count = state.get(
        "refine_count",
        0
    )

    if passed is True:
        return "advance"

    if passed is False:
        if refine_count < MAX_REFINES:
            return "refine"

        return "failed"

    raise ValueError(
        "Validation result is missing."
    )



def route_after_chart_advance(
    state: InsightFlowState
) -> Literal["plot_generation", "report"]:

    index = state["current_chart_index"]

    total_charts = len(
        state["visualization_plan"]
    )

    if index < total_charts:
        return "plot_generation"

    return "report"



def route_after_plot_execution(
    state: InsightFlowState
) -> Literal["plot_repair", "advance_chart"]:

    error = state.get("plot_error")

    retry_count = state.get(
        "plot_retry_count",
        0
    )

    if error is None:
        return "advance_chart"

    if retry_count < MAX_PLOT_RETRIES:
        return "plot_repair"

    return "advance_chart"