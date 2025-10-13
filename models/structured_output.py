from typing import Any, Dict, Literal, List
from pydantic import BaseModel

class AnalysisSummary(BaseModel):
    summary: str
    """Short text summary for this aspect of the analysis."""

class VerificationResult(BaseModel):
    verified: bool
    """Whether the report seems coherent and plausible."""

    issues: str
    """If not verified, describe the main issues or concerns."""

RESPONSE_FORMAT_REGISTRY = {
    "AnalysisSummary": AnalysisSummary,
    "VerificationResult": VerificationResult,
}

ResponseFormatName = Literal[*tuple(RESPONSE_FORMAT_REGISTRY.keys())]

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
