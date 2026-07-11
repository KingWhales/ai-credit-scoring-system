"""
feature_engineering.py

Data cleaning, anomaly handling, and behavioural feature engineering
for the credit scoring pipeline. Mirrors the logic developed and
validated in notebooks/01_eda.ipynb.
"""

import numpy as np
import pandas as pd

DAYS_EMPLOYED_PLACEHOLDER = 365243

BEHAVIORAL_COLS = [
    "avg_payment_delay",
    "std_payment_delay",
    "pct_late_payments",
    "avg_payment_diff",
    "std_payment_amount",
    "num_installments",
]


def fix_days_employed_anomaly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle the known DAYS_EMPLOYED placeholder value (365243), which
    represents pensioner/unemployed applicants rather than a genuine
    employment duration.

    Adds:
        IS_RETIRED_OR_UNEMPLOYED: binary flag
    Modifies:
        DAYS_EMPLOYED: placeholder replaced with NaN (proper numeric dtype)
    """
    df = df.copy()
    df["IS_RETIRED_OR_UNEMPLOYED"] = (
        df["DAYS_EMPLOYED"] == DAYS_EMPLOYED_PLACEHOLDER
    ).astype(int)

    df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(
        DAYS_EMPLOYED_PLACEHOLDER, np.nan
    )
    df["DAYS_EMPLOYED"] = pd.to_numeric(df["DAYS_EMPLOYED"], errors="coerce")

    return df


def add_derived_employment_income_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add employment tenure (years) and a simple income-per-tenure
    stability proxy. Requires fix_days_employed_anomaly() to have
    already been applied.
    """
    df = df.copy()
    df["DAYS_EMPLOYED_YEARS"] = -df["DAYS_EMPLOYED"] / 365
    df["INCOME_PER_EMPLOYED_YEAR"] = df["AMT_INCOME_TOTAL"] / (
        df["DAYS_EMPLOYED_YEARS"] + 1
    )
    return df


def log_transform_income(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply log1p transformation to AMT_INCOME_TOTAL to handle the
    extreme right-skewed outlier tail identified during EDA.
    """
    df = df.copy()
    df["AMT_INCOME_TOTAL_LOG"] = np.log1p(df["AMT_INCOME_TOTAL"])
    return df


def build_behavioral_features(df_installments: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate row-level installment payment data into per-applicant
    behavioural features (Objective 3).

    Args:
        df_installments: raw installments_payments.csv data

    Returns:
        One row per SK_ID_CURR with six behavioural features.
    """
    df = df_installments.copy()

    df["PAYMENT_DELAY_DAYS"] = df["DAYS_ENTRY_PAYMENT"] - df["DAYS_INSTALMENT"]
    df["PAYMENT_DIFF"] = df["AMT_PAYMENT"] - df["AMT_INSTALMENT"]

    features = (
        df.groupby("SK_ID_CURR")
        .agg(
            avg_payment_delay=("PAYMENT_DELAY_DAYS", "mean"),
            std_payment_delay=("PAYMENT_DELAY_DAYS", "std"),
            pct_late_payments=("PAYMENT_DELAY_DAYS", lambda x: (x > 0).mean()),
            avg_payment_diff=("PAYMENT_DIFF", "mean"),
            std_payment_amount=("AMT_INSTALMENT", "std"),
            num_installments=("SK_ID_CURR", "count"),
        )
        .reset_index()
    )

    return features


def merge_behavioral_features(
    df_applications: pd.DataFrame, df_behavioral: pd.DataFrame
) -> pd.DataFrame:
    """
    Left-join behavioural features onto the main application table,
    flagging and imputing applicants with no prior installment history.
    """
    df = df_applications.merge(df_behavioral, on="SK_ID_CURR", how="left")

    df["NO_INSTALLMENT_HISTORY"] = df["avg_payment_delay"].isnull().astype(int)
    df[BEHAVIORAL_COLS] = df[BEHAVIORAL_COLS].fillna(0)

    return df


def run_full_feature_pipeline(
    df_applications: pd.DataFrame, df_installments: pd.DataFrame
) -> pd.DataFrame:
    """
    Convenience function running the full cleaning + feature engineering
    sequence in the correct order, matching the notebook workflow.
    """
    df = fix_days_employed_anomaly(df_applications)
    df = add_derived_employment_income_features(df)
    df = log_transform_income(df)

    behavioral_features = build_behavioral_features(df_installments)
    df = merge_behavioral_features(df, behavioral_features)

    return df
