from config import settings
from models.agents import MistralAgentParams

MODEL = "mistral-medium-2505"
financials_mcp_url = settings.financials_mcp_url
prices_mcp_url = settings.prices_mcp_url

AGENTS_PARAMS = {
    "PLANNER": MistralAgentParams(
        model=MODEL,
        name="FinancialPlannerAgent",
        description="Agent to plan searches",
        mcp_server_url=financials_mcp_url,
        prompt_name="planner_prompt",
        response_format="FinancialSearchPlan",
        temperature=0.3,
    ),

    "SEARCH": MistralAgentParams(
        model=MODEL,
        name="FinancialSearchAgent",
        description="Agent to perform web searches",
        mcp_server_url=financials_mcp_url,
        prompt_name="search_prompt",
        response_format="AnalysisSummary",
        temperature=0.1,
        tools=[{"type": "web_search"}],
    ),

    "FUNDAMENTALS": MistralAgentParams(
        model=MODEL,
        name="FundamentalsAnalystAgent",
        description="Agent to analyze company fundamentals",
        mcp_server_url=financials_mcp_url,
        prompt_name="financials_prompt",
        response_format="AnalysisSummary",
    ),

    "RISK": MistralAgentParams(
        model=MODEL,
        name="RiskAnalystAgent",
        description="Agent to analyze risks",
        mcp_server_url=financials_mcp_url,
        prompt_name="risk_prompt",
        response_format="AnalysisSummary",
        temperature=0.1,
    ),

    "VERIFIER": MistralAgentParams(
        model=MODEL,
        name="VerificationAgent",
        description="Agent to verify facts",
        mcp_server_url=financials_mcp_url,
        prompt_name="verifier_prompt",
        response_format="VerificationResult",
    ),

    "WRITER": MistralAgentParams(
        model=MODEL,
        name="FinancialWriterAgent",
        description="Agent to write reports",
        mcp_server_url=financials_mcp_url,
        prompt_name="writer_prompt",
        response_format="FinancialReportData",
        temperature=0.,
    ),

    "ANALYST": MistralAgentParams(
        model="mistral-medium-latest",
        name="price-analyst-agent",
        description="Analyzes stock prices using real-time data",
        mcp_server_url=prices_mcp_url,
        prompt_name="price_analyst_prompt",
        temperature=0.7,
        max_tokens=1000,
        response_format="AnalysisSummary",
    ),
}
