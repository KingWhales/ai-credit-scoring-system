"""
api.py

FastAPI service exposing the trained credit default model for
predictions, including SHAP-based explanations. This is what the backend application calls internally
to score new loan applications.

Run locally with:
    uvicorn api:app --reload --port 8001
"""

from pathlib import Path
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).resolve().parent / "models" / "xgb_credit_model.pkl"
DAYS_EMPLOYED_PLACEHOLDER = 365243
TOP_N_FEATURES = 5

BEHAVIORAL_COLS = [
    "avg_payment_delay",
    "std_payment_delay",
    "pct_late_payments",
    "avg_payment_diff",
    "std_payment_amount",
    "num_installments",
]

app = FastAPI(title="Credit Scoring ML Service", version="0.2.0")

# Loaded once at startup
pipeline = None
expected_columns = None
explainer = None

@app.on_event("startup")
def load_model():
    global pipeline, expected_columns, explainer
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"No trained model found at {MODEL_PATH}. Run `python -m src.train` first."
        )
    pipeline = joblib.load(MODEL_PATH)

    preprocessor = pipeline.named_steps["preprocessor"]
    numeric_cols = preprocessor.transformers_[0][2]
    categorical_cols = preprocessor.transformers_[1][2]
    expected_columns = list(numeric_cols) + list(categorical_cols)

    classifier = pipeline.named_steps["classifier"]
    explainer = shap.TreeExplainer(classifier)

class ApplicantInput(BaseModel):
    """
    Core applicant fields collected at loan application time.
    Any field not provided is treated as missing and imputed the
    same way missing values were handled during training.
    """

    AMT_INCOME_TOTAL: Optional[float] = Field(None, description="Applicant's total income")
    AMT_CREDIT: Optional[float] = Field(None, description="Loan amount requested")
    AMT_ANNUITY: Optional[float] = Field(None, description="Loan annuity")
    AMT_GOODS_PRICE: Optional[float] = Field(None, description="Price of goods being financed")
    DAYS_BIRTH: Optional[int] = Field(None, description="Applicant age in days (negative)")
    DAYS_EMPLOYED: Optional[int] = Field(
        None, description="Days employed (negative); use 365243 if retired/unemployed"
    )
    CODE_GENDER: Optional[str] = Field(None, description="M or F")
    NAME_EDUCATION_TYPE: Optional[str] = None
    NAME_FAMILY_STATUS: Optional[str] = None
    NAME_INCOME_TYPE: Optional[str] = None
    FLAG_OWN_CAR: Optional[str] = Field(None, description="Y or N")
    FLAG_OWN_REALTY: Optional[str] = Field(None, description="Y or N")
    CNT_CHILDREN: Optional[int] = None
    EXT_SOURCE_1: Optional[float] = None
    EXT_SOURCE_2: Optional[float] = None
    EXT_SOURCE_3: Optional[float] = None


class FeatureContribution(BaseModel):
    feature: str
    value: Optional[str] = None
    contribution: float
    direction: str # "increases_risk" or "decreases_risk"

class PredictionResponse(BaseModel):
    default_probability: float
    risk_flag_no_installment_history: bool
    top_factors: List[FeatureContribution]


def build_feature_row(applicant: ApplicantInput) -> pd.DataFrame:
    """
    Construct a single-row DataFrame matching the exact column set
    the model's preprocessor expects, applying the same cleaning
    logic used during training.
    """
    # Start with all expected columns as NaN
    row = {col: np.nan for col in expected_columns}

    # Overlay provided applicant fields
    provided = applicant.dict(exclude_none=True)
    for key, value in provided.items():
        if key in row:
            row[key] = value

    df = pd.DataFrame([row])

    # Replicate DAYS_EMPLOYED anomaly handling
    is_retired = df["DAYS_EMPLOYED"].iloc[0] == DAYS_EMPLOYED_PLACEHOLDER
    df["IS_RETIRED_OR_UNEMPLOYED"] = int(is_retired) if "IS_RETIRED_OR_UNEMPLOYED" in df.columns else np.nan
    df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(DAYS_EMPLOYED_PLACEHOLDER, np.nan)
    df["DAYS_EMPLOYED"] = pd.to_numeric(df["DAYS_EMPLOYED"], errors="coerce")

    if "DAYS_EMPLOYED_YEARS" in df.columns:
        df["DAYS_EMPLOYED_YEARS"] = -df["DAYS_EMPLOYED"] / 365
    if "INCOME_PER_EMPLOYED_YEAR" in df.columns:
        df["INCOME_PER_EMPLOYED_YEAR"] = df["AMT_INCOME_TOTAL"] / (
            df.get("DAYS_EMPLOYED_YEARS", pd.Series([0])).fillna(0) + 1
        )
    if "AMT_INCOME_TOTAL_LOG" in df.columns and df["AMT_INCOME_TOTAL"].notna().all():
        df["AMT_INCOME_TOTAL_LOG"] = np.log1p(df["AMT_INCOME_TOTAL"])

    # No transaction history available for a brand new applicant -
    # default behavioural features to 0, matching training-time handling
    for col in BEHAVIORAL_COLS:
        if col in df.columns:
            df[col] = 0
    if "NO_INSTALLMENT_HISTORY" in df.columns:
        df["NO_INSTALLMENT_HISTORY"] = 1

    return df[expected_columns]


def compute_top_factors(feature_row: pd.DataFrame) -> List[FeatureContribution]:
    """
    Compute SHAP values for a single applicant and return the top N
    features by absolute contribution, in a format suitable for
    display in the admin dashboard.
    """
    preprocessor = pipeline.named_steps["preprocessor"]
    transformed = preprocessor.transform(feature_row)
 
    numeric_cols = preprocessor.transformers_[0][2]
    categorical_cols = preprocessor.transformers_[1][2]
    onehot_names = (
        preprocessor.named_transformers_["cat"]
        .named_steps["onehot"]
        .get_feature_names_out(categorical_cols)
        .tolist()
    )
    feature_names = list(numeric_cols) + onehot_names
 
    shap_values = explainer.shap_values(transformed)[0]
 
    contributions = list(zip(feature_names, shap_values, transformed[0]))
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)
 
    top_factors = []
    for name, contribution, value in contributions[:TOP_N_FEATURES]:
        top_factors.append(
            FeatureContribution(
                feature=name,
                value=str(round(value, 2)) if isinstance(value, (int, float)) else str(value),
                contribution=round(float(contribution), 4),
                direction="increases_risk" if contribution > 0 else "decreases_risk",
            )
        )
 
    return top_factors
 


@app.post("/predict", response_model=PredictionResponse)
def predict(applicant: ApplicantInput):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    feature_row = build_feature_row(applicant)
    probability = float(pipeline.predict_proba(feature_row)[0][1])
    top_factors = compute_top_factors(feature_row)

    return PredictionResponse(
        default_probability=round(probability, 4),
        risk_flag_no_installment_history=True,
        top_factors=top_factors,
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": pipeline is not None}
