import sqlite3
import pandas as pd
import os

# Excel file location
excel_file = "data/Fulfillment_Hub_Dummy_Dataset.xlsx"

# SQLite database location
database_file = "fulfillment.db"

# Check Excel file
if not os.path.exists(excel_file):
    print("Excel file not found!")
    print("Expected location:", excel_file)
    exit()

# Connect to SQLite
conn = sqlite3.connect(database_file)

# Excel sheets to import
sheets = {
    "Orders": "orders",
    "Products": "products",
    "Warehouses": "warehouses",
    "Couriers": "couriers",
    "Inventory": "inventory",
    "Issues": "issues",
    "Transfers": "transfers"
}

print("Starting database setup...\n")

for excel_sheet, table_name in sheets.items():

    df = pd.read_excel(
        excel_file,
        sheet_name=excel_sheet
    )

    # Clean column names
    df.columns = df.columns.str.strip()

    # Write data into SQLite
    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    print(
        f"{excel_sheet}: {len(df)} records imported → {table_name}"
    )

conn.close()

print("\nDatabase created successfully!")
print("Database file:", database_file)