"""
data_loader.py

Handles loading raw CSV data for the credit scoring pipeline.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_application_data(split: str = "train") -> pd.DataFrame:
    """
    Load the main application table.

    Args:
        split: "train" or "test"

    Returns:
        DataFrame of application-level applicant data.
    """
    filename = f"application_{split}.csv"
    filepath = DATA_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"Expected data file not found: {filepath}. "
            f"Make sure the Kaggle dataset is downloaded into ml-service/data/."
        )

    return pd.read_csv(filepath)


def load_installments_data() -> pd.DataFrame:
    """
    Load the installment payments history table.

    Returns:
        DataFrame of one row per historical installment payment.
    """
    filepath = DATA_DIR / "installments_payments.csv"

    if not filepath.exists():
        raise FileNotFoundError(f"Expected data file not found: {filepath}")

    return pd.read_csv(filepath)
