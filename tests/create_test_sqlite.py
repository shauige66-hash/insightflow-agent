import sqlite3

import pandas as pd


orders_df = pd.DataFrame({
    "order_id": [1, 2, 3],
    "customer_id": [101, 102, 101],
    "amount": [500, 800, 300]
})

customers_df = pd.DataFrame({
    "customer_id": [101, 102],
    "name": ["Alice", "Bob"]
})


with sqlite3.connect("data/sales.sqlite") as connection:
    orders_df.to_sql(
        "orders",
        connection,
        if_exists="replace",
        index=False
    )

    customers_df.to_sql(
        "customers",
        connection,
        if_exists="replace",
        index=False
    )