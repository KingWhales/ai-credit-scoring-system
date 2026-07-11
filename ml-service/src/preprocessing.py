"""
preprocessing.py

Builds the scikit-learn preprocessing pipeline (imputation, scaling,
encoding) used ahead of every model in this project.
"""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Columns intentionally excluded from the model feature set
NON_FEATURE_COLS = ["SK_ID_CURR", "TARGET"]


def get_feature_columns(df: pd.DataFrame) -> list:
    """Return all columns eligible to be used as model features."""
    return [col for col in df.columns if col not in NON_FEATURE_COLS]


def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """
    Build a ColumnTransformer that imputes and scales numeric features,
    and imputes and one-hot encodes categorical features.

    Args:
        df: DataFrame containing only feature columns (no ID/target)

    Returns:
        An unfitted ColumnTransformer.
    """
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    return preprocessor
