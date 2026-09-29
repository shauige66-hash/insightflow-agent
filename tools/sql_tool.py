# 把 SQLite 查询能力包装成可供 AI 调用的 SQL Tool。

from pathlib import Path
from typing import Any
import sqlite3

import pandas as pd
from langchain_core.tools import tool

from ingestion.models import TableResource


def create_sql_tool(
    tables: dict[str, TableResource]
):

    @tool
    def run_sql_query(
        table_names: list[str],
        query: str
    ) -> dict[str, Any]:
        """对同一个 SQLite 数据库中的一个或多个数据表执行只读 SQL 查询。"""

        if not table_names:
            raise ValueError(
                "At least one table is required."
            )

        sqlite_resources = []

        for table_name in table_names:

            if table_name not in tables:
                raise ValueError(
                    f"Table not found: {table_name}"
                )

            resource = tables[table_name]

            if resource.source_type != "sqlite":
                raise ValueError(
                    f"Table is not a SQLite resource: {table_name}"
                )

            sqlite_resources.append(resource)

        source_paths = {
            str(
                Path(resource.source_path).resolve()
            )
            for resource in sqlite_resources
        }

        if len(source_paths) != 1:
            raise ValueError(
                "SQL multi-table queries require all target "
                "tables to come from the same SQLite database."
            )

        database_path = next(
            iter(source_paths)
        )

        cleaned_query = query.strip()

        if not cleaned_query.lower().startswith(
            ("select", "with")
        ):
            return {
                "success": False,
                "result": None,
                "error": (
                    "Only SELECT or WITH queries "
                    "are allowed."
                )
            }

        try:
            with sqlite3.connect(
                database_path
            ) as connection:

                result_df = pd.read_sql_query(
                    cleaned_query,
                    connection
                )

            return {
                "success": True,
                "result": result_df.to_dict(
                    orient="records"
                ),
                "error": None
            }

        except Exception as error:
            return {
                "success": False,
                "result": None,
                "error": str(error)
            }

    return run_sql_query