from ingestion.loader import load_data_sources

# csv
# tables = load_data_sources([
#     "data/financials.csv"
# ])

# print(tables.keys())

# financials = tables["financials"]

# print(financials)
# print(financials.dataframe.head())



# excel
# from ingestion.loader import load_data_sources


# tables = load_data_sources([
#     "data/company.xlsx"
# ])

# print(tables.keys())

# for table_name, resource in tables.items():
#     print("\nTABLE:", table_name)
#     print(resource.dataframe)



# sqlite
# from ingestion.loader import load_data_sources


# tables = load_data_sources([
#     "data/sales.sqlite"
# ])

# print(tables.keys())

# for table_name, resource in tables.items():
#     print("\nTABLE:", table_name)
#     print("source_type:", resource.source_type)
#     print("source_path:", resource.source_path)
#     print("database_table:", resource.database_table)
#     print("dataframe:", resource.dataframe)