# Prepares the sales data for Looker Studio
# Input : sales_data_for_powerbi.csv   (created by 2_cohort_analysis.py)
# Output: sales_data_for_looker.csv

import pandas as pd

df = pd.read_csv("sales_data_for_powerbi.csv")

# Total number of orders placed by each customer (over the whole period)
orders_per_customer = df.groupby("customerNumber")["orderNumber"].nunique()


df["CustomerOrderCount"] = df["customerNumber"].map(orders_per_customer)


df.to_csv("sales_data_for_looker.csv", index=False)
print("Rows:", len(df))
print("Customers with more than 1 order:", (orders_per_customer > 1).sum(), "of", len(orders_per_customer))
print("Done. File saved.")
