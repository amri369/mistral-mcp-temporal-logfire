from fastapi import FastAPI

import logfire

from mcp_server.financial_research_server import mcp as mcp_financial_server
from mcp_server.prices_analysis_server import mcp as prices_server
from config import settings
from logger import get_logger

logger = get_logger(__name__)

try:
    logfire.configure(token=settings.logfire_token, service_name='server')
    logfire.instrument_mcp()
except Exception as e:
    logger.warning(e)

app = FastAPI()
app.mount("/financials", mcp_financial_server.sse_app())
app.mount("/prices", prices_server.sse_app())
