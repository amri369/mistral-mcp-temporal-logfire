import pytest
from pydantic import ValidationError
from models.structured_output import (
    AnalysisSummary,
    FinancialSearchItem,
    FinancialSearchPlan,
    VerificationResult,
    FinancialReportData,
    FinancialReportWorkflowOutput,
    RESPONSE_FORMAT_REGISTRY,
    _add_additional_properties_false,
    get_mistral_response_format,
)

# Test AnalysisSummary
def test_analysis_summary_valid():
    summary = AnalysisSummary(summary="This is a test summary")
    assert summary.summary == "This is a test summary"

def test_analysis_summary_missing_field():
    with pytest.raises(ValidationError):
        AnalysisSummary()

# Test FinancialSearchItem
def test_financial_search_item_valid():
    item = FinancialSearchItem(
        reason="Testing search relevance",
        query="test query"
    )
    assert item.reason == "Testing search relevance"
    assert item.query == "test query"

def test_financial_search_item_missing_fields():
    with pytest.raises(ValidationError):
        FinancialSearchItem(reason="Only reason")

# Test FinancialSearchPlan
def test_financial_search_plan_valid():
    plan = FinancialSearchPlan(
        searches=[
            FinancialSearchItem(reason="Reason 1", query="Query 1"),
            FinancialSearchItem(reason="Reason 2", query="Query 2"),
        ]
    )
    assert len(plan.searches) == 2
    assert plan.searches[0].query == "Query 1"

def test_financial_search_plan_empty_list():
    plan = FinancialSearchPlan(searches=[])
    assert plan.searches == []

# Test VerificationResult
def test_verification_result_verified():
    result = VerificationResult(verified=True, issues="No issues")
    assert result.verified is True
    assert result.issues == "No issues"

def test_verification_result_not_verified():
    result = VerificationResult(verified=False, issues="Missing data")
    assert result.verified is False
    assert result.issues == "Missing data"

# Test FinancialReportData
def test_financial_report_data_valid():
    report = FinancialReportData(
        short_summary="Executive summary",
        markdown_report="# Full Report\n\nContent here",
        follow_up_questions=["Question 1", "Question 2"]
    )
    assert report.short_summary == "Executive summary"
    assert "# Full Report" in report.markdown_report
    assert len(report.follow_up_questions) == 2

def test_financial_report_data_empty_follow_up():
    report = FinancialReportData(
        short_summary="Summary",
        markdown_report="Report",
        follow_up_questions=[]
    )
    assert report.follow_up_questions == []

# Test FinancialReportWorkflowOutput
def test_workflow_output_valid():
    output = FinancialReportWorkflowOutput(
        search_plan=FinancialSearchPlan(searches=[]),
        report=FinancialReportData(
            short_summary="Summary",
            markdown_report="Report",
            follow_up_questions=[]
        ),
        verification=VerificationResult(verified=True, issues="None"),
        risk_analysis=AnalysisSummary(summary="Risk Analysis"),
        fundamentals_analysis=AnalysisSummary(summary="Fundamentals Analysis"),
        price_analysis=AnalysisSummary(summary="Price Analysis"),
    )
    assert output.verification.verified is True
    assert len(output.search_plan.searches) == 0

# Test RESPONSE_FORMAT_REGISTRY
def test_response_format_registry_keys():
    expected_keys = {
        "AnalysisSummary",
        "FinancialSearchPlan",
        "VerificationResult",
        "FinancialReportData"
    }
    assert set(RESPONSE_FORMAT_REGISTRY.keys()) == expected_keys

def test_response_format_registry_values():
    assert RESPONSE_FORMAT_REGISTRY["AnalysisSummary"] == AnalysisSummary
    assert RESPONSE_FORMAT_REGISTRY["FinancialSearchPlan"] == FinancialSearchPlan
    assert RESPONSE_FORMAT_REGISTRY["VerificationResult"] == VerificationResult
    assert RESPONSE_FORMAT_REGISTRY["FinancialReportData"] == FinancialReportData

# Test _add_additional_properties_false
def test_add_additional_properties_simple_object():
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    result = _add_additional_properties_false(schema)
    assert result["additionalProperties"] is False

def test_add_additional_properties_nested_object():
    schema = {
        "type": "object",
        "properties": {
            "nested": {
                "type": "object",
                "properties": {"value": {"type": "string"}}
            }
        }
    }
    result = _add_additional_properties_false(schema)
    assert result["additionalProperties"] is False
    assert result["properties"]["nested"]["additionalProperties"] is False

def test_add_additional_properties_with_array():
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}}
                }
            }
        }
    }
    result = _add_additional_properties_false(schema)
    assert result["additionalProperties"] is False
    assert result["properties"]["items"]["items"]["additionalProperties"] is False

def test_add_additional_properties_non_object():
    schema = {"type": "string"}
    result = _add_additional_properties_false(schema)
    assert "additionalProperties" not in result

# Test get_mistral_response_format
def test_get_mistral_response_format_analysis_summary():
    result = get_mistral_response_format("AnalysisSummary")

    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "AnalysisSummary"
    assert result["json_schema"]["strict"] is True
    assert "schema" in result["json_schema"]
    assert result["json_schema"]["schema"]["additionalProperties"] is False

def test_get_mistral_response_format_financial_search_plan():
    result = get_mistral_response_format("FinancialSearchPlan")

    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "FinancialSearchPlan"
    assert result["json_schema"]["strict"] is True

    schema = result["json_schema"]["schema"]
    assert schema["additionalProperties"] is False
    assert "searches" in schema["properties"]

def test_get_mistral_response_format_verification_result():
    result = get_mistral_response_format("VerificationResult")

    schema = result["json_schema"]["schema"]
    assert "verified" in schema["properties"]
    assert "issues" in schema["properties"]
    assert schema["additionalProperties"] is False

def test_get_mistral_response_format_financial_report_data():
    result = get_mistral_response_format("FinancialReportData")

    schema = result["json_schema"]["schema"]
    assert "short_summary" in schema["properties"]
    assert "markdown_report" in schema["properties"]
    assert "follow_up_questions" in schema["properties"]
    assert schema["additionalProperties"] is False

def test_get_mistral_response_format_invalid_name():
    with pytest.raises(KeyError):
        get_mistral_response_format("InvalidFormat")

# Integration test
def test_mistral_format_has_all_recursive_additional_properties():
    result = get_mistral_response_format("FinancialSearchPlan")
    schema = result["json_schema"]["schema"]

    # Check root level
    assert schema["additionalProperties"] is False

    # Check nested objects in $defs (Pydantic uses references)
    if "$defs" in schema:
        for def_name, def_schema in schema["$defs"].items():
            if def_schema.get("type") == "object":
                assert def_schema["additionalProperties"] is False, f"{def_name} missing additionalProperties"
