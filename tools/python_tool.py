# 把 DataFrame 数据分析能力包装成可供 AI 调用的 Python Tool。

from typing import Any

import pandas as pd
from langchain_core.tools import tool

from ingestion.models import TableResource


def create_python_tool(
    tables: dict[str, TableResource]
):

    @tool
    def run_python_analysis(
        table_names: list[str],
        code: str
    ) -> dict[str, Any]:
        """对一个或多个 CSV / Excel 数据表执行 Pandas 分析代码。"""

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

            resource = tables[table_name]

            if resource.dataframe is None:
                raise ValueError(
                    f"Table is not a DataFrame resource: {table_name}"
                )

            dfs[table_name] = (
                resource.dataframe.copy()
            )

        safe_builtins = {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "float": float,
            "hasattr": hasattr,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "range": range,
            "round": round,
            "set": set,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            "sorted": sorted,
        }

        execution_scope = {
            "dfs": dfs,
            "pd": pd,
            "__builtins__": safe_builtins,
        }

        if len(table_names) == 1:
            execution_scope["df"] = (
                dfs[table_names[0]]
            )

        try:
            exec(
                code,
                execution_scope,
                execution_scope
            )

            if "result" not in execution_scope:
                raise ValueError(
                    "Python analysis code must store "
                    "its final output in 'result'."
                )

            return {
                "success": True,
                "result": execution_scope["result"],
                "error": None
            }

        except Exception as error:
            return {
                "success": False,
                "result": None,
                "error": str(error)
            }

    return run_python_analysis