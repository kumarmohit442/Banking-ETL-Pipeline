"""
Bronze Layer ETL Pipeline

This module processes raw banking datasets and creates the Bronze layer.

The pipeline performs the following steps:
1. Read raw CSV files.
2. Validate the schema.
3. Standardize data types.
4. Remove duplicate records.
5. Add audit columns.
6. Save the processed data to the Bronze layer.

Datasets processed:
- Customers
- Accounts
- Branches
- Transactions
"""

from pathlib import Path
import pandas as pd


def read_data(file_path: str) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.
    """
    return pd.read_csv(file_path)


def validate_schema(df: pd.DataFrame, expected_columns: list[str]) -> None:
    """
    Validate that all required columns exist.
    """

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def standardize_dtypes(
    df: pd.DataFrame,
    dtype_mapping: dict
) -> pd.DataFrame:
    """
    Convert columns to the required data types.
    """

    for column, dtype in dtype_mapping.items():
        if column in df.columns:
            df[column] = df[column].astype(dtype)

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows.
    """
    return df.drop_duplicates()


def add_audit_columns(
    df: pd.DataFrame,
    source_file: str
) -> pd.DataFrame:
    """
    Add audit columns.
    """

    df["ingestion_timestamp"] = pd.Timestamp.now(tz="UTC")
    df["source_file"] = source_file

    return df


def save_data(
    df: pd.DataFrame,
    output_path: str
) -> None:
    """
    Save DataFrame to CSV.
    """

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(output_path, index=False)


def process_dataset(
    input_path: str,
    output_path: str,
    expected_columns: list[str],
    dtype_mapping: dict
) -> None:
    """
    Execute the Bronze ETL pipeline.
    """

    df = read_data(input_path)

    validate_schema(df, expected_columns)

    df = standardize_dtypes(df, dtype_mapping)

    df = remove_duplicates(df)

    source_file = Path(input_path).name

    df = add_audit_columns(df, source_file)

    save_data(df, output_path)


DATASETS = {
    "customers": {
        "input_path": "data/raw/customers.csv",
        "output_path": "data/bronze/customers.csv",
        "expected_columns": [
            "customer_id",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "email",
            "phone_number",
            "pan_number",
            "aadhaar_number",
            "city",
            "state",
            "created_date"
        ],
        "dtype_mapping": {
            "customer_id": "string",
            "first_name": "string",
            "last_name": "string",
            "gender": "string",
            "date_of_birth": "string",
            "email": "string",
            "phone_number": "string",
            "pan_number": "string",
            "aadhaar_number": "string",
            "city": "string",
            "state": "string",
            "created_date": "string"
        }
    },

    "accounts": {
        "input_path": "data/raw/accounts.csv",
        "output_path": "data/bronze/accounts.csv",
        "expected_columns": [
            "account_number",
            "customer_id",
            "account_type",
            "balance",
            "currency",
            "branch_id",
            "account_status",
            "opening_date"
        ],
        "dtype_mapping": {
            "account_number": "string",
            "customer_id": "string",
            "account_type": "string",
            "balance": "float64",
            "currency": "string",
            "branch_id": "string",
            "account_status": "string",
            "opening_date": "string"
        }
    },

    "branches": {
        "input_path": "data/raw/branches.csv",
        "output_path": "data/bronze/branches.csv",
        "expected_columns": [
            "branch_id",
            "branch_name",
            "city",
            "state",
            "ifsc_code",
            "branch_type",
            "opened_date"
        ],
        "dtype_mapping": {
            "branch_id": "string",
            "branch_name": "string",
            "city": "string",
            "state": "string",
            "ifsc_code": "string",
            "branch_type": "string",
            "opened_date": "string"
        }
    },

    "transactions": {
        "input_path": "data/raw/transactions.csv",
        "output_path": "data/bronze/transactions.csv",
        "expected_columns": [
            "transaction_id",
            "account_number",
            "amount",
            "transaction_type",
            "transaction_mode",
            "description",
            "transaction_date"
        ],
        "dtype_mapping": {
            "transaction_id": "string",
            "account_number": "string",
            "amount": "float64",
            "transaction_type": "string",
            "transaction_mode": "string",
            "description": "string",
            "transaction_date": "string"
        }
    }
}


def main():
    """
    Process all datasets and create Bronze layer.
    """

    for dataset_name, config in DATASETS.items():

        process_dataset(
            input_path=config["input_path"],
            output_path=config["output_path"],
            expected_columns=config["expected_columns"],
            dtype_mapping=config["dtype_mapping"]
        )

        print(f"✓ {dataset_name} processed successfully.")

    print("\n✓ Bronze layer created successfully.")


if __name__ == "__main__":
    main()
