# 根据数据规模动态构建发送给大模型的数据上下文
from typing import Any
import sqlite3
import pandas as pd
from ingestion.models import TableResource
from profiling.schema import get_table_schema


def build_dataframe_context( resource: TableResource) -> dict[str, Any]:

    if resource.dataframe is None:
        raise ValueError(
            f"Table is not a DataFrame resource: {resource.name}"
        )

    df = resource.dataframe

    row_count = len(df)
    column_count = len(df.columns)
    total_cells = row_count * column_count

    schema = get_table_schema(resource)

    if total_cells <= 500:
        data = df.to_dict(
            orient="records"
        )
        context_level = "full"

    elif total_cells <= 5000:
        data = {
            "head": df.head(10).to_dict(
                orient="records"
            ),
            "tail": df.tail(10).to_dict(
                orient="records"
            )
        }
        context_level = "sampled"

    else:
        data = {
            "head": df.head(5).to_dict(
                orient="records"
            ),
            "tail": df.tail(5).to_dict(
                orient="records"
            )
        }
        context_level = "minimal"

    return {
        "schema": schema,
        "row_count": row_count,
        "column_count": column_count,
        "context_level": context_level,
        "data": data
    }


def build_sqlite_context( resource: TableResource) -> dict[str, Any]:

    if resource.source_type != "sqlite":
        raise ValueError(
            f"Table is not a SQLite resource: {resource.name}"
        )

    table_name = resource.database_table

    if table_name is None:
        raise ValueError(
            f"SQLite table name missing: {resource.name}"
        )

    safe_name = table_name.replace('"', '""')

    schema = get_table_schema(resource)

    with sqlite3.connect(resource.source_path) as connection:
        row_count = connection.execute(
            f'SELECT COUNT(*) FROM "{safe_name}"'
        ).fetchone()[0]

        sample_df = pd.read_sql_query(
            f'SELECT * FROM "{safe_name}" LIMIT 5',
            connection
        )

    return {
        "schema": schema,
        "database_table": table_name,
        "row_count": row_count,
        "context_level": "minimal",
        "data": sample_df.to_dict(
            orient="records"
        )
    }


def build_context( resource: TableResource) -> dict[str, Any]:

    if resource.dataframe is not None:
        return build_dataframe_context(resource)

    if resource.source_type == "sqlite":
        return build_sqlite_context(resource)

    raise ValueError(
        f"Unsupported resource type: {resource.source_type}"
    )



def build_all_contexts( tables: dict[str, TableResource]) -> dict[str, dict[str, Any]]:

    contexts = {}

    for table_name, resource in tables.items():
        contexts[table_name] = build_context(resource)

    return contexts