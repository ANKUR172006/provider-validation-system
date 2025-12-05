"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database.database import Base


class ValidationJob(Base):
    """Validation job tracking"""
    __tablename__ = "validation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    total_providers = Column(Integer, default=0)
    processed_providers = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    error_message = Column(Text, nullable=True)
    
    providers = relationship("Provider", back_populates="job")


class Provider(Base):
    """Provider data model"""
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("validation_jobs.job_id"))
    
    # Original data
    original_data = Column(JSON)  # Store original CSV/PDF data
    
    # Provider details
    npi = Column(String, index=True, nullable=True)
    name = Column(String, index=True)
    specialty = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    website = Column(String, nullable=True)
    
    # Validated data
    validated_name = Column(String, nullable=True)
    validated_phone = Column(String, nullable=True)
    validated_address = Column(String, nullable=True)
    validated_specialty = Column(String, nullable=True)
    validated_email = Column(String, nullable=True)
    validated_website = Column(String, nullable=True)
    
    # Enrichment data
    enriched_data = Column(JSON, nullable=True)
    
    # Confidence scores (0-1)
    confidence_name = Column(Float, default=0.0)
    confidence_phone = Column(Float, default=0.0)
    confidence_address = Column(Float, default=0.0)
    confidence_specialty = Column(Float, default=0.0)
    confidence_email = Column(Float, default=0.0)
    confidence_overall = Column(Float, default=0.0)
    
    # Flags
    needs_review = Column(Boolean, default=False)
    is_suspicious = Column(Boolean, default=False)
    is_validated = Column(Boolean, default=False)
    
    # Issues and notes
    issues = Column(JSON, nullable=True)  # List of issues found
    validation_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    job = relationship("ValidationJob", back_populates="providers")


class ValidationLog(Base):
    """Validation process logs"""
    __tablename__ = "validation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    agent_name = Column(String)  # validation, enrichment, qa, directory
    action = Column(String)
    result = Column(JSON)
    timestamp = Column(DateTime, default=func.now())


