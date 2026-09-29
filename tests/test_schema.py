from ingestion.loader import load_data_sources
from profiling.schema import get_table_schema


tables = load_data_sources([
    "data/financials.csv",
    "data/sales.sqlite"
])

for table_name, resource in tables.items():
    schema = get_table_schema(resource)

    print(f"\nTABLE: {table_name}")
    print(schema)