"""
train.py

Trains and evaluates the credit default prediction model.
Run directly as a script to reproduce the full pipeline end-to-end:

    python -m src.train
"""

from pathlib import Path

import joblib
import xgboost as xgb
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .data_loader import load_application_data, load_installments_data
from .feature_engineering import run_full_feature_pipeline
from .preprocessing import build_preprocessor, get_feature_columns

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "xgb_credit_model.pkl"


def train_and_evaluate():
    print("Loading data...")
    df_applications = load_application_data(split="train")
    df_installments = load_installments_data()

    print("Running feature engineering pipeline...")
    df = run_full_feature_pipeline(df_applications, df_installments)

    feature_cols = get_feature_columns(df)
    X = df[feature_cols]
    y = df["TARGET"]

    print(f"Feature count: {len(feature_cols)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor(X_train)

    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                xgb.XGBClassifier(
                    n_estimators=100,
                    scale_pos_weight=scale_pos_weight,
                    random_state=42,
                    eval_metric="logloss",
                ),
            ),
        ]
    )

    print("Training XGBoost model...")
    pipeline.fit(X_train, y_train)

    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = pipeline.predict(X_test)

    auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\nAUC-ROC: {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    return pipeline, X_test, y_test


if __name__ == "__main__":
    train_and_evaluate()
