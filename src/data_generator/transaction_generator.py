"""
Transaction Data Generator

This module generates realistic Transaction data Generator
for the Banking ETL Pipeline project.
"""
import random
import pandas as pd
from faker import Faker

fake = Faker("en_IN")

transaction_templates = [
    {
        "description": "Salary Credit",
        "type": "Credit",
        "mode": "NEFT",
        "min_amount": 30000,
        "max_amount": 150000
    },

    {
        "description": "ATM Withdrawal",
        "type": "Debit",
        "mode": "ATM",
        "min_amount": 1000,
        "max_amount": 50000
    },
    {
        "description": "Grocery",
        "type": "Debit",
        "mode": "UPI",
        "min_amount": 500,
        "max_amount": 20000
    },
    {
        "description": "Utility Bill Payment",
        "type": "Debit",
        "mode": "UPI",
        "min_amount": 100,
        "max_amount": 10000
    },
    {
        "description": "Online Shopping",
        "type": "Debit",
        "mode": "UPI",
        "min_amount": 500,
        "max_amount": 50000
    },
    {
        "description": "Restaurant Payment",
        "type": "Debit",
        "mode": "UPI",
        "min_amount": 500,
        "max_amount": 20000
    },
    {
        "description": "Loan EMI Payment",
        "type": "Debit",
        "mode": "NEFT",
        "min_amount": 5000,
        "max_amount": 100000
    },
    {
        "description": "Insurance Premium Payment",
        "type": "Debit",
        "mode": "NEFT",
        "min_amount": 1000,
        "max_amount": 50000
    },
    {
        "description": "Investment in Mutual Funds",
        "type": "Debit",
        "mode": "NEFT",
        "min_amount": 5000,
        "max_amount": 100000
    },
    {
        "description": "Cash Deposit",
        "type": "Credit",
        "mode": "Cash",
        "min_amount": 1000,
        "max_amount": 50000
    },
    {
        "description": "Interest Credit",
        "type": "Credit",
        "mode": "NEFT",
        "min_amount": 50,
        "max_amount": 5000
    },
    {
        "description": "Refund",
        "type": "Credit",
        "mode": "UPI",
        "min_amount": 100,
        "max_amount": 10000
    }
]


def generate_transaction_id(transaction_number: int) -> str:
    """
    Generate a unique transaction ID.

    Example:
        1 -> TXN000001
    """
    return f"TXN{transaction_number:06d}"


def generate_transaction(transaction_number: int, account_number: str) -> dict:
    """
        Generate a realistic Transaction.
        Args:
            transaction_number (int): The sequential number of the transaction.
            account_number (str): Account number associated with the transaction.
        Returns:
            dict: A dictionary containing transaction details.
    """

    transaction_id = generate_transaction_id(transaction_number)
    transaction = random.choice(transaction_templates)
    transaction_type = transaction["type"]
    transaction_mode = transaction["mode"]
    description = transaction["description"]
    amount = round(
        random.uniform(
            transaction["min_amount"],
            transaction["max_amount"]
        ),
        2
    )
    transaction_date = fake.date_time_between(
        start_date="-2y", end_date="now"
    ).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "transaction_id": transaction_id,
        "account_number": account_number,
        "amount": amount,
        "transaction_type": transaction_type,
        "transaction_mode": transaction_mode,
        "description": description,
        "transaction_date": transaction_date
    }


def generate_transactions(account_numbers: list[str]) -> list[dict]:
    """
Generate transactions for every account.

Args:
    account_numbers (list[str]): List of account numbers.

Returns:
    list[dict]: Generated transaction records.
"""
    transactions = []
    transaction_number = 1

    for account_number in account_numbers:

        number_of_transactions = random.choices(
            population=[10, 25, 50],
            weights=[20, 50, 30],
            k=1
        )[0]

        for _ in range(number_of_transactions):
            transactions.append(generate_transaction(
                transaction_number, account_number))
            transaction_number += 1
    return transactions


def save_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
        Save a DataFrame to a CSV file.

        Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str): Destination CSV file path.
    """
    df.to_csv(file_path, index=False)


def main():
    """
     Generate sample transactional data and save them to a CSV file.

     This function generates sample transaction records, writes them
     to data/raw/transactions.csv and prints a short summary.
    """
    accounts_df = pd.read_csv("data/raw/accounts.csv")

    account_numbers = accounts_df["account_number"].tolist()

    transactions = generate_transactions(
        account_numbers)  # Generate transactions
    transactions_df = pd.DataFrame(transactions)
    save_to_csv(transactions_df, "data/raw/transactions.csv")
    print(f"Generated {len(transactions_df)} transactions.")
    print("Saved to data/raw/transactions.csv")


if __name__ == "__main__":
    main()
