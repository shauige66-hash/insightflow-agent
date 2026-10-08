from typing import Any
import sqlite3

import pandas as pd

from ingestion.models import TableResource


def build_light_profile(tables: dict[str, TableResource]) -> dict[str, dict[str, Any]]:

    profiles = {}

    for table_name, resource in tables.items():

        if resource.dataframe is not None:
            profiles[table_name] = _profile_dataframe(
                resource.dataframe,
                resource.source_type
            )

        elif resource.source_type == "sqlite":
            profiles[table_name] = _profile_sqlite(resource)

        else:
            raise ValueError(
                f"Cannot profile table: {table_name}"
            )

    return profiles


# 分析DataFrame
def _profile_dataframe(
    df: pd.DataFrame,
    source_type: str
) -> dict[str, Any]:

    dtypes = {}
    missing_values = {}

    for column in df.columns:
        dtypes[column] = str(
            df[column].dtype
        )
        missing_values[column] = int(
            df[column].isna().sum()
        )

    return {
        "source_type": source_type,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": dtypes,
        "missing_values": missing_values,
        "head_sample": df.head(3).to_dict(
            orient="records"
        ),
        "tail_sample": df.tail(3).to_dict(
            orient="records"
        )
    }



# 分析 SQLite 数据表
def _profile_sqlite(
    resource: TableResource
) -> dict[str, Any]:

    table_name = resource.database_table

    if table_name is None:
        raise ValueError(
            f"SQLite table name missing: "
            f"{resource.name}"
        )

    safe_name = table_name.replace(
        '"',
        '""'
    )

    with sqlite3.connect(
        resource.source_path
    ) as connection:

        schema_rows = connection.execute(
            f'PRAGMA table_info("{safe_name}")'
        ).fetchall()

        row_count = connection.execute(
            f'SELECT COUNT(*) FROM "{safe_name}"'
        ).fetchone()[0]

        sample_df = pd.read_sql_query(
            f'SELECT * FROM "{safe_name}" LIMIT 3',
            connection
        )

    return {
        "source_type": "sqlite",
        "row_count": row_count,
        "column_count": len(schema_rows),
        "columns": [
            row[1]
            for row in schema_rows
        ],
        "dtypes": {
            row[1]: row[2]
            for row in schema_rows
        },
        "head_sample": sample_df.to_dict(
            orient="records"
        )
    }