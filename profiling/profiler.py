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