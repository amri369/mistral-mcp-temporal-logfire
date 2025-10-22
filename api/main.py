from contextlib import asynccontextmanager

from fastapi import FastAPI
import logfire

from tasks.utils.common import get_temporal_client
from api.agents import router as agents_router
from config import settings
from logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    _app.state.temporal_client = await get_temporal_client()
    try:
        yield
    finally:
        pass
app = FastAPI(
    title="API to Manage Agents Workflows",
    lifespan=lifespan,
)
app.include_router(agents_router, prefix="/agents", tags=["Mistral Agents"])

if settings.logfire_token:
    logfire.configure(
        token=settings.logfire_token,
        service_name="mistral-mcp-temporal",
    )
    logfire.instrument_fastapi(app=app)
