"""
Branch Data Generator

This module generates realistic branch data
for the Banking ETL Pipeline project.
"""

# from data_generator.customer_generator import generate_customers
import random
import pandas as pd
from faker import Faker

fake = Faker("en_IN")


def generate_branch_id(branch_number: int) -> str:
    """
    Generate a unique branch ID.

    Example:
        1 -> BR001
    """
    return f"BR{branch_number:03d}"


def generate_branch(branch_number: int) -> dict:
    """
    Generate a realistic Branch.
    """
    branch_id = generate_branch_id(branch_number)
    city = fake.city()
    branch_name = f"{city} Branch"
    state = fake.state()
    bank_code = "Bank"
    ifsc_code = f"{bank_code}0{branch_number:06d}"
    branches_type = [
        "Metro",
        "Urban",
        "Semi-Urban",
        "Rural"
    ]
    branch_type = random.choices(
        population=branches_type,
        weights=[5, 20, 60, 15],
        k=1
    )[0]
    opened_date = fake.date_between(
        start_date="-30y",
        end_date="today"
    ).strftime("%Y-%m-%d")
    return {
        "branch_id": branch_id,
        "branch_name": branch_name,
        "city": city,
        "state": state,
        "ifsc_code": ifsc_code,
        "branch_type": branch_type,
        "opened_date": opened_date
    }


def generate_branches(num_branches: int) -> list[dict]:
    """
    Generate a list of branches."""

    return [generate_branch(i + 1) for i in range(num_branches)]


def save_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
        Save a DataFrame to a CSV file.

        Args:
            df (pd.DataFrame): DataFrame to save.
            file_path (str): Destination CSV file path.
    """
    df.to_csv(file_path, index=False)


def main():
    """Generate sample branches and save them to a CSV file.

    This function generates 20 sample branch records, writes them
    to data/raw/branches.csv and prints a short summary.
    """

    branches = generate_branches(20)  # Generate branches
    branches_df = pd.DataFrame(branches)
    save_to_csv(branches_df, "data/raw/branches.csv")
    print(f"Generated {len(branches_df)} branches.")
    print("Saved to data/raw/branches.csv")


if __name__ == "__main__":
    main()
