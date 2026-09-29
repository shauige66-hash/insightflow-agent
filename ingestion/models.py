# 定义不同数据源在系统中的统一数据结构。
from dataclasses import dataclass

import pandas as pd


@dataclass
class TableResource:
    name: str
    source_type: str
    source_path: str
    dataframe: pd.DataFrame | None = None
    database_table: str | None = None