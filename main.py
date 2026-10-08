# 项目启动入口，负责通过命令行启动 InsightFlow 分析流程。

from services.analysis_service import run_analysis


def main():

    result = run_analysis(
        data_sources=[
            "data/customers.csv",
            "data/orders.csv"
        ],
        analysis_focus=(
            "分析不同地区的高价值客户表现，"
            "并比较各地区高价值客户的销售贡献。"
        ),
        knowledge_sources=[
            "knowledge/business_rules.md"
        ]
    )

    print("\n=== Run ID ===")
    print(
        result.get("run_id")
    )

    print("\n=== Retrieved Knowledge ===")
    print(
        result.get(
            "retrieved_knowledge",
            []
        )
    )

    print("\n=== Retrieved Knowledge Details ===")
    print(
        result.get(
            "retrieved_knowledge_details",
            []
        )
    )

    print("\n=== Analysis Plan ===")
    print(
        result.get(
            "analysis_plan",
            []
        )
    )

    print("\n=== Execution Results ===")
    print(
        result.get(
            "execution_results",
            []
        )
    )

    print("\n=== Failed Tasks ===")
    print(
        result.get(
            "failed_tasks",
            []
        )
    )

    print("\n=== Visualization Results ===")
    print(
        result.get(
            "visualization_results",
            []
        )
    )

    print("\n=== Final Report ===")
    print(
        result.get("report_content")
    )

    print("\n=== Report Path ===")
    print(
        result.get("report_path")
    )

    print("\n=== Artifacts ===")
    print(
        result.get(
            "artifacts",
            []
        )
    )


if __name__ == "__main__":
    main()