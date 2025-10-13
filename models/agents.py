from typing import Literal, List
from pydantic import BaseModel

from .structured_output import ResponseFormatName

MistralTools = Literal[
    "code_interpreter", "document_library", "function",
    "image_generation", "web_search", "web_search_premium"
]

class AgentCreationModel(BaseModel):
    id: str

class AgentRunInputModel(BaseModel):
    id: str
    inputs: str
    response_format: ResponseFormatName | None = None

class MistralAgentParams(BaseModel):
    model:              str
    name:               str
    mcp_server_url:     str
    prompt_name:        str
    description:        str | None = None
    temperature:        float = 0.
    max_tokens:         int = 2048
    tools:              List[MistralTools] | None = None
    response_format:    ResponseFormatName | None = None
