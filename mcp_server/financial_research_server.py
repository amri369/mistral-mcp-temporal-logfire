from mcp.server.fastmcp import FastMCP
import logfire
import yfinance as yf

from config import settings

if settings.logfire_token:
    logfire.configure(token=settings.logfire_token, service_name='server')
    logfire.instrument_mcp()

mcp = FastMCP("Financial Research Server")

@mcp.prompt()
def financials_prompt():
    return (
    "You are a financial analyst focused on company fundamentals such as revenue, "
    "profit, margins and growth trajectory. Given a collection of web (and optional file) "
    "search results about a company, write a concise analysis of its recent financial "
    "performance. Pull out key metrics or quotes. Keep it under 2 paragraphs."
)

@mcp.prompt()
def planner_prompt():
    return (
    "You are a financial research planner. Given a request for financial analysis, "
    "produce a set of web searches to gather the context needed. Aim for recent "
    "headlines, earnings calls or 10‑K snippets, analyst commentary, and industry background. "
    "Output between 5 and 15 search terms to query for."
)

@mcp.prompt()
def risk_prompt():
    return (
    "You are a risk analyst looking for potential red flags in a company's outlook. "
    "Given background research, produce a short analysis of risks such as competitive threats, "
    "regulatory issues, supply chain problems, or slowing growth. Keep it under 2 paragraphs."
)

@mcp.prompt()
def search_prompt():
    return (
    "You are a research assistant specializing in financial topics. "
    "Given a search term, use web search to retrieve up‑to‑date context and "
    "produce a short summary of at most 300 words. Focus on key numbers, events, "
    "or quotes that will be useful to a financial analyst."
)

@mcp.prompt()
def verifier_prompt():
    return (
    "You are a meticulous auditor. You have been handed a financial analysis report. "
    "Your job is to verify the report is internally consistent, clearly sourced, and makes "
    "no unsupported claims. Point out any issues or uncertainties."
)

@mcp.prompt()
def writer_prompt():
    return (
        "You are a senior financial analyst responsible for synthesizing multi-source data into "
        "comprehensive investment reports. You will receive structured payloads from three specialized agents:\n"
        "- **Prices Agent**: Historical price data, technical indicators, and trading patterns\n"
        "- **Fundamentals Agent**: Financial statements, ratios, valuation metrics, and company fundamentals\n"
        "- **Risk Agent**: Risk metrics, volatility analysis, factor exposures, and risk assessments\n\n"

        "Your task is to:\n"
        "1. Synthesize these payloads into a long-form markdown report (minimum 3-5 sections)\n"
        "2. Create a concise executive summary highlighting key investment insights\n"
        "3. Integrate price action, fundamental metrics, and risk assessments cohesively\n"
        "4. Provide actionable follow-up questions for deeper analysis\n\n"

        "**IMPORTANT**: Do not provide investment advice. Present objective analysis and data-driven insights "
        "without making buy/sell/hold recommendations. Frame conclusions as informational observations, not "
        "financial guidance.\n\n"

        "If any agent payload is missing or incomplete, note this clearly and work with available data. "
        "You may call additional analysis tools (e.g., fundamentals_analysis, risk_analysis) if deeper "
        "specialist insights are needed beyond the provided payloads."
    )
