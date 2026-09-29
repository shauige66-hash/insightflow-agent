# 负责按需获取数据表的字段名称和数据类型等基础结构信息。
from typing import Any
import pandas as pd
from ingestion.models import TableResource
import sqlite3

def get_table_schema(resource: TableResource) -> dict[str, Any]:

    if resource.dataframe is not None:
        df = resource.dataframe

        return {
            "table_name": resource.name,
            "source_type": resource.source_type,
            "columns": {
                column: str(df[column].dtype)
                for column in df.columns
            }
        }


    elif resource.source_type == "sqlite":
        table_name = resource.database_table

        if table_name is None:
            raise ValueError(
                f"SQLite table name missing: {resource.name}"
            )

        safe_name = table_name.replace('"', '""')

        with sqlite3.connect(resource.source_path) as connection:
            schema_rows = connection.execute(
                f'PRAGMA table_info("{safe_name}")'
            ).fetchall()

        return {
            "table_name": resource.name,
            "source_type": resource.source_type,
            "columns": {
                row[1]: row[2]
                for row in schema_rows
            }
        }

    else:
        raise ValueError(
            f"Unsupported resource type: {resource.source_type}"
        )