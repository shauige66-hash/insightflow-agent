# 执行 Matplotlib 绘图代码，并将生成的图表保存到 outputs 目录。

from pathlib import Path
from typing import Any
import re

import matplotlib.pyplot as plt
import pandas as pd

from langchain_core.tools import tool

from ingestion.models import TableResource


def build_result_dataframe(
    analysis_result: Any
) -> pd.DataFrame | None:

    if isinstance(
        analysis_result,
        pd.DataFrame
    ):
        return analysis_result.copy()

    if isinstance(
        analysis_result,
        list
    ):
        if all(
            isinstance(item, dict)
            for item in analysis_result
        ):
            return pd.DataFrame(
                analysis_result
            )

    if isinstance(
        analysis_result,
        dict
    ):

        dataframe_candidates = []

        for value in analysis_result.values():

            if isinstance(
                value,
                pd.DataFrame
            ):
                dataframe_candidates.append(
                    value.copy()
                )

            elif (
                isinstance(value, list)
                and all(
                    isinstance(item, dict)
                    for item in value
                )
            ):
                dataframe_candidates.append(
                    pd.DataFrame(value)
                )

        if len(dataframe_candidates) == 1:
            return dataframe_candidates[0]

        if all(
            not isinstance(
                value,
                (
                    dict,
                    list,
                    tuple,
                    set,
                    pd.DataFrame
                )
            )
            for value in analysis_result.values()
        ):
            return pd.DataFrame([
                analysis_result
            ])

    return None


def create_plot_tool(
    tables: dict[str, TableResource]
):

    @tool
    def run_plot(
        table_names: list[str],
        chart_id: str,
        code: str,
        analysis_result: Any
    ) -> dict[str, Any]:
        """根据分析结果和可用 DataFrame 执行 Matplotlib 绘图代码并保存图表。"""

        if not table_names:
            raise ValueError(
                "At least one table is required."
            )

        dfs = {}

        for table_name in table_names:

            if table_name not in tables:
                raise ValueError(
                    f"Table not found: {table_name}"
                )

            resource = tables[
                table_name
            ]

            if resource.dataframe is not None:
                dfs[table_name] = (
                    resource.dataframe.copy()
                )

            elif resource.source_type != "sqlite":
                raise ValueError(
                    f"Unsupported table resource: "
                    f"{table_name}"
                )

        if not re.fullmatch(
            r"[A-Za-z0-9\_-]+",
            chart_id
        ):
            raise ValueError(
                f"Invalid chart id: {chart_id}"
            )

        result_df = build_result_dataframe(
            analysis_result
        )

        plt.rcdefaults()

        plt.rcParams[
            "font.family"
        ] = "sans-serif"

        plt.rcParams[
            "font.sans-serif"
        ] = [
            "Microsoft YaHei",
            "SimHei",
            "DejaVu Sans",
        ]

        plt.rcParams[
            "axes.unicode_minus"
        ] = False

        output_dir = Path(
            "outputs"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = (
            output_dir
            / f"{chart_id}.png"
        )

        safe_builtins = {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "range": range,
            "round": round,
            "set": set,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
        }

        execution_scope = {
            "analysis_result": analysis_result,
            "result_df": result_df,
            "dfs": dfs,
            "plt": plt,
            "output_path": str(
                output_path
            ),
            "__builtins__": safe_builtins,
        }

        if (
            len(table_names) == 1
            and table_names[0] in dfs
        ):
            execution_scope["df"] = dfs[
                table_names[0]
            ]

        forbidden_patterns = [
            "plt.rcParams",
            "matplotlib.rcParams",
            "font_manager",
            
        ]

        for pattern in forbidden_patterns:

            if pattern in code:
                return {
                    "success": False,
                    "result": None,
                    "error": (
                        f"Plot code contains forbidden "
                        f"pattern: {pattern}"
                    )
                }

        try:

            exec(
                code,
                execution_scope,
                execution_scope
            )

            if "result" not in execution_scope:
                raise ValueError(
                    "Plot code must store its final "
                    "output in 'result'."
                )

            if not output_path.exists():
                raise ValueError(
                    "Plot code did not create the "
                    "expected image file."
                )

            return {
                "success": True,
                "result": str(
                    output_path
                ),
                "error": None
            }

        except Exception as error:

            return {
                "success": False,
                "result": None,
                "error": str(error)
            }

        finally:
            plt.close("all")

    return run_plot