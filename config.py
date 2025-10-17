from dotenv import load_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    logfire_token:          str | None = Field(None, alias="LOGFIRE_TOKEN")
    mcp_server_url:         str | None = Field(..., alias="MCP_SERVER_URL")
    mistral_api_key:        str | None = Field(None, alias="MISTRAL_API_KEY")
    temporal_server_url:    str | None = Field(..., alias="TEMPORAL_SERVER_URL")
    task_queue_url:         str | None = Field("financial-research-task-queue", alias="TASK_QUEUE_URL")

    @computed_field
    @property
    def financials_mcp_url(self) -> str:
        return f"{self.mcp_server_url}/financials/sse"

    @computed_field
    @property
    def prices_mcp_url(self) -> str:
        return f"{self.mcp_server_url}/prices/sse"

settings = Settings()
