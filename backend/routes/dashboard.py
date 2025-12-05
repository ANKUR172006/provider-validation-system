"""
Dashboard routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from database.database import get_db
from database.models import Provider, ValidationJob
from models.schemas import DashboardStatsResponse, DownloadResultsResponse
from typing import Dict, Optional
import csv
import io
from fastapi.responses import Response

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    job_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics"""
    query = select(Provider)
    if job_id:
        query = query.where(Provider.job_id == job_id)
    
    result = await db.execute(query)
    providers = result.scalars().all()
    
    total_providers = len(providers)
    auto_validated = sum(1 for p in providers if p.is_validated)
    needs_review = sum(1 for p in providers if p.needs_review)
    suspicious = sum(1 for p in providers if p.is_suspicious)
    
    # Calculate average confidence
    confidences = [p.confidence_overall for p in providers if p.confidence_overall > 0]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    # Validation status distribution
    validation_status = {
        "validated": auto_validated,
        "needs_review": needs_review,
        "suspicious": suspicious,
        "pending": total_providers - auto_validated - needs_review
    }
    
    # Specialty distribution
    specialty_dist = {}
    for provider in providers:
        specialty = provider.specialty or provider.validated_specialty or "Unknown"
        specialty_dist[specialty] = specialty_dist.get(specialty, 0) + 1
    
    # State distribution
    state_dist = {}
    for provider in providers:
        state = provider.state or "Unknown"
        state_dist[state] = state_dist.get(state, 0) + 1
    
    return DashboardStatsResponse(
        total_providers=total_providers,
        auto_validated=auto_validated,
        needs_review=needs_review,
        suspicious=suspicious,
        average_confidence=avg_confidence,
        validation_status=validation_status,
        specialty_distribution=specialty_dist,
        state_distribution=state_dist
    )


@router.get("/download-results")
async def download_results(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download validation results as CSV"""
    result = await db.execute(
        select(Provider).where(Provider.job_id == job_id)
    )
    providers = result.scalars().all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "NPI", "Name", "Specialty", "Phone", "Email",
        "Address", "City", "State", "ZIP", "Website",
        "Validated Name", "Validated Phone", "Validated Address", "Validated Specialty",
        "Confidence Overall", "Confidence Name", "Confidence Phone", "Confidence Address",
        "Needs Review", "Is Suspicious", "Is Validated", "Issues"
    ])
    
    # Write data
    for provider in providers:
        writer.writerow([
            provider.id,
            provider.npi or "",
            provider.name or "",
            provider.specialty or "",
            provider.phone or "",
            provider.email or "",
            provider.address or "",
            provider.city or "",
            provider.state or "",
            provider.zip_code or "",
            provider.website or "",
            provider.validated_name or "",
            provider.validated_phone or "",
            provider.validated_address or "",
            provider.validated_specialty or "",
            provider.confidence_overall,
            provider.confidence_name,
            provider.confidence_phone,
            provider.confidence_address,
            provider.needs_review,
            provider.is_suspicious,
            provider.is_validated,
            "; ".join(provider.issues) if provider.issues else ""
        ])
    
    output.seek(0)
    
    csv_bytes = output.getvalue().encode('utf-8')
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=validation_results_{job_id}.csv"}
    )

