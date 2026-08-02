"""
Silver Layer ETL Pipeline

This module processes bronze layer banking datasets and creates the Silver layer.

The pipeline performs the following steps:
1. Read bronze layer CSV files.
2. Trim whitespace.
3. Validate business rules.
4. Handle missing Values.
5. Add audit columns.
6. Save the processed data to the Silver layer.

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


def trim_whitespace(df: pd.DataFrame
                    ) -> pd.DataFrame:
    """
        Remove leading and trailing whitespace from text columns.
    """
    text_columns = df.select_dtypes(include=["string", "object"]).columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    return df


def standardize_text(df: pd.DataFrame
                     ) -> pd.DataFrame:
    """
    Make First charater to Upper case and rest to lower
    For upi make every column as UPI
    eg:
    mohit → Mohit
    BANGALORE → Bangalore
    upi → UPI
    savings → Savings
    """
    if "first_name" in df.columns:
        df["first_name"] = df["first_name"].str.title()

    if "last_name" in df.columns:
        df["last_name"] = df["last_name"].str.title()

    if "city" in df.columns:
        df["city"] = df["city"].str.title()

    if "state" in df.columns:
        df["state"] = df["state"].str.title()

    if "email" in df.columns:
        df["email"] = df["email"].str.lower()

    if "transaction_mode" in df.columns:
        df["transaction_mode"] = df["transaction_mode"].str.upper()

    if "ifsc_code" in df.columns:
        df["ifsc_code"] = df["ifsc_code"].str.upper()

    return df


def validate_business_rules(df: pd.DataFrame, dataset_name: str
                            ) -> pd.DataFrame:
    """
Apply dataset-specific business validations for the Silver layer.

Customers:
- Mandatory fields
- Email validation
- PAN validation
- Aadhaar validation
- Phone validation
- DOB validation

Accounts:
- Balance validation
- Account type validation
- Mandatory fields
- Currency check
- Account status validation
- Opening date validation

Branches:
- Mandatory fields
- IFSC validation
- Opening date validation

