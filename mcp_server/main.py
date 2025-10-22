from fastapi import FastAPI

import logfire

from config import settings

if settings.logfire_token:
    logfire.configure(token=settings.logfire_token, service_name='server')
    logfire.instrument_mcp()

from mcp_server.financial_research_server import mcp as mcp_financial_server
from mcp_server.prices_analysis_server import mcp as prices_server

app = FastAPI()
app.mount("/financials", mcp_financial_server.sse_app())
app.mount("/prices", prices_server.sse_app())
