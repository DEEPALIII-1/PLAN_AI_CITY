from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AgentChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str

class AgentChatRequest(BaseModel):
    message: str
    city_id: Optional[int] = None
    conversation_history: List[AgentChatMessage] = []
    user_context: Optional[Dict[str, Any]] = None

class AgentStepLog(BaseModel):
    agent_name: str
    action_taken: str
    summary_output: str
    confidence: float

class AgentChatResponse(BaseModel):
    reply: str
    intent_detected: str
    agents_involved: List[str]
    agent_steps: List[AgentStepLog] = []
    citations: List[Dict[str, Any]] = []
    suggested_places: List[Dict[str, Any]] = []
    suggested_actions: List[str] = []