Transactions:
- Mandatory fields
- Amount validation
- Transaction type validation
- Transaction mode validation
- Transaction date validation
"""
    if dataset_name == "customers":
        print("Initial:", len(df))
        # valid customer_id,first_name,last_name
        df = df.dropna(
            subset=[
                "customer_id",
                "first_name",
                "last_name"
            ]
        )
        print("After mandatory:", len(df))

        # Valid Email
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        df = df[
            df["email"].str.match(
                email_pattern,
                na=False
            )
        ]
        print("After email:", len(df))

        # Valid Phone Number (10 digits)
        df["phone_number"] = df["phone_number"].astype(str)

        phone_pattern = r"^\d{10,12}$"

        df = df[
            df["phone_number"].str.match(
                phone_pattern,
                na=False
            )
        ]
        print("After phone:", len(df))

        # Valid PAN Number
        pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        df = df[
            df["pan_number"].str.match(
                pan_pattern,
                na=False
            )
        ]
        print("After PAN:", len(df))

        # Valid Aadhaar Number (12 digits)
        df["aadhaar_number"] = df["aadhaar_number"].astype(str)
        aadhaar_pattern = r"^X{4}-X{4}-\d{4}$"

        df = df[
            df["aadhaar_number"].str.match(
                aadhaar_pattern,
                na=False
            )
        ]
        print("After aadhaar:", len(df))

        # Date of birth should not be in the future
        df["date_of_birth"] = pd.to_datetime(
            df["date_of_birth"],
            errors="coerce"
        )

        df = df[
            df["date_of_birth"] <= pd.Timestamp.today()
        ]
        print("After DOB:", len(df))

        # valid gender
        valid_gender = ["Male", "Female", "Other"]

        df = df[df["gender"].isin(valid_gender)]
        print("After gender:", len(df))

        return df

    elif dataset_name == "accounts":

        # Mandatory fields
        df = df.dropna(
            subset=[
                "account_number",
                "customer_id"
            ]
        )

        # Balance should not be negative
        df = df[df["balance"] >= 0]

        # Valid account types
        valid_account_types = [
            "Savings",
            "Current",
            "Salary",
            "Fixed Deposit"
        ]

        df = df[df["account_type"].isin(valid_account_types)]

        # Currency should be INR
        df = df[df["currency"] == "INR"]

        # Valid account status
        valid_status = [
            "Active",
            "Inactive",
            "Closed"
        ]

        df = df[df["account_status"].isin(valid_status)]

        # Opening date should not be in the future
        df["opening_date"] = pd.to_datetime(
            df["opening_date"],
            errors="coerce"
        )

        df = df[
            df["opening_date"] <= pd.Timestamp.today()
        ]

        return df

    elif dataset_name == "branches":

        # Mandatory fields
        df = df.dropna(
            subset=[
                "branch_id",
                "branch_name"
            ]
        )
        print("After mandatory:", len(df))

        # Valid IFSC
        ifsc_pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"

        df = df[
            df["ifsc_code"].str.match(
                ifsc_pattern,
                na=False
            )
        ]
        print("After IFSC:", len(df))

        # Opened date should not be in the future
        df["opened_date"] = pd.to_datetime(
            df["opened_date"],
            errors="coerce"
        )

        df["opened_date"] = pd.to_datetime(df["opened_date"], errors="coerce")
        df = df[
            df["opened_date"] <= pd.Timestamp.today()
        ]
        print("After date:", len(df))

        return df
    elif dataset_name == "transactions":

        # Mandatory fields
        df = df.dropna(
            subset=[
                "transaction_id",
                "account_number"
            ]
        )

        # Amount should be greater than zero
        df = df[df["amount"] > 0]

        # Valid transaction type
        valid_types = [
            "Credit",
            "Debit"
        ]

        df = df[df["transaction_type"].isin(valid_types)]

        # Valid transaction mode
        valid_modes = [
            "UPI",
            "NEFT",
            "RTGS",
            "IMPS",
            "ATM",
            "CASH",
            "CHEQUE",
            "NET BANKING"
        ]

        df = df[df["transaction_mode"].isin(valid_modes)]

        # Transaction date should not be in the future
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"],
            errors="coerce"
        )

        df = df[
            df["transaction_date"] <= pd.Timestamp.today()
        ]

        return df

    return df


def handle_missing_values(df: pd.DataFrame, dataset_name: str
                          ) -> pd.DataFrame:
    """
    Handle Null values
    """
    if dataset_name == "customers":

        df["city"] = df["city"].fillna("Unknown")

        df["state"] = df["state"].fillna("Unknown")

        return df

    elif dataset_name == "accounts":

        df["currency"] = df["currency"].fillna("INR")

        df["account_status"] = df["account_status"].fillna("Active")

        return df

    elif dataset_name == "branches":

        df["city"] = df["city"].fillna("Unknown")

        df["state"] = df["state"].fillna("Unknown")

        return df

    elif dataset_name == "transactions":

        df["description"] = df["description"].fillna("No Description")

        return df

    return df


def add_audit_columns(df: pd.DataFrame, source_file: str) -> pd.DataFrame:
    """
    Add audit columns.
    """
    df["ingestion_timestamp"] = pd.Timestamp.now(tz="UTC")
    df["source_file"] = source_file

    return df


def save_data(df: pd.DataFrame, output_path: str) -> None:
    """
     Save DataFrame to CSV.
    """
    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(output_path, index=False)


def process_dataset(dataset_name: str,
                    input_path: str,
                    output_path: str) -> None:
    """
     Execute the Silver ETL pipeline.
    """
    df = read_data(input_path)

    df = trim_whitespace(df)

    df = standardize_text(df)

    df = validate_business_rules(df, dataset_name)

    df = handle_missing_values(df, dataset_name)

    source_file = Path(input_path).name

    df = add_audit_columns(df, source_file)

    save_data(df, output_path)


DATASETS = {
    "customers": {
        "input_path": "data/bronze/customers.csv",
        "output_path": "data/silver/customers.csv",
    },

    "accounts": {
        "input_path": "data/bronze/accounts.csv",
        "output_path": "data/silver/accounts.csv",

    },

    "branches": {
        "input_path": "data/bronze/branches.csv",
        "output_path": "data/silver/branches.csv",
    },

    "transactions": {
        "input_path": "data/bronze/transactions.csv",
        "output_path": "data/silver/transactions.csv",

    }
}


def main() -> None:
    """
    Process all datasets and create Silver layer.   
    """

    for dataset_name, config in DATASETS.items():
        process_dataset(dataset_name=dataset_name,
                        input_path=config["input_path"],
                        output_path=config["output_path"]
                        )


if __name__ == "__main__":
    main()
