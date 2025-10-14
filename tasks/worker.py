import asyncio

import logfire
from temporalio.client import Client
from temporalio.worker import Worker

from config import settings
from tasks.activities.financial_agents import (
    create_agent_activity,
    update_agent_activity,
    start_conversation_activity,
)
from tasks.workflows.financial_agents import FinancialResearchWorkflow
from logger import get_logger
logger = get_logger(__name__)

if settings.logfire_token:
    logfire.configure(token=settings.logfire_token)

async def main():
    client = await Client.connect(
        settings.temporal_server_url,
    )

    worker = Worker(
        client,
        task_queue="financial-research-task-queue",
        workflows=[FinancialResearchWorkflow],
        activities=[
            create_agent_activity,
            update_agent_activity,
            start_conversation_activity,
        ],
    )

    logger.info("Starting financial research worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
