from fastapi import FastAPI

from mcp_server.financial_research_server import mcp as mcp_server

app = FastAPI()
app.mount("/financials", mcp_server.sse_app())
