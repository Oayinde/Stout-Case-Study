import numpy as np
import pandas as pd

# Load the dataset
df = pd.read_csv("casestudy.csv")

# Total revenue per year
total_rev_per_year = df.groupby('year')['net_revenue'].sum().reset_index()

# Identify new customers
df['prev_year_customers'] = df.groupby('customer_email')['year'].shift(1)
df['new_customer'] = np.where(df['prev_year_customers'].isna(), True, False)
new_customer_revenue = df[df['new_customer'] == True].groupby('year')['net_revenue'].sum().reset_index()

# Calculate revenue from previous year
df['prev_year_rev'] = df.groupby('customer_email')['net_revenue'].shift(1)

# Existing customer revenue for the current year
existing_customer_rev_current_year = df[df['new_customer'] == False].groupby('year')['net_revenue'].sum().reset_index()

# Existing customer revenue for the prior year
existing_customer_rev_prior_year = df[df['new_customer'] == False].groupby('year')['prev_year_rev'].sum().reset_index()

# Calculate existing customer growth
existing_customer_growth = existing_customer_rev_current_year.copy()
existing_customer_growth['growth'] = existing_customer_growth['net_revenue'] - existing_customer_rev_prior_year['prev_year_rev'].fillna(0)

# Identify attrited customers (Customers who were present this year but not the next year)
df['next_year_customers'] = df.groupby('customer_email')['year'].shift(-1)
df['attrited_customer'] = np.where(df['next_year_customers'].isna(), True, False)

# Calculate revenue of attrited customers in their last year of purchase
attrited_customer_rev = df[df['attrited_customer'] == True].groupby('year')['net_revenue'].sum().reset_index()

# Shift the attrited customer revenue to align the lost revenue with the following year
attrited_customer_rev['lost_rev'] = attrited_customer_rev['net_revenue'].shift(-1)

# Drop the 'net_revenue' column as it is not needed anymore
attrited_customer_rev = attrited_customer_rev[['year', 'lost_rev']].fillna(0)

# Ensure that the 'lost_rev' for the final year is NaN since we cannot lose revenue in the final year
attrited_customer_rev.loc[attrited_customer_rev.index[-1], 'lost_rev'] = 0

# Total customers current year
total_customers_current_year = df.groupby('year')['customer_email'].nunique().reset_index()
total_customers_current_year.columns = ['year', 'total_customers']

# Total customers previous year
df['prev_year_customers_count'] = df.groupby('customer_email')['customer_email'].shift(1)
total_customers_previous_year = df[df['prev_year_customers_count'].notna()].groupby('year')['customer_email'].nunique().reset_index()
total_customers_previous_year.columns = ['year', 'total_customers_previous_year']

# New customers count
new_customers = df[df['new_customer'] == True].groupby('year')['customer_email'].nunique().reset_index()
new_customers.columns = ['year', 'new_customers']

# Identify customers who appear in the current year but not in the next year
df['is_lost_customer'] = df['customer_email'].isin(df[df['next_year_customers'].isna()]['customer_email'])

# Count the lost customers per year
lost_customers = df[df['is_lost_customer']].groupby('year')['customer_email'].nunique().reset_index()
lost_customers.columns = ['year', 'lost_customers']

# Merge all data into a summary DataFrame
summary_df = pd.merge(total_rev_per_year, new_customer_revenue, on='year', how='left')
summary_df = pd.merge(summary_df, existing_customer_rev_current_year, on='year', how='left')
summary_df = pd.merge(summary_df, existing_customer_rev_prior_year[['year', 'prev_year_rev']], on='year', how='left')
summary_df = pd.merge(summary_df, existing_customer_growth[['year', 'growth']], on='year', how='left')
summary_df = pd.merge(summary_df, attrited_customer_rev, on='year', how='left')
summary_df = pd.merge(summary_df, total_customers_current_year, on='year', how='left')
summary_df = pd.merge(summary_df, total_customers_previous_year, on='year', how='left')
summary_df = pd.merge(summary_df, new_customers, on='year', how='left')
summary_df = pd.merge(summary_df, lost_customers, on='year', how='left')

# Rename columns for clarity
summary_df.columns = ['Year', 'Total Revenue', 'New Customer Revenue', 'Existing Customer Revenue Current Year',
                      'Existing Customer Revenue Prior Year', 'Existing Customer Growth', 'Revenue Lost from Attrition',
                      'Total Customers Current Year', 'Total Customers Previous Year', 'New Customers', 'Lost Customers']

# Display the summary DataFrame
print(summary_df)

# Optionally, save the summary DataFrame to a CSV file
summary_df.to_csv('summary_data.csv', index=False)
