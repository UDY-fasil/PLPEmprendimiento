"""Schemas del asistente virtual."""
from typing import List, Optional

from pydantic import BaseModel, Field


class AssistantAction(BaseModel):
    label: str
    type: str  # public_tab | admin_view | open_form | auth | panel
    target: Optional[str] = None


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    context: Optional[str] = Field(default="public", max_length=50)


class AssistantChatResponse(BaseModel):
    reply: str
    actions: List[AssistantAction] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
