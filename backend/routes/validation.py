"""
Validation routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.database import get_db
from database.models import ValidationJob, Provider
from models.schemas import ValidationJobRequest, ValidationJobResponse, ProviderListResponse, ProviderResponse
from tasks.validation_task import run_validation_job_async
import uuid

router = APIRouter()


@router.post("/start", response_model=ValidationJobResponse)
async def start_validation(
    request: ValidationJobRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start validation job"""
    job_id = request.job_id or str(uuid.uuid4())
    
    # Check if job exists
    result = await db.execute(
        select(ValidationJob).where(ValidationJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == "processing":
        raise HTTPException(status_code=400, detail="Job already processing")
    
    # Start background task
    background_tasks.add_task(run_validation_job_async, job_id)
    
    return ValidationJobResponse(
        job_id=job.job_id,
        status=job.status,
        total_providers=job.total_providers,
        processed_providers=job.processed_providers,
        progress_percentage=(job.processed_providers / job.total_providers * 100) if job.total_providers > 0 else 0.0,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error_message=job.error_message
    )


@router.get("/status/{job_id}", response_model=ValidationJobResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get validation job status"""
    result = await db.execute(
        select(ValidationJob).where(ValidationJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    progress = (job.processed_providers / job.total_providers * 100) if job.total_providers > 0 else 0.0
    
    return ValidationJobResponse(
        job_id=job.job_id,
        status=job.status,
        total_providers=job.total_providers,
        processed_providers=job.processed_providers,
        progress_percentage=progress,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error_message=job.error_message
    )


@router.get("/providers/{job_id}", response_model=ProviderListResponse)
async def get_providers(
    job_id: str,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get providers for a job"""
    # Get total count
    count_result = await db.execute(
        select(func.count(Provider.id)).where(Provider.job_id == job_id)
    )
    total = count_result.scalar()
    
    # Get providers with pagination
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Provider)
        .where(Provider.job_id == job_id)
        .offset(offset)
        .limit(page_size)
    )
    providers = result.scalars().all()
    
    return ProviderListResponse(
        providers=[ProviderResponse.model_validate(p) for p in providers],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/provider/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get single provider details"""
    result = await db.execute(
        select(Provider).where(Provider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return ProviderResponse.model_validate(provider)

