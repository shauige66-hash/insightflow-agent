# AI调用的 Schema Tool（查表结构）

from langchain_core.tools import tool

from ingestion.models import TableResource
from profiling.schema import get_table_schema


def create_schema_tool(tables: dict[str, TableResource]):

    @tool
    def inspect_schema(table_name: str) -> dict:
        """查看指定数据表的字段名称和数据类型。"""

        if table_name not in tables:
            raise ValueError(
                f"Table not found: {table_name}"
            )

        resource = tables[table_name]

        return get_table_schema(resource)

    return inspect_schema