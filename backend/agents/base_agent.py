"""
Base agent class for all AI agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession


class BaseAgent(ABC):
    """Base class for all agentic AI agents"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def process(self, provider_data: Dict[str, Any], session: AsyncSession) -> Dict[str, Any]:
        """
        Process provider data
        
        Args:
            provider_data: Provider data dictionary
            session: Database session
        
        Returns:
            Updated provider data with agent results
        """
        pass
    
    async def log_action(
        self,
        session: AsyncSession,
        job_id: str,
        provider_id: int,
        action: str,
        result: Dict[str, Any]
    ):
        """Log agent action to database"""
        from database.models import ValidationLog
        
        log = ValidationLog(
            job_id=job_id,
            provider_id=provider_id,
            agent_name=self.name,
            action=action,
            result=result
        )
        session.add(log)
        await session.flush()


