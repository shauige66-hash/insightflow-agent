# 项目启动入口，负责启动整个 InsightFlow 分析流程。
from utils.run_logger import create_run_id, log_event
from workflow import create_workflow


def main():

    run_id = create_run_id()

    print(f"Run ID: {run_id}")

    log_event(
            run_id=run_id,
            node="workflow",
            event="run_started",
            status="started"
        )

    workflow = create_workflow()

    result = workflow.invoke(
    {
        # "data_sources": [
        # "data/sales.sqlite"
        # ],
        # "analysis_focus": (
        #     "重点分析订单和客户之间的关系。"
        #     "根据数据库中真实存在的字段进行分析，"
        #     "包括客户订单贡献、订单金额表现、客户购买行为等有价值的问题。"
        #     "如果需要关联多张表，请根据真实 schema 自动选择关联字段，"
        #     "不要编造不存在的字段或表关系。"
        # ),
        "run_id": run_id,
        "data_sources": [
        "data/customers.csv",
        "data/orders.csv"
    ],
    "analysis_focus": (
        "重点分析客户地区与订单之间的关系。"
        "需要关联 customers 和 orders 两张表，"
        "比较不同地区的订单总金额、订单数量和平均订单金额，"
        "并识别订单金额最高的地区。"
    ),
        "execution_results": [],
        "failed_tasks": [],
        "visualization_results": [],
        "artifacts": [],
    },
    config={
        "recursion_limit": 100
    }
)

    log_event(
    run_id=run_id,
    node="workflow",
    event="run_completed",
    status="success",
    details={
        "analysis_tasks": len(
            result.get(
                "analysis_plan",
                []
            )
        ),
        "failed_tasks": len(
            result.get(
                "failed_tasks",
                []
            )
        ),
        "visualizations": len(
            result.get(
                "visualization_plan",
                []
            )
        ),
        "artifacts": result.get(
            "artifacts",
            []
        )
    }
)

    print("\n=== Analysis Plan ===")
    print(result.get("analysis_plan"))

    print("\n=== Execution Results ===")
    print(result.get("execution_results"))

    print("\n=== Failed Tasks ===")
    print(result.get("failed_tasks", []))

    print("\n=== Final Report ===")
    print(result.get("report_content"))

    print("\n=== Report Path ===")
    print(result.get("report_path"))

    print("\n=== Artifacts ===")
    print(result.get("artifacts", []))

    print("\n=== Visualization Results ===")
    print(result.get("visualization_results", []))

    print("\n=== Visualization Plan ===")
    print(result.get("visualization_plan", []))

if __name__ == "__main__":
    main()