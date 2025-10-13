from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    logfire_token:          str | None = Field(None, alias="LOGFIRE_TOKEN")
    mcp_server_url:         str | None = Field(..., alias="MCP_SERVER_URL")
    mistral_api_key:        str | None = Field(None, alias="MISTRAL_API_KEY")
    temporal_server_url:    str | None = Field(..., alias="TEMPORAL_SERVER_URL")

settings = Settings()
