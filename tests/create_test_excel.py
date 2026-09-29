import pandas as pd


revenue_df = pd.DataFrame({
    "Year": [2023, 2024, 2025],
    "Revenue": [1200, 1350, 1500]
})

customers_df = pd.DataFrame({
    "Customer_ID": [1, 2, 3],
    "Region": ["Asia", "Europe", "America"]
})


with pd.ExcelWriter("data/company.xlsx") as writer:
    revenue_df.to_excel(
        writer,
        sheet_name="Revenue",
        index=False
    )

    customers_df.to_excel(
        writer,
        sheet_name="Customers",
        index=False
    )