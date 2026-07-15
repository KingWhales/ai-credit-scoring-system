"""
models.py

SQLAlchemy ORM models for the loan management platform.

Tables:
    applicants      - personal/demographic data of loan applicants
    applications     - individual loan requests submitted by applicants
    predictions       - ML model output (risk score) for a given application
    admin_reviews     - admin decisions made on applications
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("Application", back_populates="applicant")


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("applicants.id"), nullable=False)

    # Core fields sent to the ML service for scoring
    amt_income_total = Column(Float, nullable=True)
    amt_credit = Column(Float, nullable=True)
    amt_annuity = Column(Float, nullable=True)
    amt_goods_price = Column(Float, nullable=True)
    days_employed = Column(Integer, nullable=True)
    name_education_type = Column(String, nullable=True)
    name_family_status = Column(String, nullable=True)
    name_income_type = Column(String, nullable=True)
    flag_own_car = Column(String, nullable=True)
    flag_own_realty = Column(String, nullable=True)
    cnt_children = Column(Integer, nullable=True)
    ext_source_1 = Column(Float, nullable=True)
    ext_source_2 = Column(Float, nullable=True)
    ext_source_3 = Column(Float, nullable=True)

    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    applicant = relationship("Applicant", back_populates="applications")
    prediction = relationship("Prediction", back_populates="application", uselist=False)
    review = relationship("AdminReview", back_populates="application", uselist=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)

    default_probability = Column(Float, nullable=False)
    risk_flag_no_installment_history = Column(String, nullable=True)
    explanation_summary = Column(Text, nullable=True)  # human-readable SHAP summary
    predicted_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="prediction")


class AdminReview(Base):
    __tablename__ = "admin_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)

    reviewer_name = Column(String, nullable=True)
    decision = Column(Enum(ApplicationStatus), nullable=False)
    notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="review")
