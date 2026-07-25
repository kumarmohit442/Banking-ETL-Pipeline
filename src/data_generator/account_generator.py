"""
Account Data Generator

This module generates realistic banking account data
for the Banking ETL Pipeline project.
"""
import random
import pandas as pd
from faker import Faker

# Create Faker instance for Indian locale
fake = Faker("en_IN")


def generate_account_number(account_number: int) -> str:
    """
        Generate a unique account number.

        Example:
            1 -> ACC000001
    """
    return f"ACC{account_number:08d}"


def generate_account(account_number: int, customer_id: str) -> dict:
    """
        Generate a realistic Account.

        Args:
            account_number (int): The sequential number of the account.
            customer_id (str): Customer ID to whom the account belongs.

        Returns:
            dict: A dictionary containing account details.
    """
    account_number_str = generate_account_number(account_number)

    account_type = random.choice(
        ["Savings", "Current", "Fixed Deposit"],
    )

    if account_type == "Savings":
        balance = round(random.uniform(1_000, 500_000), 2)

    elif account_type == "Current":
        balance = round(random.uniform(10_000, 2_000_000), 2)

    else:  # Fixed Deposit
        balance = round(random.uniform(50_000, 5_000_000), 2)

    currency = "INR"

    branch_id = f"BR{random.randint(1, 20):03d}"

    account_status = random.choices(
        population=["Active", "Dormant", "Closed"],
        weights=[90, 8, 2],
        k=1
    )[0]

    opening_date = fake.date_between(
        start_date="-10y", end_date="today").strftime("%Y-%m-%d")

    return {
        "account_number": account_number_str,
        "customer_id": customer_id,
        "account_type": account_type,
        "balance": balance,
        "currency": currency,
        "branch_id": branch_id,
        "account_status": account_status,
        "opening_date": opening_date
    }


def generate_accounts(customers_df: pd.DataFrame) -> list[dict]:
    """
    Generate accounts for every customer.

    Each customer gets:
        - 1 account (60%)
        - 2 accounts (30%)
        - 3 accounts (10%)

    Returns:
        list[dict]
    """

    accounts = []
    account_number = 1

    for customer_id in customers_df["customer_id"]:

        num_accounts = random.choices(
            population=[1, 2, 3],
            weights=[60, 30, 10],
            k=1
        )[0]

        for _ in range(num_accounts):

            account = generate_account(
                account_number,
                customer_id
            )

            accounts.append(account)

            account_number += 1

    return accounts


def save_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
        Save a DataFrame to a CSV file.

        Args:
            df (pd.DataFrame): DataFrame to save.
            file_path (str): Destination CSV file path.
    """
    df.to_csv(file_path, index=False)


def main():
    """Entry point of the application."""
    # read customer.csv to get customer_id for foreign key
    customers_df = pd.read_csv("data/raw/customers.csv")
    # Generate accounts
    accounts = generate_accounts(customers_df)
    # Convert to DataFrame and save
    accounts_df = pd.DataFrame(accounts)
    save_to_csv(accounts_df, "data/raw/accounts.csv")

    # print(accounts_df.head())
    # print(accounts_df.info())
    # print(accounts_df["account_type"].value_counts())
    # print(accounts_df["account_status"].value_counts())
    # print(accounts_df["account_number"].is_unique)
    # print(
    #   accounts_df["customer_id"].isin(
    #      customers_df["customer_id"]
    #   ).all()
    # )
    # print(
    #   accounts_df.groupby("customer_id")
    #  .size()
    # .describe()
    # )


if __name__ == "__main__":
    main()
