"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class UploadResponse(BaseModel):
    """Response for file upload"""
    message: str
    file_id: str
    filename: str


class ValidationJobRequest(BaseModel):
    """Request to start validation"""
    job_id: Optional[str] = None
    file_ids: List[str] = []


class ValidationJobResponse(BaseModel):
    """Validation job status response"""
    job_id: str
    status: str
    total_providers: int
    processed_providers: int
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class ProviderResponse(BaseModel):
    """Provider data response"""
    id: int
    job_id: str
    npi: Optional[str]
    name: str
    specialty: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    website: Optional[str]
    
    # Validated fields
    validated_name: Optional[str]
    validated_phone: Optional[str]
    validated_address: Optional[str]
    validated_specialty: Optional[str]
    validated_email: Optional[str]
    validated_website: Optional[str]
    
    # Confidence scores
    confidence_name: float
    confidence_phone: float
    confidence_address: float
    confidence_specialty: float
    confidence_email: float
    confidence_overall: float
    
    # Flags
    needs_review: bool
    is_suspicious: bool
    is_validated: bool
    
    # Issues
    issues: Optional[List[str]]
    validation_notes: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProviderListResponse(BaseModel):
    """List of providers with pagination"""
    providers: List[ProviderResponse]
    total: int
    page: int
    page_size: int


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics"""
    total_providers: int
    auto_validated: int
    needs_review: int
    suspicious: int
    average_confidence: float
    validation_status: Dict[str, int]
    specialty_distribution: Dict[str, int]
    state_distribution: Dict[str, int]


class EmailTemplateRequest(BaseModel):
    """Request to generate email template"""
    provider_id: int
    template_type: str = "review_request"  # review_request, issue_notification, etc.


class EmailTemplateResponse(BaseModel):
    """Generated email template"""
    provider_id: int
    provider_name: str
    subject: str
    body: str
    issues: List[str]


class DownloadResultsResponse(BaseModel):
    """Response for download results"""
    message: str
    download_url: str
    filename: str


