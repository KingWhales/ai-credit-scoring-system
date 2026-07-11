"""
predict.py

Loads the saved model pipeline and generates predictions for new
applicant data. This is the module the future ml-service API will
import and call.
"""

from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "xgb_credit_model.pkl"

_pipeline = None  # loaded lazily, cached after first load


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. Run train.py first."
            )
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


def predict_default_probability(applicant_data: pd.DataFrame) -> pd.Series:
    """
    Predict probability of default for one or more applicants.

    Args:
        applicant_data: DataFrame with the same feature columns used
            during training (already feature-engineered — see
            feature_engineering.run_full_feature_pipeline).

    Returns:
        Series of predicted default probabilities, indexed the same
        as the input.
    """
    pipeline = _get_pipeline()
    probabilities = pipeline.predict_proba(applicant_data)[:, 1]
    return pd.Series(probabilities, index=applicant_data.index, name="default_probability")


def predict_default_label(applicant_data: pd.DataFrame, threshold: float = 0.5) -> pd.Series:
    """
    Predict binary default label based on a probability threshold.
    Threshold is configurable so the eventual admin platform can
    expose it as an adjustable risk policy setting rather than a
    hardcoded value.
    """
    probabilities = predict_default_probability(applicant_data)
    return (probabilities >= threshold).astype(int).rename("predicted_default")
