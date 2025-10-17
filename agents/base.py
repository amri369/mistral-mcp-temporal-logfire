from typing import Any

from mcp.client.sse import sse_client
from mcp import ClientSession
from mistralai import Mistral, MessageOutputEntry, Agent
import logfire

from models.agents import MistralAgentParams, AgentCreationModel, AgentRunInputModel, MistralAgentUpdateModel
from models.structured_output import get_mistral_response_format, RESPONSE_FORMAT_REGISTRY

from config import settings
from logger import get_logger

logger = get_logger(__name__)

if settings.logfire_token:
    logfire.configure(
        token=settings.logfire_token,
        service_name="mistral-mcp-temporal",
    )
    logfire = logfire.with_settings(custom_scope_suffix='mistral_agents')

async def get_prompt(server_url: str, prompt_name: str) -> str:
    async with sse_client(server_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            logger.info(f"Connected to MCP server: {server_url}")

            prompts = await session.list_prompts()

            available_prompts = [prompt.name for prompt in prompts.prompts]

            logger.info("Available prompts: %s", available_prompts)

            if prompt_name not in available_prompts:
                raise ValueError(f"Prompt {prompt_name} is not available in server '{server_url}'")

            prompt = await session.get_prompt(prompt_name)

            prompt = prompt.messages[0].content.text

            return prompt

def get_client() -> Mistral:
    try:
        return Mistral(api_key=settings.mistral_api_key)
    except Exception as e:
        raise PermissionError("Invalid Mistral API key") from e

async def create_agent_async(params: MistralAgentParams) -> AgentCreationModel:
    instructions = await get_prompt(
        server_url=params.mcp_server_url,
        prompt_name=params.prompt_name
    )
    if not instructions.strip():
        raise ValueError(f"Prompt '{params.prompt_name}' returned empty instructions")

    client = get_client()

    agent = await client.beta.agents.create_async(
        model=params.model,
        name=params.name,
        instructions=instructions,
        description=params.description,
        completion_args={
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
            "response_format": get_mistral_response_format(params.response_format),
        },
        tools=params.tools,
        retries=None # Temporal best practice.
    )
    logger.info(f"Created Mistral agent '{params.name}' (id: {agent.id})")

    return AgentCreationModel(id=agent.id)

async def get_agent_async(params: AgentCreationModel) -> Agent:
    client = get_client()
    agent = await client.beta.agents.get_async(agent_id=params.id)
    return agent

async def start_conversation_async(params: AgentRunInputModel) -> Any:
    client = get_client()
    with logfire.span(
            "Mistral Agents trace: Agent workflow",
            agent_id=params.id,
            _tags=["LLM"],
    ) as span:
        try:
            try:
                agent = await get_agent_async(AgentCreationModel(id=params.id))
            except Exception as e:
                logger.error(f"Failed to fetch agent metadata: {e}")
                raise

            response = await client.beta.conversations.start_async(
                agent_id=params.id,
                inputs=params.inputs,
            )

            outputs = []
            for output in response.outputs:
                if isinstance(output, MessageOutputEntry):
                    outputs.append(output)

            model = outputs[-1].model
            logfire.info(
                f"Responses API with {model}",
                **{
                    'gen_ai.system': 'mistral',
                    'gen_ai.agent.id': params.id,
                    'gen_ai.agent.description': agent.description,
                    'gen_ai.agent.name': agent.name,
                    'gen_ai.system_instructions': agent.instructions,
                    'gen_ai.response.model': model,
                    'gen_ai.usage.input_tokens': response.usage.prompt_tokens,
                    'gen_ai.usage.output_tokens': response.usage.completion_tokens,
                    'gen_ai.conversation.id': response.conversation_id,
                    'gen_ai.input.messages': params.inputs,
                    'gen_ai.output.messages': response.outputs,
                    'gen_ai.output.type': params.response_format
                }
            )

            response = outputs[-1].content
            model_class = RESPONSE_FORMAT_REGISTRY[params.response_format]
            response = model_class.model_validate_json(response)
            return response

        except Exception as e:
            span.record_exception(e)
            raise

async def update_agent_async(params: MistralAgentUpdateModel) -> None:
    client = get_client()
    await client.beta.agents.update_async(agent_id=params.id, handoffs=params.handoffs)
