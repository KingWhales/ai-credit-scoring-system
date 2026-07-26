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


def get_default_prediction(application_data: dict) -> dict:
    """
    Call the ml-service /predict endpoint with application data and
    return the parsed response.

    Args:
        application_data: dict of applicant/application fields matching
            the ml-service's ApplicantInput schema.

    Returns:
        dict with 'default_probability' and 'risk_flag_no_installment_history'.

    Raises:
        httpx.HTTPStatusError: if the ml-service returns a non-2xx response.
        httpx.RequestError: if the ml-service is unreachable.
    """
    response = httpx.post(
        f"{ML_SERVICE_URL}/predict",
        json=application_data,
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
