"""
main.py

Main FastAPI application: applicant/loan application submission,
retrieval, and admin review endpoints.

Run locally with:
    uvicorn main:app --reload --port 8000
"""

import uuid

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db
from ml_client import get_default_prediction

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credit Scoring Backend", version="0.1.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/applications", response_model=schemas.ApplicationOut, status_code=201)
def submit_application(payload: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    """
    Submit a new loan application:
    1. Create (or reuse) the applicant record
    2. Create the application record
    3. Call ml-service for a risk prediction
    4. Store the prediction alongside the application
    """
    # Look up existing applicant by email, or create a new one
    applicant = (
        db.query(models.Applicant)
        .filter(models.Applicant.email == payload.applicant.email)
        .first()
    )
    if applicant is None:
        applicant = models.Applicant(**payload.applicant.dict())
        db.add(applicant)
        db.commit()
        db.refresh(applicant)

    application_fields = payload.dict(exclude={"applicant"})
    application = models.Application(applicant_id=applicant.id, **application_fields)
    db.add(application)
    db.commit()
    db.refresh(application)

    # Call ml-service for a risk prediction. If it's unreachable, the
    # application is still saved - it just won't have a prediction yet.
    try:
        ml_input = {
            k: v
            for k, v in application_fields.items()
            if v is not None
        }
        prediction_result = get_default_prediction(ml_input)

        prediction = models.Prediction(
            application_id=application.id,
            default_probability=prediction_result["default_probability"],
            risk_flag_no_installment_history=str(
                prediction_result.get("risk_flag_no_installment_history")
            ),
        )
        db.add(prediction)
        db.commit()
        db.refresh(application)

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        # Don't fail the whole application submission if ml-service is down -
        # log and let an admin trigger scoring later if needed.
        print(f"Warning: ml-service call failed: {e}")

    return application


@app.get("/applications", response_model=list[schemas.ApplicationOut])
def list_applications(db: Session = Depends(get_db)):
    """Return all submitted applications, most recent first."""
    return (
        db.query(models.Application)
        .order_by(models.Application.submitted_at.desc())
        .all()
    )


@app.get("/applications/{application_id}", response_model=schemas.ApplicationOut)
def get_application(application_id: uuid.UUID, db: Session = Depends(get_db)):
    application = (
        db.query(models.Application)
        .filter(models.Application.id == application_id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.post(
    "/applications/{application_id}/review",
    response_model=schemas.ReviewOut,
    status_code=201,
)
def review_application(
    application_id: uuid.UUID, payload: schemas.ReviewCreate, db: Session = Depends(get_db)
):
    """Admin submits a decision on an application."""
    application = (
        db.query(models.Application)
        .filter(models.Application.id == application_id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    review = models.AdminReview(application_id=application_id, **payload.dict())
    db.add(review)

    application.status = payload.decision
    db.add(application)

    db.commit()
    db.refresh(review)

    return review


@app.get("/health")
def health_check():
    return {"status": "ok"}
