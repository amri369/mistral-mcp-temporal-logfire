from pydantic import BaseModel

from mistralai import SDKError
from temporalio import activity

from models.agents import MistralAgentParams, AgentCreationModel, AgentRunInputModel
from agents.base import create_agent_async, start_conversation_async
from tasks.retry_llm_call import http_response_to_application_error

@activity.defn
async def create_agent_activity(params: MistralAgentParams) -> AgentCreationModel:
    try:
        agent = await create_agent_async(params)
        return agent
    except SDKError as e:
        raise http_response_to_application_error(e.raw_response)

@activity.defn
async def start_conversation_activity(params: AgentRunInputModel) -> BaseModel:
    try:
        response = await start_conversation_async(params)
        return response
    except SDKError as e:
        raise http_response_to_application_error(e.raw_response)
