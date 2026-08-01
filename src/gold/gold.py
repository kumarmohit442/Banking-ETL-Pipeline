"""
Gold Layer ETL Pipeline

This module processes Silver layer datasets and creates analytics-ready
Gold layer datasets for reporting and business intelligence.

The pipeline performs the following steps:
1. Read Silver layer datasets.
2. Join related datasets.
3. Aggregate business metrics.
4. Generate reporting tables.
5. Save Gold layer datasets.

Gold datasets:
- Customer Summary
- Account Summary
- Branch Summary
- Daily Transaction Summary
"""

from pathlib import Path
import pandas as pd


def read_data(file_path: str) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.
    """
    return pd.read_csv(file_path)


def create_customer_summary() -> None:
    """Create customer summary dataset.
    """
    customer_df = read_data("data/silver/customers.csv")
    accounts_df = read_data("data/silver/accounts.csv")
    transactions_df = read_data("data/silver/transactions.csv")

    customer_df["customer_name"] = (
        customer_df["first_name"] + " " + customer_df["last_name"]
    )

    transactions_with_accounts = transactions_df.merge(
        accounts_df,
        on="account_number",
        how="left"
    )

    # KPI 1: Total accounts per customer
    customer_accounts = (
        accounts_df
        .groupby("customer_id")["account_number"]
        .nunique()
        .reset_index(name="total_accounts")
    )

    # KPI 2: Total balance per customer
    customer_total_balance = (accounts_df
                              .groupby("customer_id")["balance"]
                              .sum()
                              .reset_index(name="total_balance"))

    # KPI 3: Total transactions per customer
    customer_total_transactions = (transactions_with_accounts
                                   .groupby("customer_id")["transaction_id"]
                                   .count()
                                   .reset_index(name="total_transactions"))

    # KPI 4 : Total credit amount per customer
    credit_df = transactions_with_accounts[
        transactions_with_accounts["transaction_type"] == "Credit"
    ]

    total_credit_amount = (credit_df
                           .groupby("customer_id")["amount"]
                           .sum()
                           .reset_index(name="total_credit_amount")
                           )
    # KPI 5: Total debit amount per customer
    debit_df = transactions_with_accounts[
        transactions_with_accounts["transaction_type"] == "Debit"
    ]

    total_debit_amount = (debit_df
                          .groupby("customer_id")["amount"]
                          .sum()
                          .reset_index(name="total_debit_amount")
                          )

    # Final Report
    customer_summary = (
        customer_df
        .merge(customer_accounts, on="customer_id", how="left")
        .merge(customer_total_balance, on="customer_id", how="left")
        .merge(customer_total_transactions, on="customer_id", how="left")
        .merge(total_credit_amount, on="customer_id", how="left")
        .merge(total_debit_amount, on="customer_id", how="left")
    )

    customer_summary = customer_summary.fillna({
        "total_accounts": 0,
        "total_balance": 0,
        "total_transactions": 0,
        "total_credit_amount": 0,
        "total_debit_amount": 0
    })

    customer_summary["total_accounts"] = (
        customer_summary["total_accounts"].astype(int)
    )

    customer_summary["total_transactions"] = (
        customer_summary["total_transactions"].astype(int)
    )

    customer_summary = customer_summary[
        [
            "customer_id",
            "customer_name",
            "total_accounts",
            "total_balance",
            "total_transactions",
            "total_credit_amount",
            "total_debit_amount"
        ]
    ]

    save_data(
        customer_summary,
        "data/gold/customer_summary.csv"
    )


def create_account_summary() -> None:
    """Create account summary dataset."""

    df_customers = read_data("data/silver/customers.csv")
    df_accounts = read_data("data/silver/accounts.csv")
    df_transactions = read_data("data/silver/transactions.csv")

    # KPI 1: Total transactions per account

    account_transactions = (
        df_transactions
        .groupby("account_number")["transaction_id"]
        .count()
        .reset_index(name="total_transactions")
    )

    # KPI 2: Total credit amount per account

    df_credit = df_transactions[df_transactions["transaction_type"] == "Credit"]
    df_debit = df_transactions[df_transactions["transaction_type"] == "Debit"]

    account_credit_amount = (
        df_credit
        .groupby("account_number")["amount"]
        .sum()
        .reset_index(name="total_credit_amount")
    )

    account_debit_amount = (
        df_debit
        .groupby("account_number")["amount"]
        .sum()
        .reset_index(name="total_debit_amount")
    )

    df_customers["customer_name"] = (
        df_customers["first_name"] + " " + df_customers["last_name"]
    )

    # Final Report
    account_summary = (
        df_accounts
        .merge(account_transactions, on="account_number", how="left")
        .merge(account_credit_amount, on="account_number", how="left")
        .merge(account_debit_amount, on="account_number", how="left")
        .merge(df_customers[["customer_id", "customer_name"]], on="customer_id", how="left")
    )

    account_summary = account_summary.fillna({
        "total_transactions": 0,
        "total_credit_amount": 0,
        "total_debit_amount": 0

    })
    account_summary["total_transactions"] = (
        account_summary["total_transactions"].astype(int)
    )

    account_summary = account_summary[
        [
            "account_number",
            "customer_name",
            "account_type",
            "branch_id",
            "balance",
            "total_transactions",
            "total_credit_amount",
            "total_debit_amount"
        ]
    ]
    save_data(
        account_summary,
        "data/gold/account_summary.csv"
    )


def create_branch_summary() -> None:
    """
    Create branch summary dataset.
    """

    df_branches = read_data("data/silver/branches.csv")
    df_accounts = read_data("data/silver/accounts.csv")
    df_transactions = read_data("data/silver/transactions.csv")

    # Join accounts with transactions
    transactions_with_accounts = df_transactions.merge(
        df_accounts,
        on="account_number",
        how="left"
    )

    # KPI 1: Total accounts per branch
    total_accounts = (
        df_accounts
        .groupby("branch_id")["account_number"]
        .nunique()
        .reset_index(name="total_accounts")
    )

    # KPI 2: Total balance per branch
    total_balance = (
        df_accounts
        .groupby("branch_id")["balance"]
        .sum()
        .reset_index(name="total_balance")
    )

    # KPI 3: Total transactions per branch
    total_transactions = (
        transactions_with_accounts
        .groupby("branch_id")["transaction_id"]
        .count()
        .reset_index(name="total_transactions")
    )

    # KPI 4: Total credit amount per branch
    credit_df = transactions_with_accounts[
        transactions_with_accounts["transaction_type"] == "Credit"
    ]

    total_credit_amount = (
        credit_df
        .groupby("branch_id")["amount"]
        .sum()
        .reset_index(name="total_credit_amount")
    )

    # KPI 5: Total debit amount per branch
    debit_df = transactions_with_accounts[
        transactions_with_accounts["transaction_type"] == "Debit"
    ]

    total_debit_amount = (
        debit_df
        .groupby("branch_id")["amount"]
        .sum()
        .reset_index(name="total_debit_amount")
    )

    # Final Report
    branch_summary = (
        df_branches
        .merge(total_accounts, on="branch_id", how="left")
        .merge(total_balance, on="branch_id", how="left")
        .merge(total_transactions, on="branch_id", how="left")
        .merge(total_credit_amount, on="branch_id", how="left")
        .merge(total_debit_amount, on="branch_id", how="left")
    )

    branch_summary = branch_summary.fillna({
        "total_accounts": 0,
        "total_balance": 0,
        "total_transactions": 0,
        "total_credit_amount": 0,
        "total_debit_amount": 0
    })

    branch_summary["total_accounts"] = (
        branch_summary["total_accounts"].astype(int)
    )

    branch_summary["total_transactions"] = (
        branch_summary["total_transactions"].astype(int)
    )

    branch_summary = branch_summary[
        [
            "branch_id",
            "branch_name",
            "city",
            "state",
            "total_accounts",
            "total_balance",
            "total_transactions",
            "total_credit_amount",
            "total_debit_amount"
        ]
    ]

    save_data(
        branch_summary,
        "data/gold/branch_summary.csv"
    )


def create_daily_transaction_summary() -> None:
    """
    Create daily transaction dataset.
    """
    transactions_df = read_data("data/silver/transactions.csv")

    # KPI 1: Total transactions per day
    daily_transactions = (
        transactions_df
        .groupby("transaction_date")["transaction_id"]
        .count()
        .reset_index(name="total_transactions"))

    daily_credits = (
        transactions_df[transactions_df["transaction_type"] == "Credit"]
        .groupby("transaction_date")["amount"]
        .sum()
        .reset_index(name="total_credit_amount")
    )

    daily_debits = (
        transactions_df[transactions_df["transaction_type"] == "Debit"]
        .groupby("transaction_date")["amount"]
        .sum()
        .reset_index(name="total_debit_amount")
    )

    total_amount = (
        transactions_df
        .groupby("transaction_date")["amount"]
        .sum()
        .reset_index(name="total_amount"))

    transactions_summary = (
        daily_transactions
        .merge(daily_credits, on="transaction_date", how="left")
        .merge(daily_debits, on="transaction_date", how="left")
        .merge(total_amount, on="transaction_date", how="left")
    )

    transactions_summary = transactions_summary.fillna({
        "total_credit_amount": 0,
        "total_debit_amount": 0,
        "total_amount": 0
    })
    transactions_summary["total_transactions"] = (
        transactions_summary["total_transactions"].astype(int)
    )

    transactions_summary = transactions_summary[
        [
            "transaction_date",
            "total_transactions",
            "total_credit_amount",
            "total_debit_amount",
            "total_amount"
        ]
    ]

    transactions_summary = transactions_summary.sort_values(
        "transaction_date"
    )

    save_data(transactions_summary, "data/gold/daily_transaction_summary.csv")


def save_data(df: pd.DataFrame, output_path: str) -> None:
    """
    save a dataframe to a CSV file.
    """
    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )
    df.to_csv(output_path, index=False)


def main() -> None:
    """
    Process all datasets and create Gold layer. 
    """

    create_customer_summary()

    create_account_summary()

    create_branch_summary()

    create_daily_transaction_summary()


if __name__ == "__main__":
    main()
