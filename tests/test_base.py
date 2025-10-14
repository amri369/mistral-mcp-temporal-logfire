import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from mistralai import Mistral, MessageOutputEntry

from agents.base import (
 get_prompt,
 get_client,
 create_agent_async,
 start_conversation_async,
 update_agent_async,
)
from models.agents import (
 MistralAgentParams,
 AgentRunInputModel,
 MistralAgentUpdateModel,
)
from models.structured_output import AnalysisSummary


@pytest.fixture
def mock_mcp_session():
 """Mock MCP ClientSession"""
 session = AsyncMock()
 session.initialize = AsyncMock()
 session.list_prompts = AsyncMock()
 session.get_prompt = AsyncMock()
 return session


@pytest.fixture
def mock_mistral_client():
 """Mock Mistral client"""
 client = Mock(spec=Mistral)
 client.beta = Mock()
 client.beta.agents = Mock()
 client.beta.conversations = Mock()
 return client


@pytest.fixture
def sample_agent_params():
 """Sample agent creation params"""
 return MistralAgentParams(
 model="mistral-medium-2505",
 name="test-agent",
 mcp_server_url="http://localhost:8000",
 prompt_name="financial_analysis",
 description="Test agent",
 response_format="AnalysisSummary",
 temperature=0.7,
 max_tokens=1000,
 tools=[{"type": "web_search"}],
 )


@pytest.fixture
def sample_run_input():
 """Sample agent run input"""
 return AgentRunInputModel(
 id="ag_123",
 inputs='{"query": "test query"}',
 response_format="AnalysisSummary",
 )


@pytest.fixture
def mock_conversation_response():
 """Mock Mistral conversation response"""
 response = Mock()
 response.conversation_id = "conv_123"
 response.usage = Mock()
 response.usage.prompt_tokens = 100
 response.usage.completion_tokens = 200
 response.usage.total_tokens = 300
 response.usage.connector_tokens = 50
 response.usage.connectors = {"web_search": 1}

 output = Mock(spec=MessageOutputEntry)
 output.content = '{"summary": "test summary"}'
 output.model = "mistral-medium-2505"

 response.outputs = [output]
 return response


# Test get_prompt
@pytest.mark.asyncio
async def test_get_prompt_success(mock_mcp_session):
 """Test successful prompt retrieval from MCP server"""
 # Setup
 mock_prompts = Mock()
 mock_prompts.prompts = [
 Mock(name="financial_analysis"),
 Mock(name="market_research"),
 ]
 mock_mcp_session.list_prompts.return_value = mock_prompts

 mock_prompt = Mock()
 mock_prompt.messages = [
 Mock(content=Mock(text="You are a financial analyst"))
 ]
 mock_mcp_session.get_prompt.return_value = mock_prompt

 with patch("agents.base.streamablehttp_client") as mock_http:
 mock_http.return_value.__aenter__.return_value = (
 AsyncMock(), AsyncMock(), lambda: "session_123"
 )

 with patch("agents.base.ClientSession") as mock_session_class:
 mock_session_class.return_value.__aenter__.return_value = mock_mcp_session

 # Execute
 result = await get_prompt(
 "http://localhost:8000",
 "financial_analysis"
 )

 # Assert
 assert result == "You are a financial analyst"
 mock_mcp_session.get_prompt.assert_called_once_with("financial_analysis")


@pytest.mark.asyncio
async def test_get_prompt_not_found(mock_mcp_session):
 """Test prompt not found in MCP server"""
 mock_prompts = Mock()
 mock_prompts.prompts = [Mock(name="other_prompt")]
 mock_mcp_session.list_prompts.return_value = mock_prompts

 with patch("agents.base.streamablehttp_client") as mock_http:
 mock_http.return_value.__aenter__.return_value = (
 AsyncMock(), AsyncMock(), lambda: "session_123"
 )

 with patch("agents.base.ClientSession") as mock_session_class:
 mock_session_class.return_value.__aenter__.return_value = mock_mcp_session

 # Execute & Assert
 with pytest.raises(ValueError, match="Prompt financial_analysis is not available"):
 await get_prompt("http://localhost:8000", "financial_analysis")


# Test get_client
@patch("agents.base.settings")
def test_get_client_success(mock_settings):
 """Test Mistral client initialization"""
 mock_settings.mistral_api_key = "test_key"

 with patch("agents.base.Mistral") as mock_mistral:
 client = get_client()
 mock_mistral.assert_called_once_with(api_key="test_key")
 assert client is not None


