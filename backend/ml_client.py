"""
ml_client.py

Thin HTTP client for calling the ml-service prediction API from the
backend. Keeps the network call logic in one place, separate from
endpoint logic in main.py.
"""

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")

# Backend field names (lowercase, matching SQLAlchemy columns) -> 
# ml-service field names (uppercase, matching the original dataset schema
# that the model was trained on). These MUST stay in sync with
# ApplicantInput in ml-service/api.py.
FIELD_NAME_MAP = {
    "amt_income_total": "AMT_INCOME_TOTAL",
    "amt_credit": "AMT_CREDIT",
    "amt_annuity": "AMT_ANNUITY",
    "amt_goods_price": "AMT_GOODS_PRICE",
    "days_employed": "DAYS_EMPLOYED",
    "name_education_type": "NAME_EDUCATION_TYPE",
    "name_family_status": "NAME_FAMILY_STATUS",
    "name_income_type": "NAME_INCOME_TYPE",
    "flag_own_car": "FLAG_OWN_CAR",
    "flag_own_realty": "FLAG_OWN_REALTY",
    "cnt_children": "CNT_CHILDREN",
    "ext_source_1": "EXT_SOURCE_1",
    "ext_source_2": "EXT_SOURCE_2",
    "ext_source_3": "EXT_SOURCE_3",
}


def _translate_fields(application_data: dict) -> dict:
    """Convert backend field names to the field names ml-service expects."""
    translated = {}
    for key, value in application_data.items():
        mapped_key = FIELD_NAME_MAP.get(key, key)
        translated[mapped_key] = value
    return translated


def get_default_prediction(application_data: dict) -> dict:
    """
    Call the ml-service /predict endpoint with application data and
    return the parsed response.

    Args:
        application_data: dict of applicant/application fields using
            backend (lowercase) field names.

    Returns:
        dict with 'default_probability' and 'risk_flag_no_installment_history'.

    Raises:
        httpx.HTTPStatusError: if the ml-service returns a non-2xx response.
        httpx.RequestError: if the ml-service is unreachable.
    """
    payload = _translate_fields(application_data)

    response = httpx.post(
        f"{ML_SERVICE_URL}/predict",
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
