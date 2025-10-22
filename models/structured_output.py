from typing import Any, Dict, Literal, List
from pydantic import BaseModel

class AnalysisSummary(BaseModel):
    summary: str
    """Short text summary for this aspect of the analysis."""

class FinancialSearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""

    query: str
    """The search term to feed into a web (or file) search."""

class FinancialSearchPlan(BaseModel):
    searches: list[FinancialSearchItem]
    """A list of searches to perform."""

class VerificationResult(BaseModel):
    verified: bool
    """Whether the report seems coherent and plausible."""

    issues: str
    """If not verified, describe the main issues or concerns."""

class FinancialReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence executive summary highlighting key insights across price, fundamental, and risk analysis."""

    markdown_report: str
    """The full markdown report synthesizing prices, fundamentals, and risk analyses."""

    follow_up_questions: list[str]
    """Suggested follow-up questions for further research."""

    key_metrics: dict[str, Any] | None = None
    """Key metrics extracted from all agents (e.g., current_price, pe_ratio, volatility, risk_score)."""

RESPONSE_FORMAT_REGISTRY = {
    "AnalysisSummary": AnalysisSummary,
    "FinancialSearchPlan": FinancialSearchPlan,
    "VerificationResult": VerificationResult,
    "FinancialReportData": FinancialReportData,
}

ResponseFormatName = Literal[*tuple(RESPONSE_FORMAT_REGISTRY.keys())]

class WriterAgentInputModel(BaseModel):
    """Input for Writer Agent to synthesize prices, fundamentals, and risk analyses into a final report."""

    prices_analysis: AnalysisSummary
    """Price history, technical indicators, trading patterns, and market trends."""

    fundamentals_analysis: AnalysisSummary
    """Financial health, revenue trends, valuation metrics, and market position analysis."""

    risk_analysis: AnalysisSummary
    """Risk assessment, volatility metrics, factor exposures, and mitigation factors."""

def _add_additional_properties_false(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively add additionalProperties: False to all objects in schema."""
    if isinstance(schema_dict, dict):
        if schema_dict.get("type") == "object":
            schema_dict["additionalProperties"] = False
        for value in schema_dict.values():
            if isinstance(value, dict):
                _add_additional_properties_false(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        _add_additional_properties_false(item)
    return schema_dict

def get_mistral_response_format(format_name: ResponseFormatName) -> Dict[str, Any]:
    model_class = RESPONSE_FORMAT_REGISTRY[format_name]
    schema = model_class.model_json_schema()
    schema = _add_additional_properties_false(schema)

    return {
        "type": "json_schema",
        "json_schema": {
            "name": format_name,
            "schema": schema,
            "strict": True
        }
    }

class FinancialReportWorkflowOutput(BaseModel):
    search_plan: FinancialSearchPlan
    report: FinancialReportData
    verification: VerificationResult
    risk_analysis: AnalysisSummary
    fundamentals_analysis: AnalysisSummary
    price_analysis: AnalysisSummary
    search_results: List[AnalysisSummary]

def format_search_results(results: List[AnalysisSummary]) -> str:
    """Format search results as clean, readable text for the agent."""
    formatted = "# Analysis Results\n\n"
    for i, result in enumerate(results, 1):
        formatted += f"## Finding {i}\n{result.summary}\n\n"
    return formatted.strip()
