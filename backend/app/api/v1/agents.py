from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.agents.orchestrator import orchestrator
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_city_agents(
    req: AgentChatRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Multi-Agent conversational interface:
    The AI Orchestrator classifies user intent, delegates work to specialized agents
    (City, Planning, Search, RAG, Map, Recommendation), and provides transparent execution logs.
    """
    return await orchestrator.handle_message(db, req)