@patch("agents.base.settings")
def test_get_client_invalid_key(mock_settings):
 """Test client initialization with invalid key"""
 mock_settings.mistral_api_key = "invalid"

 with patch("agents.base.Mistral", side_effect=Exception("Invalid API key")):
 with pytest.raises(PermissionError, match="Invalid Mistral API key"):
 get_client()


# Test create_agent_async
@pytest.mark.asyncio
async def test_create_agent_success(sample_agent_params, mock_mistral_client):
 """Test successful agent creation"""
 mock_agent = Mock()
 mock_agent.id = "ag_123"
 mock_mistral_client.beta.agents.create_async = AsyncMock(return_value=mock_agent)

 with patch("agents.base.get_prompt", return_value="Test instructions"):
 with patch("agents.base.get_client", return_value=mock_mistral_client):
 result = await create_agent_async(sample_agent_params)

 assert result.id == "ag_123"
 mock_mistral_client.beta.agents.create_async.assert_called_once()


@pytest.mark.asyncio
async def test_create_agent_empty_prompt(sample_agent_params, mock_mistral_client):
 """Test agent creation with empty prompt fails"""
 with patch("agents.base.get_prompt", return_value=" "):
 with patch("agents.base.get_client", return_value=mock_mistral_client):
 with pytest.raises(ValueError, match="returned empty instructions"):
 await create_agent_async(sample_agent_params)


# Test start_conversation_async (MOST CRITICAL)
@pytest.mark.asyncio
async def test_start_conversation_success(
 sample_run_input,
 mock_mistral_client,
 mock_conversation_response,
):
 """Test successful conversation execution"""
 mock_mistral_client.beta.conversations.start_async = AsyncMock(
 return_value=mock_conversation_response
 )

 with patch("agents.base.get_client", return_value=mock_mistral_client):
 with patch("agents.base.logfire"):
 result = await start_conversation_async(sample_run_input)

 assert isinstance(result, AnalysisSummary)
 assert result.summary == "test summary"
 mock_mistral_client.beta.conversations.start_async.assert_called_once()


@pytest.mark.asyncio
async def test_start_conversation_logfire_tracking(
 sample_run_input,
 mock_mistral_client,
 mock_conversation_response,
):
 """Test Logfire observability is called"""
 mock_mistral_client.beta.conversations.start_async = AsyncMock(
 return_value=mock_conversation_response
 )

 with patch("agents.base.get_client", return_value=mock_mistral_client):
 with patch("agents.base.logfire") as mock_logfire:
 await start_conversation_async(sample_run_input)

 # Verify logfire.info was called with correct attributes
 mock_logfire.info.assert_called_once()
 call_kwargs = mock_logfire.info.call_args[1]
 assert call_kwargs["gen_ai.system"] == "mistral"
 assert call_kwargs["gen_ai.usage.input_tokens"] == 100
 assert call_kwargs["gen_ai.usage.output_tokens"] == 200


@pytest.mark.asyncio
async def test_start_conversation_exception_handling(
 sample_run_input,
 mock_mistral_client,
):
 """Test exception handling and Logfire span recording"""
 mock_mistral_client.beta.conversations.start_async = AsyncMock(
 side_effect=Exception("API Error")
 )

 with patch("agents.base.get_client", return_value=mock_mistral_client):
 with patch("agents.base.logfire") as mock_logfire:
 mock_span = MagicMock()
 mock_logfire.span.return_value.__enter__.return_value = mock_span

 with pytest.raises(Exception, match="API Error"):
 await start_conversation_async(sample_run_input)

 # Verify exception was recorded
 mock_span.record_exception.assert_called_once()


@pytest.mark.asyncio
async def test_start_conversation_invalid_json_response(
 sample_run_input,
 mock_mistral_client,
 mock_conversation_response,
):
 """Test handling of invalid JSON in response"""
 mock_conversation_response.outputs[0].content = "invalid json"
 mock_mistral_client.beta.conversations.start_async = AsyncMock(
 return_value=mock_conversation_response
 )

 with patch("agents.base.get_client", return_value=mock_mistral_client):
 with patch("agents.base.logfire"):
 with pytest.raises(Exception): # Pydantic validation error
 await start_conversation_async(sample_run_input)


# Test update_agent_async
@pytest.mark.asyncio
async def test_update_agent_success(mock_mistral_client):
 """Test successful agent update"""
 params = MistralAgentUpdateModel(
 id="ag_123",
 handoffs=[{"name": "escalation_agent"}]
 )

 mock_mistral_client.beta.agents.update_async = AsyncMock()

 with patch("agents.base.get_client", return_value=mock_mistral_client):
 await update_agent_async(params)

 mock_mistral_client.beta.agents.update_async.assert_called_once_with(
 agent_id="ag_123",
 handoffs=[{"name": "escalation_agent"}]
 )