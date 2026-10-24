# Task 3 - KPIs and Cohort Analysis (classicmodels)
# Input : sales_data.csv   (exported from MySQL using 1_export_query.sql)
# Output: kpi_summary.csv, cohort_retention.csv, cohort_revenue.csv, sales_data_for_powerbi.csv

import pandas as pd

# 1 Load data
df = pd.read_csv("sales_data.csv")
df["orderDate"] = pd.to_datetime(df["orderDate"])

# Sales of each row = quantity x price
df["sales"] = df["quantityOrdered"] * df["priceEach"]

# Make year, quarter and a label like "2003Q1"
df["Year"] = df["orderDate"].dt.year
df["QuarterNo"] = df["orderDate"].dt.quarter
df["Quarter"] = df["Year"].astype(str) + "Q" + df["QuarterNo"].astype(str)

# A running quarter number so we can subtract quarters easily
df["QuarterNumber"] = df["Year"] * 4 + df["QuarterNo"]

# 2 Core KPIs
total_revenue = df["sales"].sum()
total_orders = df["orderNumber"].nunique()
total_customers = df["customerNumber"].nunique()
avg_order_value = total_revenue / total_orders

# Number of orders placed by each customer
orders_per_customer = df.groupby("customerNumber")["orderNumber"].nunique()

# Customers who ordered more than once
repeat_customers = (orders_per_customer > 1).sum()
repeat_rate = repeat_customers / total_customers * 100

kpi = pd.DataFrame({
    "KPI": ["Total Revenue", "Total Orders", "Average Order Value", "Repeat Customer Rate (%)"],
    "Value": [round(total_revenue, 2), total_orders, round(avg_order_value, 2), round(repeat_rate, 2)]
})
print(kpi)
kpi.to_csv("kpi_summary.csv", index=False)

# 3 Cohort analysis
# Cohort = the quarter in which a customer placed their FIRST order

# Sort by date and keep only the first order of each customer
first_orders = df.sort_values("orderDate").drop_duplicates("customerNumber")
first_orders = first_orders[["customerNumber", "Quarter", "QuarterNumber"]]
first_orders.columns = ["customerNumber", "Cohort", "CohortQuarterNumber"]

# Add the cohort of each customer to every row of the data
df = df.merge(first_orders, on="customerNumber")

# How many quarters after the first order did this purchase happen? (0 = first quarter)
df["QuartersSinceFirst"] = df["QuarterNumber"] - df["CohortQuarterNumber"]

# Number of customers in each cohort
cohort_size = first_orders["Cohort"].value_counts()

# Retention: how many customers of each cohort ordered in each quarter
retention = df.groupby(["Cohort", "QuartersSinceFirst"])["customerNumber"].nunique().reset_index()
retention.columns = ["Cohort", "QuartersSinceFirst", "ActiveCustomers"]
retention["CohortSize"] = retention["Cohort"].map(cohort_size)
retention["RetentionRate"] = (retention["ActiveCustomers"] / retention["CohortSize"] * 100).round(1)

# Lifetime value: revenue of each cohort in each quarter
revenue = df.groupby(["Cohort", "QuartersSinceFirst"])["sales"].sum().reset_index()
revenue = revenue.sort_values(["Cohort", "QuartersSinceFirst"])

# Running total of revenue for each cohort
revenue["CumulativeRevenue"] = revenue.groupby("Cohort")["sales"].cumsum()
revenue["CohortSize"] = revenue["Cohort"].map(cohort_size)

# LTV = total revenue so far / number of customers in the cohort
revenue["LTVPerCustomer"] = (revenue["CumulativeRevenue"] / revenue["CohortSize"]).round(2)
revenue["sales"] = revenue["sales"].round(2)
revenue["CumulativeRevenue"] = revenue["CumulativeRevenue"].round(2)

retention.to_csv("cohort_retention.csv", index=False)
revenue.to_csv("cohort_revenue.csv", index=False)

# Show the tables with cohorts as rows and quarters as columns
print("\nRetention table (%):")
print(retention.pivot(index="Cohort", columns="QuartersSinceFirst", values="RetentionRate"))
print("\nLTV per customer:")
print(revenue.pivot(index="Cohort", columns="QuartersSinceFirst", values="LTVPerCustomer"))

# 4 Save a clean copy for Power BI
df = df.drop(columns=["QuarterNo", "QuarterNumber", "CohortQuarterNumber"])
df.to_csv("sales_data_for_powerbi.csv", index=False)
print("\nDone. Files saved.")
