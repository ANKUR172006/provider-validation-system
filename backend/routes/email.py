"""
Email template routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from database.models import Provider
from models.schemas import EmailTemplateRequest, EmailTemplateResponse
from jinja2 import Template

router = APIRouter()


@router.post("/template", response_model=EmailTemplateResponse)
async def generate_email_template(
    request: EmailTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate email template for provider"""
    result = await db.execute(
        select(Provider).where(Provider.id == request.provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Generate email based on template type
    if request.template_type == "review_request":
        subject = f"Review Required: Provider Data Validation - {provider.name}"
        body_template = Template("""
Dear Team,

A provider record requires manual review:

Provider Information:
- Name: {{ provider.name }}
- NPI: {{ provider.npi or 'Not provided' }}
- Specialty: {{ provider.specialty or 'Not provided' }}
- Phone: {{ provider.phone or 'Not provided' }}
- Address: {{ provider.address or 'Not provided' }}

Validation Results:
- Overall Confidence: {{ "%.1f"|format(provider.confidence_overall * 100) }}%
- Needs Review: {{ 'Yes' if provider.needs_review else 'No' }}
- Suspicious: {{ 'Yes' if provider.is_suspicious else 'No' }}

Issues Identified:
{% for issue in provider.issues %}
- {{ issue }}
{% endfor %}

Validation Notes:
{{ provider.validation_notes or 'None' }}

Please review and take appropriate action.

Best regards,
Provider Validation System
        """)
    elif request.template_type == "issue_notification":
        subject = f"Issues Detected: {provider.name}"
        body_template = Template("""
Dear Team,

Issues have been detected with the following provider:

Provider: {{ provider.name }}
NPI: {{ provider.npi or 'Not provided' }}

Issues:
{% for issue in provider.issues %}
- {{ issue }}
{% endfor %}

Please investigate and resolve.

Best regards,
Provider Validation System
        """)
    else:
        subject = f"Provider Validation: {provider.name}"
        body_template = Template("""
Dear Team,

Provider validation completed:

Provider: {{ provider.name }}
Status: {{ 'Validated' if provider.is_validated else 'Needs Review' }}
Confidence: {{ "%.1f"|format(provider.confidence_overall * 100) }}%

Best regards,
Provider Validation System
        """)
    
    body = body_template.render(provider=provider)
    issues = provider.issues if provider.issues else []
    
    return EmailTemplateResponse(
        provider_id=provider.id,
        provider_name=provider.name,
        subject=subject,
        body=body,
        issues=issues
    )


