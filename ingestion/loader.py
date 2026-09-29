# 负责加载 CSV、Excel 和 SQLite 数据源。
from pathlib import Path
import sqlite3
import pandas as pd
from ingestion.models import TableResource

def load_data_sources( data_sources: list[str]) -> dict[str, TableResource]:

    tables: dict[str, TableResource] = {}

    for source in data_sources:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(
                f"Data source not found: {path}"
            )

        suffix = path.suffix.lower()

        if suffix == ".csv":
           df = pd.read_csv(path)

           tables[path.stem] = TableResource(
           name=path.stem,
           source_type="csv",
           source_path=str(path),
           dataframe=df
           )

        elif suffix == ".xlsx":
            sheets = pd.read_excel(path,sheet_name=None)

            for sheet_name, df in sheets.items():
                table_name = f"{path.stem}.{sheet_name}"
                tables[table_name] = TableResource(
                    name=table_name,
                    source_type="excel",
                    source_path=str(path),
                    dataframe=df
                )

        elif suffix in {".db", ".sqlite", ".sqlite3"}:
            with sqlite3.connect(str(path)) as connection:

                table_names = pd.read_sql_query(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table'
                    AND name NOT LIKE 'sqlite_%';
                    """,
                    connection
                )["name"].tolist()

                for table_name in table_names:                   

                    key = f"{path.stem}.{table_name}"

                    tables[key] = TableResource(
                        name=key,
                        source_type="sqlite",
                        source_path=str(path),
                        database_table=table_name
                    )

        else:
            raise ValueError(
                f"Unsupported data source: {path.suffix}"
            )

    return tables