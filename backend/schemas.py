"""
schemas.py

Pydantic schemas defining the shape of API requests and responses.
Kept separate from models.py (SQLAlchemy) since API contracts and
database structure don't always need to evolve in lockstep.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from models import ApplicationStatus


class ApplicantCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None


class ApplicationCreate(BaseModel):
    applicant: ApplicantCreate

    amt_income_total: Optional[float] = None
    amt_credit: Optional[float] = None
    amt_annuity: Optional[float] = None
    amt_goods_price: Optional[float] = None
    days_employed: Optional[int] = None
    name_education_type: Optional[str] = None
    name_family_status: Optional[str] = None
    name_income_type: Optional[str] = None
    flag_own_car: Optional[str] = None
    flag_own_realty: Optional[str] = None
    cnt_children: Optional[int] = None
    ext_source_1: Optional[float] = None
    ext_source_2: Optional[float] = None
    ext_source_3: Optional[float] = None


class PredictionOut(BaseModel):
    default_probability: float
    predicted_at: datetime

    class Config:
        from_attributes = True


class ApplicationOut(BaseModel):
    id: uuid.UUID
    applicant_id: uuid.UUID
    status: ApplicationStatus
    submitted_at: datetime
    amt_income_total: Optional[float]
    amt_credit: Optional[float]
    prediction: Optional[PredictionOut] = None

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    reviewer_name: Optional[str] = None
    decision: ApplicationStatus
    notes: Optional[str] = None


class ReviewOut(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    decision: ApplicationStatus
    reviewer_name: Optional[str]
    notes: Optional[str]
    reviewed_at: datetime

    class Config:
        from_attributes = True
