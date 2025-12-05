"""
File upload routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
import os
from config import settings
from utils.file_handler import save_uploaded_file, read_csv_file, extract_pdf_text, parse_provider_from_text
from models.schemas import UploadResponse
from database.models import ValidationJob, Provider
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends

router = APIRouter()


@router.post("/csv", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload CSV file with provider data"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Read file content
    content = await file.read()
    
    # Save file
    file_path = await save_uploaded_file(content, file.filename, settings.UPLOAD_DIR)
    
    # Read CSV data
    providers_data = await read_csv_file(file_path)
    
    # Create validation job
    job_id = str(uuid.uuid4())
    job = ValidationJob(
        job_id=job_id,
        status="pending",
        total_providers=len(providers_data)
    )
    db.add(job)
    await db.flush()
    
    # Create provider records
    for provider_data in providers_data:
        provider = Provider(
            job_id=job_id,
            original_data=provider_data,
            name=provider_data.get("name", ""),
            npi=provider_data.get("npi"),
            specialty=provider_data.get("specialty"),
            phone=provider_data.get("phone"),
            email=provider_data.get("email"),
            address=provider_data.get("address"),
            city=provider_data.get("city"),
            state=provider_data.get("state"),
            zip_code=provider_data.get("zip_code"),
            website=provider_data.get("website")
        )
        db.add(provider)
    
    await db.commit()
    
    return UploadResponse(
        message="CSV uploaded successfully",
        file_id=job_id,
        filename=file.filename
    )


@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload PDF file with provider data"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Read file content
    content = await file.read()
    
    # Save file
    file_path = await save_uploaded_file(content, file.filename, settings.UPLOAD_DIR)
    
    # Extract text from PDF
    pdf_text = await extract_pdf_text(file_path)
    
    # Parse provider data from text
    provider_data = parse_provider_from_text(pdf_text)
    
    # Create validation job
    job_id = str(uuid.uuid4())
    job = ValidationJob(
        job_id=job_id,
        status="pending",
        total_providers=1
    )
    db.add(job)
    await db.flush()
    
    # Create provider record
    provider = Provider(
        job_id=job_id,
        original_data={"source": "pdf", "text": pdf_text},
        name=provider_data.get("name", ""),
        npi=provider_data.get("npi"),
        specialty=provider_data.get("specialty"),
        phone=provider_data.get("phone"),
        email=provider_data.get("email"),
        address=provider_data.get("address"),
        city=provider_data.get("city"),
        state=provider_data.get("state"),
        zip_code=provider_data.get("zip_code"),
        website=provider_data.get("website")
    )
    db.add(provider)
    await db.commit()
    
    return UploadResponse(
        message="PDF uploaded successfully",
        file_id=job_id,
        filename=file.filename
    )


