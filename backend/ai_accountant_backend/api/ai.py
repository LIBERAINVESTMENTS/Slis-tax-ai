"""AI agent chat endpoints — master coordinator + specialist agents."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ai_accountant_backend.agents.master import MasterAgent
from ai_accountant_backend.agents.service import register_all
from ai_accountant_backend.agents.registry import get_agent
from ai_accountant_backend.db import get_db
from ai_accountant_backend.deps import get_current_user
from ai_accountant_backend.llm.router import route_chat

# Ensure agents are registered
register_all()

router = APIRouter(tags=["ai"])


class ChatRequest(BaseModel):
    message: str
    agent: str | None = None  # master | accountant | tax | cfo | personal_finance | document | audit


class ChatResponse(BaseModel):
    text: str
    agent: str
    model: str
    provider: str
    requires_approval: bool = False


@router.get("/ai/agents")
def list_agents():
    from ai_accountant_backend.agents.registry import all_agents
    return {"agents": [{"name": a.name, "role": a.role} for a in all_agents()]}


@router.post("/ai/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    agent_type = payload.agent or "master"
    if agent_type == "master":
        agent = MasterAgent()
    else:
        agent = get_agent(agent_type)
        if agent is None:
            raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_type}")
    context = {
        "tenant_id": user.tenant_id,
        "user_id": user.id,
        "company_id": None,
    }
    result = await agent.run(message=payload.message, context=context)
    # Track the LLM usage via router (uses the agent's preferred tier)
    tier = "heavy" if agent.name in ("cfo", "tax") else "light"
    try:
        await route_chat(
            db,
            tenant_id=user.tenant_id,
            tier=tier,
            messages=[{"role": "user", "content": payload.message}],
            user_id=user.id,
            agent=agent.name,
        )
    except Exception:
        # Cost tracking must never break the chat response
        pass
    return ChatResponse(
        text=result.text,
        agent=result.agent,
        model=result.model,
        provider=result.provider,
        requires_approval=result.requires_approval,
    )

