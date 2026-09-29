# 负责连接各个 Agent 和工具，定义整个分析工作流。

from langgraph.graph import StateGraph, START, END
from state import InsightFlowState
from nodes import (
    loader_node,
    knowledge_retrieval_node,
    context_node,
    planner_node,
    router_node,
    execution_node,
    tool_execution_node,
    repair_node,
    critic_node,
    refine_node,
    failed_task_node,
    advance_task_node,
    report_node,
    artifact_node,

    visualization_planner_node,
    plot_generation_node,
    plot_execution_node,
    plot_repair_node,
    advance_chart_node,
)

from conditions import (
    route_after_execution,
    route_after_critic,
    route_after_advance,
    route_after_plot_execution,
    route_after_chart_advance,
    route_after_visualization_plan,
)


def create_workflow():

    graph = StateGraph(
        InsightFlowState
    )

    graph.add_node(
        "loader",
        loader_node
    )

    graph.add_node(
        "context",
        context_node
    )

    graph.add_node(
    "knowledge_retrieval",
    knowledge_retrieval_node
    )

    graph.add_node(
        "planner",
        planner_node
    )

    graph.add_node(
        "router",
        router_node
    )

    graph.add_node(
        "execution",
        execution_node
    )

    graph.add_node(
        "tool_execution",
        tool_execution_node
    )

    graph.add_node(
        "repair",
        repair_node
    )

    graph.add_node(
        "critic",
        critic_node
    )

    graph.add_node(
        "refine",
        refine_node
    )

    graph.add_node(
        "failed_task",
        failed_task_node
    )

    graph.add_node(
        "advance_task",
        advance_task_node
    )

    graph.add_node(
    "report",
    report_node
    )

    graph.add_node(
    "artifact",
    artifact_node
    )


    graph.add_node(
    "visualization_planner",
    visualization_planner_node
)

    graph.add_node(
        "plot_generation",
        plot_generation_node
    )

    graph.add_node(
        "plot_execution",
        plot_execution_node
    )

    graph.add_node(
        "plot_repair",
        plot_repair_node
    )

    graph.add_node(
        "advance_chart",
        advance_chart_node
    )



    graph.add_edge(
        START,
        "loader"
    )

    graph.add_edge(
        "loader",
        "context"
    )

  
    graph.add_edge(
    "context",
    "knowledge_retrieval"
)

    graph.add_edge(
        "knowledge_retrieval",
        "planner"
    )

    graph.add_edge(
        "planner",
        "router"
    )

    graph.add_edge(
        "router",
        "execution"
    )

    graph.add_edge(
        "execution",
        "tool_execution"
    )

    graph.add_conditional_edges(
        "tool_execution",
        route_after_execution,
        {
            "repair": "repair",
            "critic": "critic",
            "failed": "failed_task",
        }
    )

    graph.add_edge(
        "repair",
        "tool_execution"
    )

    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "advance": "advance_task",
            "refine": "refine",
            "failed": "failed_task",
        }
    )

    graph.add_edge(
        "refine",
        "tool_execution"
    )

    graph.add_edge(
        "failed_task",
        "advance_task"
    )

    graph.add_conditional_edges(
        "advance_task",
        route_after_advance,
        {
            "router": "router",
            "complete": "visualization_planner",
        }
    )

    graph.add_conditional_edges(
        "visualization_planner",
        route_after_visualization_plan,
        {
            "plot_generation": "plot_generation",
            "report": "report",
        }
    )

    graph.add_edge(
        "plot_generation",
        "plot_execution"
    )


    graph.add_conditional_edges(
    "plot_execution",
    route_after_plot_execution,
    {
        "plot_repair": "plot_repair",
        "advance_chart": "advance_chart",
    }
    )

    graph.add_edge(
    "plot_repair",
    "plot_execution"
    )

    graph.add_conditional_edges(
    "advance_chart",
    route_after_chart_advance,
    {
        "plot_generation": "plot_generation",
        "report": "report",
    }
    )


    graph.add_edge(
        "report",
        "artifact"
    )

    graph.add_edge(
        "artifact",
        END
    )

    return graph.compile()