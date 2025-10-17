from typing import Dict, Literal, List
from pydantic import BaseModel

from .structured_output import ResponseFormatName

MistralTools = Literal[
    "code_interpreter", "document_library", "function",
    "image_generation", "web_search", "web_search_premium"
]

class AgentCreationModel(BaseModel):
    id: str

class AgentRunInputModel(BaseModel):
    id:                 str
    inputs:             str
    response_format:    ResponseFormatName | None = None
    mcp_server_url:     str | None = None

class MistralAgentStaticParams(BaseModel):
    model:              str
    name:               str
    mcp_server_url:     str
    prompt_name:        str
    description:        str | None = None
    temperature:        float = 0.
    max_tokens:         int = 2048
    tools:              List[Dict[str, MistralTools]] | None = None
    response_format:    ResponseFormatName | None = None

class MistralAgentDynamicParams(BaseModel):
    handoffs:           List[str] | None = None

class MistralAgentParams(MistralAgentDynamicParams, MistralAgentStaticParams):
    ...

class QueryModel(BaseModel):
    query: str

class WorkflowIDModel(BaseModel):
    workflow_id: str
