"""
Customer Data Generator

This module generates realistic banking customer data
for the Banking ETL Pipeline project.
"""

import random
import string
from pathlib import Path
import pandas as pd
from faker import Faker

# Create Faker instance for Indian locale
fake = Faker("en_IN")


def generate_customer_id(customer_number: int) -> str:
    """
    Generate a unique customer ID.

    Example:
        1 -> CUST000001
    """
    return f"CUST{customer_number:06d}"


def generate_pan_number(last_name: str, status: str = "P") -> str:
    """
    Generate a realistic PAN number.

    Args:
        last_name (str): Customer's last name.
        status (str): PAN holder type.

    Returns:
        str: Generated PAN number.
    """
    # 1. Generate first 3 random uppercase letters
    first_three = "".join(random.choices(string.ascii_uppercase, k=3))

    # 2. Holder status (forced uppercase)
    holder_status = status.upper()[0]

    # 3. First letter of last name (forced uppercase)
    # Uses 'X' as a fallback if the provided string is empty
    name_char = last_name.strip().upper()[0] if last_name.strip() else "X"

    # 4. Generate random 4-digit sequential number
    digits = f"{random.randint(1, 9999):04d}"

    # 5. Generate final alphabetic check digit
    check_digit = random.choice(string.ascii_uppercase)

    # Combine all parts into the final PAN string
    pan = f"{first_three}{holder_status}{name_char}{digits}{check_digit}"
    return pan


def generate_masked_aadhaar() -> str:
    """
    Generate a masked Aadhaar number.

    Returns:
        str: A masked Aadhaar number.
    """
    return f"XXXX-XXXX-{random.randint(0, 9999):04d}"


def generate_customer(customer_number: int) -> dict:
    """
    Generate a realistic customer profile.

    Args:
        customer_number (int): The sequential number of the customer.

    Returns:
        dict: A dictionary containing customer details.
    """
    customer_id = generate_customer_id(customer_number)
    gender = random.choice(["Male", "Female"])
    if gender == "Male":
        first_name = fake.first_name_male()
    else:
        first_name = fake.first_name_female()
    last_name = fake.last_name()
    date_of_birth = fake.date_of_birth(
        minimum_age=18, maximum_age=70).strftime("%Y-%m-%d")
    email = fake.email()
    phone_number = fake.phone_number()
    pan_number = generate_pan_number(last_name=last_name)
    aadhaar_number = generate_masked_aadhaar()
    city = fake.city()
    state = fake.state()
    created_date = fake.date_this_decade().strftime("%Y-%m-%d")

    return {
        "customer_id": customer_id,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "date_of_birth": date_of_birth,
        "email": email,
        "phone_number": phone_number,
        "pan_number": pan_number,
        "aadhaar_number": aadhaar_number,
        "city": city,
        "state": state,
        "created_date": created_date
    }


def generate_customers(count: int) -> list[dict]:
    """
    Generate a list of realistic customer profiles.

    Args:
        count (int): The number of customers to generate.

    Returns:
        list: A list of dictionaries containing customer details.
    """
    return [generate_customer(i) for i in range(1, count + 1)]


def save_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
    Save a DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str): Destination CSV file path.
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)


def main():
    """Entry point of the application."""

    customers = generate_customers(1000)  # Generate 1000 customers
    customers_df = pd.DataFrame(customers)
    save_to_csv(customers_df, "data/raw/customers.csv")
    print(f"Generated {len(customers_df)} customers.")
    print("Saved to data/raw/customers.csv")


if __name__ == "__main__":
    main()
