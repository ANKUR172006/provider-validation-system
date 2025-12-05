"""
Background task for provider validation pipeline
"""
import asyncio
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.database import AsyncSessionLocal
from database.models import ValidationJob, Provider
from agents.validation_agent import ValidationAgent
from agents.enrichment_agent import EnrichmentAgent
from agents.qa_agent import QAAgent
from agents.directory_agent import DirectoryAgent
from utils.confidence import calculate_overall_confidence


class ValidationPipeline:
    """Validation pipeline orchestrator"""
    
    def __init__(self):
        self.validation_agent = ValidationAgent()
        self.enrichment_agent = EnrichmentAgent()
        self.qa_agent = QAAgent()
        self.directory_agent = DirectoryAgent()
    
    async def process_provider(
        self,
        provider: Provider,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Process a single provider through the validation pipeline"""
        # Start with original data
        provider_data = provider.original_data.copy()
        provider_data.update({
            "id": provider.id,
            "job_id": provider.job_id,
            "name": provider.name,
            "npi": provider.npi,
            "specialty": provider.specialty,
            "phone": provider.phone,
            "email": provider.email,
            "address": provider.address,
            "city": provider.city,
            "state": provider.state,
            "zip_code": provider.zip_code,
            "website": provider.website
        })
        
        # Step 1: Enrichment (fill missing data)
        enrichment_result = await self.enrichment_agent.process(provider_data, session)
        if enrichment_result.get("enriched_data"):
            provider_data.update(enrichment_result["enriched_data"])
            # Update provider with enriched data
            for field, value in enrichment_result["enriched_data"].items():
                if hasattr(provider, field):
                    setattr(provider, field, value)
        
        # Step 2: Validation
        validation_result = await self.validation_agent.process(provider_data, session)
        provider_data.update(validation_result)
        
        # Update provider with validated data
        for key, value in validation_result.items():
            if hasattr(provider, key):
                setattr(provider, key, value)
        
        # Step 3: QA
        qa_result = await self.qa_agent.process(provider_data, session)
        provider_data.update(qa_result)
        
        # Update provider with QA results
        provider.needs_review = qa_result.get("needs_review", False)
        provider.is_suspicious = qa_result.get("is_suspicious", False)
        provider.issues = qa_result.get("issues", [])
        provider.validation_notes = qa_result.get("validation_notes", "")
        
        # Step 4: Directory Management
        directory_result = await self.directory_agent.process(provider_data, session)
        provider_data.update(directory_result)
        
        # Update provider with directory results
        provider.is_validated = directory_result.get("is_validated", False)
        
        # Calculate final overall confidence
        provider.confidence_overall = calculate_overall_confidence({
            "confidence_name": provider.confidence_name,
            "confidence_phone": provider.confidence_phone,
            "confidence_address": provider.confidence_address,
            "confidence_specialty": provider.confidence_specialty,
            "confidence_email": provider.confidence_email
        })
        
        await session.commit()
        
        return provider_data
    
    async def run_validation_job(self, job_id: str):
        """Run validation job for all providers"""
        async with AsyncSessionLocal() as session:
            # Get job
            result = await session.execute(
                select(ValidationJob).where(ValidationJob.job_id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                return
            
            # Update job status
            job.status = "processing"
            await session.commit()
            
            # Get all providers for this job
            result = await session.execute(
                select(Provider).where(Provider.job_id == job_id)
            )
            providers = result.scalars().all()
            
            job.total_providers = len(providers)
            await session.commit()
            
            # Process each provider
            for idx, provider in enumerate(providers):
                try:
                    await self.process_provider(provider, session)
                    job.processed_providers = idx + 1
                    await session.commit()
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Error processing provider {provider.id}: {e}")
                    continue
            
            # Mark job as completed
            job.status = "completed"
            await session.commit()


async def run_validation_job_async(job_id: str):
    """Async wrapper for running validation job"""
    pipeline = ValidationPipeline()
    await pipeline.run_validation_job(job_id)


